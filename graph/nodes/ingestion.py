import os
from dotenv import load_dotenv
load_dotenv()
from langchain_elasticsearch import ElasticsearchStore
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from uuid import uuid4
from langchain_core.documents import Document
from typing import List
from elasticsearch import Elasticsearch
import mysql.connector
from mysql.connector import Error


ES_CLOUD_ID = os.getenv('ES_CLOUD_ID')
ES_INDEX = os.getenv('ES_INDEX')
ES_API_KEY = os.getenv('ES_API_KEY')
ES_INDEX_RELEVANCE = os.getenv('ES_INDEX_RELEVANCE')
host = os.getenv("MYSQL_HOST")
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
database = os.getenv("MYSQL_DATABASE")

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

vector_store = ElasticsearchStore(
    es_cloud_id=ES_CLOUD_ID,
    index_name=ES_INDEX,
    embedding=embeddings,
    es_api_key=ES_API_KEY,
)

research_index = Elasticsearch(
    cloud_id=ES_CLOUD_ID,
    #index_name=ES_INDEX_RELEVANCE,
    #embedding=embeddings,
    api_key=ES_API_KEY,
)

try:
    # Establish a connection to the MySQL database
    connection = mysql.connector.connect(
        host="host.docker.internal",
        user=user,
        password=password,
        database=database,
        # use_pure=True
    )
except Error as e:
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        # use_pure=True
    )
    

def extract_packagename_datasetname(field_name: str):
    parts = field_name.split(".")
    return parts[0], parts[1]

def get_es_retriever(field_name: str):
    return vector_store.as_retriever(
        search_type="similarity_score_threshold", 
        search_kwargs={
            "score_threshold": 0.2,
            "filter": {
                'term': {
                    'metadata.source.keyword': field_name
                }
            }
        },
        #filter=[{"term": {"metadata.source.keyword": field_name}}],
    )


def is_document_exists(field_name):
    resp = research_index.search(
        index=ES_INDEX_RELEVANCE,
        query={
            "term": {
                "field_name.keyword": field_name
            }
        }
    )        
    return resp['hits']['total']['value']
    #return len(resp['hits']['hits'])
    
    
def get_package_dataset_documents(package_name, dataset_name):
    resp = research_index.search(
        index=ES_INDEX_RELEVANCE,
        query={
            "bool": {
                "must": [
                    {"term": {"dataset_name.keyword": dataset_name}},
                    {"term": {"package_name.keyword": package_name}}
                ]
            }
        }
    )
    return resp

# def get_package_dataset_research_details(package_name, dataset_name):
#     res = get_package_dataset_documents(
#         package_name=package_name,
#         dataset_name=dataset_name,
#     )
#     research_details_list = []
#     data = [] 
#     if res['hits']['total']['value'] > 0:
#         data = res['hits']['hits']
#         for item in data:
#             print(item)
#             if 'research_details' in item['_source'] and isinstance(item['_source']['research_details'], str):
#                 research_details_list.append(item['_source']['research_details'])
    
#     research_details = " ".join(research_details_list)
#     return research_details

def get_document(field_name):
    resp = research_index.search(
        index=ES_INDEX_RELEVANCE,
        query={
            "term": {
                "field_name.keyword": field_name
            }
        }
    )
    try:
        document = {
            "research_details": resp['hits']['hits'][0]['_source']['research_details'],
            "package_name": resp['hits']['hits'][0]['_source']['package_name'],
            "dataset_name": resp['hits']['hits'][0]['_source']['dataset_name'],
            "field_name": resp['hits']['hits'][0]['_source']['field_name'],
            "research_cost": resp['hits']['hits'][0]['_source']['research_cost'],
        }
    except (IndexError, KeyError, TypeError) as e:
        document = {
            "research_details": None,
            "package_name": None,
            "dataset_name": None,
            "field_name": None,
            "research_cost": None,
        }
    return resp['hits']['hits'][0]['_id'], document


def store_research_details(field_name, document="", 
                           research_cost=0.0, 
                           obs_relevance = "", 
                           related_details = "",
                           alert_baselining = "",
                           threshold_baseline = "",
                           warning_threshold= "",
                           critical_threshold = "",
                           slo_configuration = ""
                           ):
    package_name, dataset_name = extract_packagename_datasetname(field_name=field_name)
    document = {
        "research_details": document,
        "package_name": package_name,
        "dataset_name": dataset_name,
        "field_name": field_name,
        "research_cost": research_cost
    }
    if is_document_exists(field_name) > 0:
        doc_id, document = get_document(field_name)
        document["obs_relevance"] = obs_relevance
        document["related_details"] = related_details
        document["alert_baselining"] = alert_baselining
        document["threshold_baseline"] = threshold_baseline
        document["warning_threshold"] = warning_threshold
        document["critical_threshold"] = critical_threshold,
        document["slo_configuration"] = slo_configuration
        
        research_index.update(index=ES_INDEX_RELEVANCE, id=doc_id, doc=document, refresh=True)
    else:
        research_index.index(id=str(uuid4()),document=document, index=ES_INDEX_RELEVANCE, refresh=True)

        

