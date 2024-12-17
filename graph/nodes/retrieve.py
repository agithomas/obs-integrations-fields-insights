from typing import Any, Dict

from graph.state import GraphState
from graph.nodes.ingestion import get_es_retriever


def retrieve(state: GraphState) -> Dict[str, Any]:
    print("---RETRIEVE---")
    question = state["question"]
    field_name = state["field_name"]
    retriever = get_es_retriever(field_name=field_name)
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}