from dotenv import load_dotenv
load_dotenv()
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableSequence
from typing import List

class ObsRelevance(BaseModel):
    """Tdentify the relevance of the alert in determining the availability of the system."""

    obs_relevance: str = Field(
        description="the relevance in determining the availability or scalability or performance or errors of the system."
    )
    related_details: str = Field(
        description="name, description of metrics, related metrics, formula of determining availability or scalability or performance or errors or alerts of the system"
    )
    

# GPT 3.5 Turbo failed to extract all the values. Hence went with gpt-4o
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

structured_llm_grader = llm.with_structured_output(ObsRelevance)

prompt = hub.pull("rlm/rag-prompt")

alert_relevance_chain: RunnableSequence = prompt | structured_llm_grader