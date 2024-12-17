from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI

class GradeAnswer(BaseModel):
    binary_score: bool = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )

llm = ChatOpenAI(temperature=0)
structred_llm_grader = llm.with_structured_output(GradeAnswer)

system = """You are a grader assessing whether an answer addresses / resolves a question \n\
Give a binary score 'yes' or 'no'. 'yes' means the answer resolves the question."""

answer_prompt = ChatPromptTemplate(
    [
        ("system", system),
        ("human", "User Question: \n\n {question} \n\n LLM Generation: {generation}")
    ]
)

answer_grader: RunnableSequence = answer_prompt | structred_llm_grader
