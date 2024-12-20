from langgraph.graph import StateGraph, START, END
from graph.consts import RETRIEVE, GRADE_DOCUMENTS, ALERT_THRESHOLD_GENERATOR, PREPARE_RETRIEVER_QUESTION, RESEARCHER_CHOICE, OBS_FIELD_RESEARCHER, RELEVANCE_GENERATOR, RESEARCH_TOPIC_GENERATOR, SAVE_RESEARCH_REPORT
from graph.nodes import retrieve, grade_documents, alert_threshold_generate, save_research_report, research_search_topic_generator, relevance_generator, gr_researcher
from langgraph.checkpoint.memory import MemorySaver
from graph.nodes import configuration
#from langgraph.checkpoint.sqlite import SqliteSaver
from graph.state import GraphState
#import sqlite3
from langgraph.errors import NodeInterrupt
import uuid
#import os
#FORCE_RESEARCH_FLAG = os.getenv('FORCE_RESEARCH_WITHOUT_CONFIRMATION') or "N"
#conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
#memory = SqliteSaver(conn=conn)
memory= MemorySaver()
thread = {
    "configurable": {
        "thread_id": str(uuid.uuid4())
    }
}


def prepare_retriever_question(state: GraphState):
    print("--- Preparing Retriever Question ---")
    return {
        "question": """Define the alert's warning and critical thresholds, specifying the reference value, capacity, and metric used for comparison. Provide the names of the metrics, any related metrics, and the burn rate associated with the SLO. Explain whether historical metric data should be considered when setting these thresholds and how it impacts accuracy.""",
        #"force_research": FORCE_RESEARCH_FLAG,
    }

def researcher_choice(state: GraphState):
    print("<<ALERT>>!!!: No valid records available to determine the Warning and Critical Threshold for the field : ",state["field_name"])
    print("Do you want to run the GPT Reasearcher to perform research? Enter Y (Yes) to continue or N (No) to stop the chain without outcome")
    print("<<NOTE>>!!!: Running GPT Research would incur cost. The exact cost of running GPT researcher will be known after the run")
    raise NodeInterrupt(
            f"Interrupted to take user input - if to run GPT Researcher or not"
    )
    


def research_confirmation(state):
    research_run_enabled = state["is_research_needed"] 
    if research_run_enabled == True:
        return RESEARCH_TOPIC_GENERATOR
    else: 
        return END

    
def decide_to_generate(state):
    
    print("---ASSESS GRADED DOCUMENTS---")
    if len(state["filtered_documents"]) > 0:
        return ALERT_THRESHOLD_GENERATOR
    # elif (len(state["filtered_documents"]) == 0) and (state["force_research"] == "Y"):
    #     return RESEARCH_SEARCH_STRING_GENERATOR
    # elif len(state["filtered_documents"]) == 0 and state["research_complete_flag"] == True:
    #     return END
    # elif len(state["filtered_documents"]) == 0:
    #     return RESEARCH_SEARCH_STRING_GENERATOR
    else:
        return RESEARCHER_CHOICE

def welcome(state: GraphState):
    if state["field_name"] == "welcome":
        return END
    else:
        return PREPARE_RETRIEVER_QUESTION


builder = StateGraph(GraphState, config_schema=configuration.Configuration)

# builder.add_node(prepare_retriever_question, PREPARE_RETRIEVER_QUESTION)
# builder.add_node(retrieve, RETRIEVE)
# builder.add_node(grade_documents, GRADE_DOCUMENTS)
# builder.add_node(alert_threshold_generate, ALERT_THRESHOLD_GENERATOR)
# builder.add_node(researcher_choice, RESEARCHER_CHOICE)
# builder.add_node(research_search_topic_generator, RESEARCH_TOPIC_GENERATOR)
# #builder.add_node(research_search_string_generator, RESEARCH_SEARCH_STRING_GENERATOR)
# builder.add_node(obs_field_researcher, OBS_FIELD_RESEARCHER)
# builder.add_node(relevance_generator, RELEVANCE_GENERATOR)

