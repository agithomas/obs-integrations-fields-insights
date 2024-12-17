from dotenv import load_dotenv
load_dotenv()
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableSequence


def dot_to_space(input_string):
    return input_string.replace('.', ' ')

class GenerateSearchQuery(BaseModel):
    """Generate search string using the observability metric name and metric description"""
    search_string: str = Field(
        description="the search string to query the search engines"
    )
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

structured_llm_grader = llm.with_structured_output(GenerateSearchQuery)

search_string_generator_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a search expert specializing in observability metrics. Based on both metric name and metric description, generate a search query that can help determine if this metric is suitable for configuring warning and critical alert thresholds in observability systems. You MUST use both metric name to generate the ideal search string. Ensure the search string targets resources related to alert thresholds and warning levels. "),
    ("human", "Metric Name:\n\n{metric_name}\n\nMetric Description:\n\n{metric_description}\n\n"),
])

search_string_generator: RunnableSequence = search_string_generator_prompt | structured_llm_grader
