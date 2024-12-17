from typing import List, TypedDict

class GraphState(TypedDict):
    """
    Represent the state of the graph.
    
    Attributes:
        research_question: LLM generated question to query the researcher
        question: Formatted question - What is the warning and alert threshold?
        field_name: Name of the field
        field_description: Field Description
        warning_threshold: Warning threshold for the alert using the field
        critical_threshold: Critical threshold for the alert using the field
        is_threshold_availalbe: If either warning or critical threshold is available
        references:  List of references mentioned in the document
        thread_id : This is same as the name of the field. This is for checkpointing.
        asset_preset_selected: Indicate if the field with its threshold is selected for asset preset generation
        use_historical_data: Flag indicates, if a historical value is to be considered for alert generation. 
        is_alert_theshold_halluciated: Indicate if the threshold is based on hallication or not
        is_use_historical_data_hallucinated: Indicate if the historical value for alert configuration, generated based on halluication.
        research_cost: Cost of running gpt researcher only. 
    """
    question: str
    research_question: str = ""
    field_name: str = None
    field_description: str = None
    warning_threshold: str
    critical_threshold: str
    slo_configuration: str
    #is_threshold_availalbe: bool
    references: List[str]
    thread_id: str
    # asset_preset_selected: bool = False
    # use_historical_data: bool = False
    # is_alert_theshold_halluciated: bool= True
    # is_use_historical_data_hallucinated: bool = True
    is_research_needed: bool = True
    # force_research: str = "N"
    research_answer: str
    # research_cost: float = 0.0
    research_complete_flag: bool = False
    documents: List[str]
    filtered_documents: List[str]
    alert_baselining: bool
    threshold_baseline: str
    obs_relevance: str
    alert_related_details: str
    topic: str
  