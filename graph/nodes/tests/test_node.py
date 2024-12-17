from graph.nodes.ingestion import get_es_retriever, store_docs_es_vectorstore, store_research_details
# from graph.nodes.alert_relevance_storage import store_alert_relevance
from graph.nodes.ingestion import is_document_exists, store_research_details, insert_or_update_elastic_fields, get_package_dataset_documents
from graph.state import GraphState
import json
from langchain_core.documents import Document

def test_store_retrieve_yes():
    store_docs_es_vectorstore(
        """
### Alert Thresholds

Oracle databases use alert thresholds to notify administrators when tablespace usage reaches critical levels. These thresholds can be set for individual tablespaces or database-wide, using the DBMS_SERVER_ALERT package. Commonly used thresholds include warning and critical levels, typically set at 85% and 97% of tablespace capacity, respectively ([Oracle Docs](https://docs.oracle.com/en/database/oracle/oracle-database/18/spmsu/set-threshold-values-for-tablespace-alerts.html)).""",
        "test_field"
    )
    retriever = get_es_retriever("test_field")
    documents = retriever.invoke("What is the alert warning and critical threshold")
    print(documents)
    assert(len(documents) > 0)


def test_store_retrieve_no():
    store_docs_es_vectorstore(
        """
### Alert Thresholds

Oracle databases use alert thresholds to notify administrators when tablespace usage reaches critical levels. These thresholds can be set for individual tablespaces or database-wide, using the DBMS_SERVER_ALERT package. Commonly used thresholds include warning and critical levels, typically set at 85% and 97% of tablespace capacity, respectively ([Oracle Docs](https://docs.oracle.com/en/database/oracle/oracle-database/18/spmsu/set-threshold-values-for-tablespace-alerts.html)).""",
        "test_field"
    )
    retriever = get_es_retriever("abcdefg")
    documents = retriever.invoke("What is the alert warning and critical threshold")
    print(documents)
    assert(len(documents) == 0)

def test_store_retrieve_no():
    store_docs_es_vectorstore(
        """
### Alert Thresholds

Oracle databases use alert thresholds to notify administrators when tablespace usage reaches critical levels. These thresholds can be set for individual tablespaces or database-wide, using the DBMS_SERVER_ALERT package. Commonly used thresholds include warning and critical levels, typically set at 85% and 97% of tablespace capacity, respectively ([Oracle Docs](https://docs.oracle.com/en/database/oracle/oracle-database/18/spmsu/set-threshold-values-for-tablespace-alerts.html)).""",
        "test_field"
    )
    retriever = get_es_retriever("test_field")
    documents = retriever.invoke("What is the cost of the pizza?")
    assert(len(documents) > 0)

# -- Not needed -----#
# def test_alert_relevance_storage():
#     state = GraphState(
#         field_name =  'redis.info.clients.max_input_buffer',
#         alert_related_details = 'The `max_input_buffer` metric is monitored with hard and soft limits; exceeding the hard limit results in immediate client disconnection, while the soft limit allows temporary spikes before disconnection. Setting these thresholds appropriately is crucial to prevent excessive memory usage and maintain service availability.',
#         alert_relevance= 'The alert is highly relevant in determining system availability as it helps monitor the `max_input_buffer` metric, which indicates the largest input buffer size among active clients. If this metric approaches its thresholds, it signals potential resource consumption issues that could lead to performance degradation or server crashes. Properly configured alert thresholds and warning levels allow for timely intervention to maintain system stability.'
#     )
#     if is_document_exists(state) == 0:
#         store_alert_relevance(state)

#     resp = is_document_exists(state)
#     assert resp > 0

def test_alert_relevance_storage():
    field_name = 'redis.test.field_name_part1.field_name_part2'
    document = "test research document"
    
    # state = GraphState(
    #     field_name =  'redis.info.clients.max_input_buffer',
    #     alert_related_details = 'The `max_input_buffer` metric is monitored with hard and soft limits; exceeding the hard limit results in immediate client disconnection, while the soft limit allows temporary spikes before disconnection. Setting these thresholds appropriately is crucial to prevent excessive memory usage and maintain service availability.',
    #     alert_relevance= 'The alert is highly relevant in determining system availability as it helps monitor the `max_input_buffer` metric, which indicates the largest input buffer size among active clients. If this metric approaches its thresholds, it signals potential resource consumption issues that could lead to performance degradation or server crashes. Properly configured alert thresholds and warning levels allow for timely intervention to maintain system stability.'
    # )
    store_research_details(field_name, document,0.0)
    
    #assert is_document_exists(field_name) == 1
    store_research_details(field_name, None, 0.0, "alert relevance information", "alert related metrics description")
    assert is_document_exists(field_name) == 1

def test_insert_or_update_elastic_fields():
    res = insert_or_update_elastic_fields(
            research_details="# Redis Performance Tuning: A Deep Dive\n\n## Key Insights",
            critical_threshold='10',
            related_details="Metrics like `connected_clients` and `used_memory` are used to monitor Redis performance...",
            dataset_name="info",
            field_name="redis.info.memory.used_memory_human",
            research_cost=0.0876543,
            warning_threshold='0',
            obs_relevance="Proactive monitoring through metrics like memory usage helps identify performance bottlenecks...",
            package_name="redis",
            threshold_baseline="used_memory, connected_clients",
            alert_baselining=True
    )
    assert res == 0

def test_get_package_dataset_documents():
    res = get_package_dataset_documents(
        package_name="nginx",
        dataset_name="stubstatus",
    )
    research_details_list = []
    data = [] 
    if res['hits']['total']['value'] > 0:
        data = res['hits']['hits']
        for item in data:
            # research_details_list.append(item['_source'])
            
            # research_details_list.append({
            #     'field_name': item['_source']['field_name'],
            #     'research_details': item['_source']['research_details'],
            #     'dataset_name': item['_source']['dataset_name'],
            #     'research_details': item['_source']['research_details'],
                
                
            # })
            if 'research_details' in item['_source'] and isinstance(item['_source']['research_details'], str):
                research_details_list.append(
                    Document(
                        page_content=item['_source']['research_details'],
                        metadata={
                            'field_name': item['_source']['field_name'],
                            'dataset_name': item['_source']['dataset_name'],
                            'package_name': item['_source']['package_name']
                        }
                    )
                )
    
    # research_details = " ".join(research_details_list)
    # print(json.dumps(research_details_list))
    # return research_details