# def store_alert_relevance(state: GraphState):
#     field_name = state['field_name']
#     package_name, dataset_name = extract_packagename_datasetname(field_name=field_name)
#     document = {
#         "alert_relevance" : state["alert_relevance"],
#         "alert_related_details": state["alert_related_details"],
#         "package_name": package_name,
#         "dataset_name": dataset_name,
#         "field_name": field_name,
#     }
#     research_index.index(id=str(uuid4()),document=document, index=ES_INDEX_RELEVANCE)
    

def store_docs_es_vectorstore(document, field_name, research_cost = 0.0):
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=200, chunk_overlap=50
    )
    documents = text_splitter.create_documents([document])
    for i in range(len(documents)):
        documents[i].metadata = {"source": field_name, "cost": research_cost}
    
    uuids = [str(uuid4()) for _ in range(len(documents))]
    vector_store.add_documents(documents=documents, ids=uuids)

def insert_or_update_elastic_fields(research_details="", critical_threshold="", related_details="", dataset_name="", field_name="", research_cost=0.0, warning_threshold="", obs_relevance="", package_name="", threshold_baseline="", alert_baselining=""):
    try:
        # Fetch MySQL connection details from the .env file
        #host = os.getenv("MYSQL_HOST")
        # user = os.getenv("MYSQL_USER")
        # password = os.getenv("MYSQL_PASSWORD")
        # database = os.getenv("MYSQL_DATABASE")
        # package_name, dataset_name = extract_packagename_datasetname(field_name=field_name)

        # Establish a connection to the MySQL database
        # connection = mysql.connector.connect(
        #     host=host,
        #     user=user,
        #     password=password,
        #     database=database
        # )
        try:
            connection = mysql.connector.connect(
                host="host.docker.internal",
                user=user,
                password=password,
                database=database,
                # use_pure=True
            )
        except:
            connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                # use_pure=True
            )
        if connection.is_connected():
            print("Inside the IF Statement")
            cursor = connection.cursor()

            # Check if the field_name already exists in the table
            select_query = "SELECT COUNT(*) FROM elastic_fields WHERE field_name = %s"
            cursor.execute(select_query, (field_name,))
            result = cursor.fetchone()

            if result[0] > 0:
                # Record exists, so update the record
                update_query = """
                UPDATE elastic_fields
                SET 
                    critical_threshold = %s,
                    related_details = %s,
                    warning_threshold = %s,
                    obs_relevance = %s,
                    threshold_baseline = %s,
                    alert_baselining = %s
                WHERE field_name = %s
                """

                update_values = (
                    critical_threshold,
                    related_details,
                    warning_threshold,
                    obs_relevance,
                    threshold_baseline,
                    alert_baselining,
                    field_name
                )
                print("Going to update")
                cursor.execute(update_query, update_values)

            else:
                # Record doesn't exist, so insert new data
                insert_query = """
                INSERT INTO elastic_fields (
                    critical_threshold,
                    research_details,
                    related_details,
                    dataset_name,
                    field_name,
                    research_cost,
                    warning_threshold,
                    obs_relevance,
                    package_name,
                    threshold_baseline,
                    alert_baselining
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """

                insert_values = (
                    critical_threshold,
                    research_details,
                    related_details,
                    dataset_name,
                    field_name,
                    research_cost,
                    warning_threshold,
                    obs_relevance,
                    package_name,
                    threshold_baseline,
                    alert_baselining
                )
                print("Going to insert")
                cursor.execute(insert_query, insert_values)

            # Commit the transaction
            print("Going to commit")
            connection.commit()

            print(f"Operation successful: {'Updated' if result[0] > 0 else 'Inserted'} record for field_name: {field_name}")
            return 0
    except Error as e:
        print("************************************************************************************")
        print(f"Error: {e}")
        print("************************************************************************************")
        if connection.is_connected():
            connection.rollback()
        return -1
    finally:
        # Close the connection
        if connection.is_connected():
            cursor.close()
            connection.close()