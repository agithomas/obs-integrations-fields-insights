from typing import Any, Dict
from graph.chains.search_topic_generator import search_topic_generator, dot_to_space, uscore_to_space
from graph.state import GraphState

def research_search_topic_generator(state: GraphState) -> Dict[str, Any]:
    print("--- RUNNING SEARCH TOPIC GENERATOR ---")
    field_name = state["field_name"]
    field_description = state["field_description"]
    field_name_expanded = dot_to_space(field_name)
    field_name_final = uscore_to_space(field_name_expanded)
    
    search_query_details =  search_topic_generator.invoke(
        {
            "metric_name": field_name_final,
            "metric_description": field_description,
        }
    )
    
    print(search_query_details)
    return {
        "topic": search_query_details.search_topic,
        "field_name": field_name,
    }