from dotenv import load_dotenv
load_dotenv()
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableSequence


def dot_to_space(input_string):
    return input_string.replace('.', ' ')

def uscore_to_space(input_string):
    return input_string.replace('_', ' ')

class GenerateSearchTopic(BaseModel):
    """Generate search string using the observability metric name and metric description"""
    search_topic: str = Field(
        description="the search topic"
    )
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

structured_llm_grader = llm.with_structured_output(GenerateSearchTopic)

search_topic_generator_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a search expert specializing in observability metrics. Based on both metric name and metric description, generate a search topic in the context of observability or monitoring of IT infrastructure. You MUST try to  use both metric name and metric description to generate the ideal search string. Words such as 'ms', 'sec', 'count', 'counter', indicate the unit of metric and it can be excluded from creating the topic title."),
    ("human", "Metric Name:\n\n{metric_name}\n\nMetric Description:\n\n{metric_description}\n\n"),
])

search_topic_generator: RunnableSequence = search_topic_generator_prompt | structured_llm_grader
