# The purpose of this chain is to determine if the answer generated 
# by the generate node is grounded based on the documents or hallucinated

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(temperature=0)

class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in the generated answer"""
    binary_score: bool = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )

structured_llm_grader = llm.with_structured_output(GradeHallucinations)

system = """You are a grader assessing whether an LLM is grounded in / supported by a set of retrieved facts \n
Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts \n
"""

hallucination_prompt = ChatPromptTemplate(
    [
        ("system", system),
        ("human", "Set of facts: \n\n {documents}\n\n LLM Generation : {generation}") #The generation content is of the format : The alert warning threshold value is {alert_warning_threshold} and critical warning threshold is {critical_warning_threshold}"
    ]
)
hallucination_grader: RunnableSequence = hallucination_prompt | structured_llm_grader
