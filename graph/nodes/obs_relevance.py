from typing import Dict, Any

from graph.chains.relevance_summarizer import ObsRelevance, alert_relevance_chain
from graph.nodes.ingestion import store_research_details, insert_or_update_elastic_fields

from graph.state import GraphState

def relevance_generator(state: GraphState) -> Dict[str, any]:
    print("--- GENERATE OBS RELEVANCE DATA---")
    question = """What is the relevance of the alert in determining the availability or scalability or performance or errors of the system?
    What is the name, description of metrics, related metrics, formula of determining availability or scalability or performance or errors or alerts of the system?
    """
    documents = state["documents"]
    field_name = state["field_name"]
    
    relevance_details: ObsRelevance = alert_relevance_chain.invoke({
        "context": documents,
        "question": question
    })
    
    store_research_details(field_name=field_name, 
                           obs_relevance=relevance_details.obs_relevance,
                           related_details=relevance_details.related_details,
                           alert_baselining = state["alert_baselining"],
                           threshold_baseline = state["threshold_baseline"],
                           warning_threshold = state["warning_threshold"],
                           critical_threshold = state["critical_threshold"],
                           slo_configuration=state["slo_configuration"]
                           )
    
    insert_or_update_elastic_fields(
            obs_relevance=relevance_details.obs_relevance,
            related_details=relevance_details.related_details,
            warning_threshold = state["warning_threshold"],
            threshold_baseline = state["threshold_baseline"],
            alert_baselining = state["alert_baselining"],
            critical_threshold = state["critical_threshold"],
            field_name=field_name)
    
    # document_exist = is_document_exists(state)
    # print("**************************************")
    # print(document_exist)
    # print("**************************************")
    # if is_document_exists(state) == 0:
    #     store_alert_relevance(state)

    return {
        "obs_relevance": relevance_details.obs_relevance,
        "alert_related_details": relevance_details.related_details,
        "field_name": field_name,
    }
