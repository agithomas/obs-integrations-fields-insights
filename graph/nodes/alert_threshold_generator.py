from typing import Dict, Any

from graph.chains.alert_threshold_generator import alert_threshold_generator, AlertThreshold
from graph.state import GraphState

def alert_threshold_generate(state: GraphState) -> Dict[str, any]:
    print("--- GENERATE ---")
    question = state["question"]
    documents = state["filtered_documents"]
    
    alert_threshold_details = alert_threshold_generator.invoke({
        "context": documents,
        "question": question
    })
    return {
        "warning_threshold": alert_threshold_details.warning_threshold,
        "critical_threshold": alert_threshold_details.critical_threshold,
        "alert_baselining": alert_threshold_details.alert_baselining,
        "threshold_baseline": alert_threshold_details.threshold_baseline,
        "slo_configuration": alert_threshold_details.slo_configuration
    }
