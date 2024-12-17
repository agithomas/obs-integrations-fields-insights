from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(temperature=0)
"""
Prompt description is as follows:
    Use the following pieces of retrieved context to answer the question.
"""
prompt = hub.pull("rlm/rag-prompt")

generation_chain = prompt | llm | StrOutputParser()
