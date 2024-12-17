from typing import Dict, Any

from graph.chains.researcher import ResearchAnswer, research_assistant,get_report
from graph.nodes.ingestion import store_docs_es_vectorstore, vector_store, store_research_details, insert_or_update_elastic_fields
from graph.state import GraphState

def save_research_report(state: GraphState) -> Dict[str, Any]:
    print("--- Saving Research results in ES---")
    report = state["research_answer"]
    field_name = state["field_name"]
    
    
    # research_details: ResearchAnswer = research_assistant.invoke({
    #     "input": research_question,
    # })
    #report, cost = get_report(research_question)
    
    store_docs_es_vectorstore(
        document=report,
        field_name=field_name,
        # research_cost=cost,
    )
    store_research_details(
        document=report,
        field_name=field_name,
        # research_cost=cost,
    )
    insert_or_update_elastic_fields(
        research_details=report,
        field_name=field_name,
        # research_cost=cost
    )
    
    return {
        "research_complete_flag": True,
        "research_answer": report,
        # "research_cost": cost,
        # "research_question": research_question,
    }
