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

#prompt = hub.pull("rlm/rag-prompt")
system = """
You are a helpful site reliability engineer and has knowledge on Observability alert and slo configurations. Your responsibility is to go through the context and advice on the alert thresholds and slo configurations. 
Use the following pieces of retrieved context to answer the question. 

Help the user by
- Identifying name of metric, description of a metric.
- If the name of the metric is not available but description is available, create a metric name that is easy to understand.
- Determine if there are any related metrics 
- Formulate an alert warning threshold formula using one or more metrics. Represent using the metric names.
- Formulate an alert critical threshould formula using one or more metrics. Represent using metric names.
- Determine if the historical value of the metrics needs to be taken into consideration to determine the alert threshold value. 
- Formulate an SLO with SLI configurations using the using the metrics. 

If you don't know the answer, just say that you don't know.
"""
human = """
Question: {question} 
Context: {context} 
Answer:
"""
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

prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", human)
])


alert_threshold_generator: RunnableSequence = prompt | structured_llm_grader
