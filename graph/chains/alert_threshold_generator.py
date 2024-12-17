from dotenv import load_dotenv
load_dotenv()
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableSequence
from typing import List

class AlertThreshold(BaseModel):
    """Thresholds for alert warnings and critical conditions."""

    warning_threshold: str = Field(
        description="Specify the alert warning threshold value based on the context. If unknown, provide a suggested value making use of the information in the context following the format mentioned. Format: 'I could not find the details, Suggestion: 70% of the dropped client connections as the dropped connection indicate an issue in accepting connection'"
    )
    critical_threshold: str = Field(
        description="Specify the alert critical threshold value based on the context. If unknown, provide a suggested value making use of the information in the context following the format mentioned. Format: 'I could not find the details, Suggestion: 90% of the total memory of the system considering the memory overuse may lead to reduced performance'"
    )
    threshold_baseline: str = Field(
        description="Specify the reference metric or baseline used for defining the warning or critical thresholds."
    )
    alert_baselining: str = Field(
        description="Indicate if historical metrics should be considered for setting alert thresholds. If unknown, return an empty string."
    )
    slo_configuration: str = Field(
        description="Details on how to configurure SLO and SLI configuration including related metrics, burn rate, reasoning behind configuring the slo. If unknown, return empty string"
    )
    

# GPT 3.5 Turbo failed to extract all the values. Hence went with gpt-4o
llm = ChatOpenAI(model="gpt-4o", temperature=0)

structured_llm_grader = llm.with_structured_output(AlertThreshold)

prompt = hub.pull("rlm/rag-prompt")

# system = """You are an observability domain researcher evaluating whether the research document contains information on alert warning and critical thresholds. Return 'True' if either threshold is present, otherwise return 'False'.
# Extract the values for both warning and critical thresholds. 
# If the alert warning details is not present in the research document, the warning threshold value is -1. 
# If the critical warning details is not present in the research document, the crtical threshold value is -1.
# Use only the research document to answer the question. Do not assume answers.

# Question: 

#     What are the alert warning and critical thresholds? 
# """

# prompt = ChatPromptTemplate.from_messages([
#     ("system", system),
#     ("human", "Research Document:\n\n{research_document}\n\n Question: \n\n {question}\n"),
# ])

# prompt = ChatPromptTemplate.from_messages([
#     ("system", system),
#     ("human", "Research Document:\n\n{research_document}\n\n Question: \n\n {question}\n"),
# ])


alert_threshold_generator: RunnableSequence = prompt | structured_llm_grader