builder.add_node( PREPARE_RETRIEVER_QUESTION,prepare_retriever_question)
builder.add_node( RETRIEVE, retrieve)
builder.add_node(GRADE_DOCUMENTS, grade_documents)
builder.add_node(ALERT_THRESHOLD_GENERATOR, alert_threshold_generate)
builder.add_node(RESEARCHER_CHOICE, researcher_choice)
builder.add_node(RESEARCH_TOPIC_GENERATOR, research_search_topic_generator)
#builder.add_node(research_search_string_generator, RESEARCH_SEARCH_STRING_GENERATOR)
builder.add_node(OBS_FIELD_RESEARCHER, gr_researcher.compile())
builder.add_node(RELEVANCE_GENERATOR, relevance_generator)
builder.add_node(SAVE_RESEARCH_REPORT, save_research_report)

builder.add_edge(START, PREPARE_RETRIEVER_QUESTION)
builder.add_edge(PREPARE_RETRIEVER_QUESTION, RETRIEVE)
builder.add_edge(RETRIEVE, GRADE_DOCUMENTS)
builder.add_conditional_edges(
    GRADE_DOCUMENTS,
    decide_to_generate,
    {
        ALERT_THRESHOLD_GENERATOR: ALERT_THRESHOLD_GENERATOR,
        RESEARCHER_CHOICE: RESEARCHER_CHOICE,
        #RESEARCH_SEARCH_STRING_GENERATOR: RESEARCH_SEARCH_STRING_GENERATOR
        
    }
)

builder.add_conditional_edges(
    RESEARCHER_CHOICE,
    research_confirmation,
    {
        RESEARCH_TOPIC_GENERATOR: RESEARCH_TOPIC_GENERATOR,
        END: END
    }
)
builder.add_edge(RESEARCH_TOPIC_GENERATOR, OBS_FIELD_RESEARCHER)
builder.add_edge(OBS_FIELD_RESEARCHER, SAVE_RESEARCH_REPORT)
builder.add_edge(SAVE_RESEARCH_REPORT, RETRIEVE)
builder.add_edge(ALERT_THRESHOLD_GENERATOR, RELEVANCE_GENERATOR)
builder.add_edge(RELEVANCE_GENERATOR, END)


graph = builder.compile(
    checkpointer=memory,
    #interrupt_before=["get_package_field_details"]
)

graph.get_graph().draw_mermaid_png(output_file_path="graph.png")

def stream_graph_updates(user_input):
    for event in graph.stream(user_input, thread, stream_mode="values"):
        print(event)

    state = graph.get_state(thread)
    if state.next == ('researcher_choice',) :
        # if state["is_research_needed"] == True:
        #     print("<<ALERT>>!!!: You have already run the research but failed to get any information. This is a research re-run")
        
        research_run_input = input("Do you prefer to run GPT-Researcher Y (Yes) / N (No) : > ")
        if research_run_input == "Y":
            research_run_input_bool = True
        else:
            research_run_input_bool = False

        graph.update_state(
            thread,
            values={
                "is_research_needed": research_run_input_bool,
                #"research_complete_flag": False
            },
            as_node=RESEARCHER_CHOICE
        )

        for event in graph.stream(None, thread, stream_mode="values"):
            print(event)

# # while True:
# try:
#     field_name = input("Field Name: ")
#     if field_name.lower() in ["quit", "exit", "q"]:
#         print("Goodbye!")
#         exit(0)

#     field_description = input("Field Description: ")
#     user_input = {
#         "field_name" : field_name,
#         "field_description": field_description,
#         "force_research": "Y"
#     }
#     stream_graph_updates(user_input)
# except:
#     # fallback if input() is not available
#     user_input = {
#         "field_name" : "quit",
#         "field_description": "welcome.",
#         "force_research": "Y"
#     }
#     #stream_graph_updates(user_input)
    