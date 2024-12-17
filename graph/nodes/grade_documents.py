from typing import Any, Dict
from graph.chains.retriever_grader import retrieval_grader
from graph.state import GraphState

def grade_documents(state: GraphState) -> Dict[str, Any]:
    """
    Determine whether the retrieved documents are relevant to the question.
    If any document is not relevant, we will set the flag to run web search

    Args:
        state (GraphState): The current graph state

    Returns:
        Dict[str, Any]: Filtered out irrelevant documents and updated web_search state.
    """
    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]
    
    filtered_docs = []
    is_research_needed = False
    
    for d in documents:
        score = retrieval_grader.invoke(
            {
                "question": question,
                "document": d.page_content
            }
        )
        grade = score.binary_score
        if grade.lower() == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT: REMOVING---")
            #is_research_needed = True
            continue
    
    if len(filtered_docs) == 0:
        is_research_needed = True

    return {
        "filtered_documents": filtered_docs,
        "question": question,
        "is_research_needed": is_research_needed
    }
        