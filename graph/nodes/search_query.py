from typing import Any, Dict
from graph.chains.search_query_generator import search_string_generator, dot_to_space, GenerateSearchQuery
from graph.state import GraphState

def research_search_string_generator(state: GraphState) -> Dict[str, Any]:
    print("--- RUNNING SEARCH QUERY GENERATOR ---")
    field_name = state["field_name"]
    field_description = state["field_description"]
    field_name_expanded = dot_to_space(field_name)
    
    search_query_details =  search_string_generator.invoke(
        {
            "metric_name": field_name_expanded,
            "metric_description": field_description,
        }
    )
    
    print(search_query_details)
    return {
        "research_question": search_query_details.search_string,
        "field_name": field_name,
    }
