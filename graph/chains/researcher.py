import os
from dotenv import load_dotenv
load_dotenv()
#from gpt_researcher import GPTResearcher
# from gpt_researcher.utils.enum import ReportSource, ReportType
import asyncio
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import tool
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

GPT_RESEARCHER_CONFIG_PATH = os.getenv('GPT_RESEARCHER_CONFIG_PATH')

class ResearchAnswer(BaseModel):
    research_answer: str = Field(
        description="Answer to the research topic"
    )
    research_cost: float = Field(
        description="Cost of doing the research"
    )
    
@tool
def get_report(query: str):

    """
    Args:
        query (str): Research Question
    """
    pass

# @tool
# def get_report(query: str):

#     """
#     Args:
#         query (str): Research Question
#     """
#     async def run_research():
#         researcher = GPTResearcher(
#             query, 
#             max_subtopics=5,
#             subtopics=[
#                 "Observability Alert threshold configuration",
#                 "Sustenance period before alerting.",
#                 "Details of all relevant metrics under the observability category"
#                 "Relevance to the overall health, availability, performance, latency of the system"
#                 "key parameters, metrics, queries, endpoints for measuring the health"
#                 ""
#             ],
#             verbose=False,
#             #parent_query="Provide the warning and critical alert thresholds for observability metrics, along with their significance",
#             config_path=GPT_RESEARCHER_CONFIG_PATH
#         )
#         research_result = await researcher.conduct_research()
#         report = await researcher.write_report()
#         return report, float(researcher.get_costs())
    
#     report, cost = asyncio.run(run_research())
#     return report, cost


tools = [get_report]

prompt = ChatPromptTemplate.from_messages([
    ("system", "you're a helpful research assistant who answers the research question and gives answer and cost of doing the research"), 
    ("human", "{input}"), 
    ("placeholder", "{agent_scratchpad}"),
])


# llm_with_tools = ChatOpenAI().bind_tools(tools)
# structured_llm = llm_with_tools.with_structured_output(ResearchAnswer)
# agent = create_tool_calling_agent(structured_llm, tools, prompt)

llm = ChatOpenAI()
agent = create_tool_calling_agent(llm, tools, prompt)

research_assistant = AgentExecutor(agent=agent, tools=tools, verbose=True)

