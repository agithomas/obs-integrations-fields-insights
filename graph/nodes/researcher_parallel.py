import os
from dotenv import load_dotenv
load_dotenv()

import asyncio
import operator
from typing_extensions import TypedDict
from typing import  Annotated, List, Optional, Literal
from pydantic import BaseModel, Field

from tavily import TavilyClient, AsyncTavilyClient

from langchain_openai import ChatOpenAI


from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from langgraph.constants import Send
from langgraph.graph import START, END, StateGraph
from langsmith import traceable
from graph.nodes import configuration
import operator
from typing import Annotated

from threading import Lock

# Define a global lock
update_lock = Lock()


OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')

# LLMs 
gpt_4o = ChatOpenAI(model="gpt-4o-mini", temperature=0) 
#https://github.com/langchain-ai/langchain/issues/27962
#gpt_4o = BedrockLLM(model="claude-3-5-sonnet-20240620", temperature=0) 

# Search
tavily_client = TavilyClient()
tavily_async_client = AsyncTavilyClient()

class Topic:
    topic: str = Field(
        description="Topic of the report"
    )

class Section(BaseModel):
    name: str = Field(
        description="Name for this section of the report.",
    )
    description: str = Field(
        description="Brief overview of the main topics and concepts to be covered in this section.",
    )
    research: bool = Field(
        description="Whether to perform web research for this section of the report."
    )
    content: str = Field(
        description="The content of the section."
    )
    # def __add__(self, other: 'Section') -> 'Section':
    #     if not isinstance(other, Section):
    #         raise TypeError(f"Cannot add Section with {type(other)}")

    #     # Example: Combine the content and maintain the rest of the attributes from the first section
    #     return Section(
    #         name=self.name,
    #         description=self.description,
    #         research=self.research,
    #         content=self.content + "\n" + other.content
    #     )
           

class Sections(BaseModel):
    sections: List[Section] = Field(
        description="Sections of the report.",
    )

class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Query for web search.")

class Queries(BaseModel):
    queries: List[SearchQuery] = Field(
        description="List of search queries.",
    )

class ReportStateInput(TypedDict):
    topic: str # Report topic

class ReportStateOutput(TypedDict):
    research_answer: str # Final report

class ReportState(TypedDict):
    topic: str # Report topic    
    sections: list[Section] # List of report sections 
    completed_sections: Annotated[list, operator.add] # Send() API key
    report_sections_from_research: str # String of any completed sections from research to write final sections
    research_answer: str # Final report

class SectionState(TypedDict):
    section: Section # Report section 
    #section: Annotated[Section, operator.add]   

    search_queries: list[SearchQuery] # List of search queries
    source_str: str # String of formatted source content from web search
    report_sections_from_research: str # String of any completed sections from research to write final sections
    completed_sections: list[Section] # Final key we duplicate in outer state for Send() API

class SectionStateSeq(TypedDict):
    section_name: str # Report section 
    section_description: str
    #section: Annotated[Section, operator.add]   

    #search_queries: list[SearchQuery] # List of search queries
    #source_str: str # String of formatted source content from web search
    #report_sections_from_research: str # String of any completed sections from research to write final sections
    completed_sections: list[Section] # Final key we duplicate in outer state for Send() API

class SectionStateOutput(TypedDict):
    #section: Section # Report section 
    #section: Annotated[Section, operator.add]   

    search_queries: list[SearchQuery] # List of search queries
    source_str: str # String of formatted source content from web search
    report_sections_from_research: str # String of any completed sections from research to write final sections
    completed_sections: list[Section] # Final key we duplicate in outer state for Send() API
    

class SectionOutputState(TypedDict):
    completed_sections: list[Section] # Final key we duplicate in outer state for Send() API

class ResearchContent(TypedDict):
    name: str #Name of the section
    content: str # Section Content 

# Utility functions

def deduplicate_and_format_sources(search_response, max_tokens_per_source, include_raw_content=True):
    """
    Takes either a single search response or list of responses from Tavily API and formats them.
    Limits the raw_content to approximately max_tokens_per_source.
    include_raw_content specifies whether to include the raw_content from Tavily in the formatted string.
    
    Args:
        search_response: Either:
            - A dict with a 'results' key containing a list of search results
            - A list of dicts, each containing search results
            
    Returns:
        str: Formatted string with deduplicated sources
    """
    # Convert input to list of results
    if isinstance(search_response, dict):
        sources_list = search_response['results']
    elif isinstance(search_response, list):
        sources_list = []
        for response in search_response:
            if isinstance(response, dict) and 'results' in response:
                sources_list.extend(response['results'])
            else:
                sources_list.extend(response)
    else:
        raise ValueError("Input must be either a dict with 'results' or a list of search results")
    
    # Deduplicate by URL
    unique_sources = {}
    for source in sources_list:
        if source['url'] not in unique_sources:
            unique_sources[source['url']] = source
    
    # Format output
    formatted_text = "Sources:\n\n"
    for i, source in enumerate(unique_sources.values(), 1):
        formatted_text += f"Source {source['title']}:\n===\n"
        formatted_text += f"URL: {source['url']}\n===\n"
        formatted_text += f"Most relevant content from source: {source['content']}\n===\n"
        if include_raw_content:
            # Using rough estimate of 4 characters per token
            char_limit = max_tokens_per_source * 4
            # Handle None raw_content
            raw_content = source.get('raw_content', '')
            if raw_content is None:
                raw_content = ''
                print(f"Warning: No raw_content found for source {source['url']}")
            if len(raw_content) > char_limit:
                raw_content = raw_content[:char_limit] + "... [truncated]"
            formatted_text += f"Full source content limited to {max_tokens_per_source} tokens: {raw_content}\n\n"
                
    return formatted_text.strip()

def format_sections(sections: list[Section]) -> str:
    """ Format a list of sections into a string """
    formatted_str = ""
    for idx, section in enumerate(sections, 1):
        formatted_str += f"""
{'='*60}
Section {idx}: {section.name}
{'='*60}
Description:
{section.description}
Requires Research: 
{section.research}

Content:
{section.content if section.content else '[Not yet written]'}

"""
    return formatted_str

@traceable
def tavily_search(query):
    """ Search the web using the Tavily API.
    
    Args:
        query (str): The search query to execute
        
    Returns:
        dict: Tavily search response containing:
            - results (list): List of search result dictionaries, each containing:
                - title (str): Title of the search result
                - url (str): URL of the search result
                - content (str): Snippet/summary of the content
                - raw_content (str): Full content of the page if available"""
     
    return tavily_client.search(query, 
                         max_results=5, 
                         include_raw_content=False)

@traceable
async def tavily_search_async(search_queries, tavily_topic, tavily_days):
    """
    Performs concurrent web searches using the Tavily API.

    Args:
        search_queries (List[SearchQuery]): List of search queries to process
        tavily_topic (str): Type of search to perform ('news' or 'general')
        tavily_days (int): Number of days to look back for news articles (only used when tavily_topic='news')

    Returns:
        List[dict]: List of search results from Tavily API, one per query

    Note:
        For news searches, each result will include articles from the last `tavily_days` days.
        For general searches, the time range is unrestricted.
    """
    print("----------Calling Tavily Search Async-------------")
    search_tasks = []
    for query in search_queries:
        print("Searching tavilly with -", query)
        # if tavily_topic == "news":
        #     search_tasks.append(
        #         tavily_async_client.search(
        #             query,
        #             max_results=5,
        #             include_raw_content=True,
        #             topic="news",
        #             days=tavily_days
        #         )
        #     )
        # else:
        search_tasks.append(
            tavily_async_client.search(
                query,
                max_results=1,
                include_raw_content=False,
                topic="general"
            )
        )

    # Execute all searches concurrently
    search_docs = await asyncio.gather(*search_tasks)

    return search_docs



async def tavily_search_async_retry(search_queries, tavily_topic, tavily_days, max_retries=3, backoff_factor=2):
    """
    Performs concurrent web searches using the Tavily API with error handling and retries.

    Args:
        search_queries (List[SearchQuery]): List of search queries to process.
        tavily_topic (str): Type of search to perform ('news' or 'general').
        tavily_days (int): Number of days to look back for news articles (only used when tavily_topic='news').
        max_retries (int): Maximum number of retry attempts for failed requests.
        backoff_factor (int): Multiplier for the backoff delay between retries.

    Returns:
        List[dict]: List of search results from Tavily API, one per query.
    """
    
    async def perform_search(query, retries=0):
        try:
            return await tavily_async_client.search(
                query,
                max_results=5,
                include_raw_content=False,
                topic="general"
            )
        except Exception as e:
            if retries < max_retries and hasattr(e, "status") and e.status == 504:
                # Log the retry attempt
                print(f"504 error encountered. Retrying {query} ({retries + 1}/{max_retries})...")
                await asyncio.sleep(backoff_factor ** retries)
                return await perform_search(query, retries + 1)
            else:
                print(f"Failed to fetch results for query: {query} after {retries} retries. Error: {e}")
                return None  # Or return a default value

    # Create tasks for all queries
    search_tasks = [perform_search(query) for query in search_queries]

    # Execute all tasks concurrently
    search_docs = await asyncio.gather(*search_tasks, return_exceptions=False)

    return search_docs

# Prompts

# Prompt to generate a search query to help with planning the report outline
report_planner_query_writer_instructions="""You are an expert technical writer, helping to plan a report. 

The report will be focused on the following topic:

{topic}

The report structure will follow these guidelines:

{report_organization}

Your goal is to generate {number_of_queries} search queries that will help gather comprehensive information for planning the report sections. 

The query should:

1. Be related to the topic 
2. Help satisfy the requirements specified in the report organization

Make the query specific enough to find high-quality, relevant sources while covering the breadth needed for the report structure."""

# Prompt generating the report outline
report_planner_instructions="""You are an expert technical writer, helping to plan a report.

Your goal is to generate the outline of the sections of the report. 

The overall topic of the report is:

{topic}

The report should follow this organization: 

{report_organization}

You should reflect on this information to plan the sections of the report: 

{context}

Now, generate the sections of the report. Each section should have the following fields:

- Name - Name for this section of the report.
- Description - Brief overview of the main topics and concepts to be covered in this section.
- Research - Whether to perform web research for this section of the report.
- Content - The content of the section, which you will leave blank for now.

Consider which sections require web research. For example, introduction and conclusion will not require research because they will distill information from other parts of the report."""

# Query writer instructions
query_writer_instructions="""Your goal is to generate targeted web search queries that will gather comprehensive information for writing a technical report section.

Topic for this section:
{section_topic}

When generating {number_of_queries} search queries, ensure they:
1. Cover different aspects of the topic ()
2. Include specific infrastructure concpets related to the topic
3. Look for related fields and configurations
4. Look for alert thresholds (warning and critical thresholds), SLO configurations
5. Search for both official documentation and practical implementation examples

Your queries should be:
- Specific enough to avoid generic results
- Technical enough to capture detailed implementation information
- Diverse enough to cover all aspects of the section plan
- Focused on authoritative sources (documentation, technical blogs, academic papers)
- The number of queries must match {number_of_queries}"""


# Section writer instructions
section_writer_instructions = """You are an expert technical writer crafting one section of a technical report.

Topic for this section:
{section_topic}

Guidelines for writing:

1. Technical Accuracy:
- Include specific version numbers
- Reference concrete metrics/benchmarks
- Cite official documentation
- Use technical terminology precisely

2. Length and Style:
- Strict 150-200 word limit
- No marketing language
- Technical focus
- Write in simple, clear language
- Start with your most important insight in **bold**
- Use short paragraphs (2-3 sentences max)

3. Structure:
- Use ## for section title (Markdown format)
- Only use ONE structural element IF it helps clarify your point:
  * Either a focused table comparing 2-3 key items (using Markdown table syntax)
  * Or a short list (3-5 items) using proper Markdown list syntax:
    - Use `*` or `-` for unordered lists
    - Use `1.` for ordered lists
    - Ensure proper indentation and spacing
- End with ### Sources that references the below source material formatted as:
  * List each source with title, date, and URL
  * Format: `- Title : URL`

3. Writing Approach:
- Include at least one specific example or case study
- Use concrete details over general statements
- Make every word count
- No preamble prior to creating the section content
- Focus on your single most important point

4. Use this source material to help write the section:
{context}

5. Quality Checks:
- Exactly 150-200 words (excluding title and sources)
- Careful use of only ONE structural element (table or list) and only if it helps clarify your point
- One specific example / case study
- Starts with bold insight
- No preamble prior to creating the section content
- Sources cited at end"""

final_section_writer_instructions="""You are an expert technical writer crafting a section that synthesizes information from the rest of the report.

Section to write: 
{section_topic}

Available report content:
{context}

1. Section-Specific Approach:

For Introduction:
- Use # for report title (Markdown format)
- 50-100 word limit
- Write in simple and clear language
- Focus on the core motivation for the report in 1-2 paragraphs
- Use a clear narrative arc to introduce the report
- Include NO structural elements (no lists or tables)
- No sources section needed

For Conclusion/Summary:
- Use ## for section title (Markdown format)
- 100-150 word limit
- For comparative reports:
    * Must include a focused comparison table using Markdown table syntax
    * Table should distill insights from the report
    * Keep table entries clear and concise
- For non-comparative reports: 
    * Only use ONE structural element IF it helps distill the points made in the report:
    * Either a focused table comparing items present in the report (using Markdown table syntax)
    * Or a short list using proper Markdown list syntax:
      - Use `*` or `-` for unordered lists
      - Use `1.` for ordered lists
      - Ensure proper indentation and spacing
- End with specific next steps or implications
- No sources section needed

3. Writing Approach:
- Use concrete details over general statements
- Make every word count
- Focus on your single most important point

4. Quality Checks:
- For introduction: 50-100 word limit, # for report title, no structural elements, no sources section
- For conclusion: 100-150 word limit, ## for section title, only ONE structural element at most, no sources section
- Markdown format
- Do not include word count or any preamble in your response"""


# Graph nodes

async def generate_report_plan(state: ReportState, config: RunnableConfig):
    """ Generate the report plan """
    print("-----Generate Report Plan-------")

    # Inputs
    topic = state["topic"]

    # Get configuration
    configurable = configuration.Configuration.from_runnable_config(config)
    report_structure = configurable.report_structure
    number_of_queries = configurable.number_of_queries
    tavily_topic = configurable.tavily_topic
    tavily_days = configurable.tavily_days

    # Convert JSON object to string if necessary
    if isinstance(report_structure, dict):
        report_structure = str(report_structure)

    # Generate search query
    structured_llm = gpt_4o.with_structured_output(Queries)

    # Format system instructions
    system_instructions_query = report_planner_query_writer_instructions.format(topic=topic, report_organization=report_structure, number_of_queries=number_of_queries)

    # Generate queries  
    results = structured_llm.invoke([SystemMessage(content=system_instructions_query)]+[HumanMessage(content="Generate search queries that will help with planning the sections of the report.")])
    

    # Web search
    query_list = [query.search_query for query in results.queries]

    # Search web 
    search_docs = await tavily_search_async(query_list, tavily_topic, tavily_days)
    #search_docs = tavily_search(query_list)

    # Deduplicate and format sources
    source_str = deduplicate_and_format_sources(search_docs, max_tokens_per_source=800, include_raw_content=False)

    # Format system instructions
    system_instructions_sections = report_planner_instructions.format(topic=topic, report_organization=report_structure, context=source_str)

    # Generate sections 
    structured_llm = gpt_4o.with_structured_output(Sections)
    report_sections = structured_llm.invoke([SystemMessage(content=system_instructions_sections)]+[HumanMessage(content="Generate the sections of the report. Your response must include a 'sections' field containing a list of sections. Each section must have: name, description, plan, research, and content fields.")])

    return {"sections": report_sections.sections}

def generate_queries(state: SectionState, config: RunnableConfig) -> SectionStateOutput:
    """ Generate search queries for a report section """
    print("---------_Generate Search Queries-----------------")

    # Get state 
    section = state["section"]

    # Get configuration
    configurable = configuration.Configuration.from_runnable_config(config)
    number_of_queries = configurable.number_of_queries

    # Generate queries 
    structured_llm = gpt_4o.with_structured_output(Queries)

    # Format system instructions
    system_instructions = query_writer_instructions.format(section_topic=section.description, number_of_queries=number_of_queries)

    # Generate queries  
    queries = structured_llm.invoke([SystemMessage(content=system_instructions)]+[HumanMessage(content="Generate search queries on the provided topic.")])
    
    # print(queries.queries)
    # exit(0)

    return {"search_queries": queries.queries}

async def search_web(state: SectionState, config: RunnableConfig) -> SectionStateOutput:
    """ Search the web for each query, then return a list of raw sources and a formatted string of sources."""
    print("------------Search Web -------------------")
    
    # Get state 
    search_queries = state["search_queries"]

    # Get configuration
    configurable = configuration.Configuration.from_runnable_config(config)
    tavily_topic = configurable.tavily_topic
    tavily_days = configurable.tavily_days

    # Web search
    query_list = [query.search_query for query in search_queries]
    search_docs = await tavily_search_async(query_list, tavily_topic, tavily_days)

    # Deduplicate and format sources
    #source_str = deduplicate_and_format_sources(search_docs, max_tokens_per_source=800, include_raw_content=True)
    source_str = deduplicate_and_format_sources(search_docs, max_tokens_per_source=500, include_raw_content=True)

    return {"source_str": source_str}

def write_section(state: SectionState) -> SectionStateOutput:
    """ Write a section of the report """
    print("-----------Write Section---------------")

    # Get state 
    section = state["section"]
    source_str = state["source_str"]

    # Format system instructions
    system_instructions = section_writer_instructions.format(section_title=section.name, section_topic=section.description, context=source_str)

    # Generate section  
    section_content = gpt_4o.invoke([SystemMessage(content=system_instructions)]+[HumanMessage(content="Generate a report section based on the provided sources.")])
    
    # Write content to the section object  
    section.content = section_content.content

    # Write the updated section to completed sections
    return {"completed_sections": [section]}


# Add nodes and edges 
#section_builder = StateGraph(SectionState, input=Section, output=SectionOutputState)
section_builder = StateGraph(SectionState, output=SectionOutputState)
section_builder.add_node("generate_queries", generate_queries)
section_builder.add_node("search_web", search_web)
section_builder.add_node("write_section", write_section)

section_builder.add_edge(START, "generate_queries")
section_builder.add_edge("generate_queries", "search_web")
section_builder.add_edge("search_web", "write_section")
section_builder.add_edge("write_section", END)

# g = section_builder.compile()
# g.get_graph().draw_mermaid_png(output_file_path="g.png")




def initiate_section_writing(state: ReportState):
    """ This is the "map" step when we kick off web research for some sections of the report """    
    print("--------initiate_section_writing---------------")
    # Kick off section writing in parallel via Send() API for any sections that require research
    return [
        Send("build_section_with_web_research", {"section": s.copy()}) 
        for s in state["sections"] 
        if s.research
    ]


def write_final_sections(state: SectionStateSeq):
    """Write final sections of the report."""
    print("-----------Write Final Section--------------")
    section_name = state["section_name"]
    section_description = state["section_description"]
    
    # Process the section data
    #completed_section = process_section(state["section"], state["report_sections_from_research"])
    completed_report_sections = state["report_sections_from_research"]
    system_instructions = final_section_writer_instructions.format(section_title=section_name, section_topic=section_description, context=completed_report_sections)
    section_content = gpt_4o.invoke([SystemMessage(content=system_instructions)]+[HumanMessage(content="Generate a report section based on the provided sources.")])
    
    with update_lock:

        if "completed_sections" in state:
            completed_section = state["completed_sections"] 
            completed_section.append(
                research_content = ResearchContent(
                    name=section_name,
                    content=section_content
                )
            )
        else:
            return {"completed_sections": []}
    
    return {"completed_sections": [completed_section]}




def gather_completed_sections(state: ReportState):
    """ Gather completed sections from research and format them as context for writing the final sections """    
    print("-----------gather_completed_sections--------------------")

    # List of completed sections
    completed_sections = state["completed_sections"]

    # Format completed section to str to use as context for final sections
    completed_report_sections = format_sections(completed_sections)

    return {"report_sections_from_research": completed_report_sections, "topic" : state["topic"]}

def initiate_final_section_writing(state: ReportState):
    """ Write any final sections using the Send API to parallelize the process """    

    # Kick off section writing in parallel via Send() API for any sections that do not require research
    print("initiate_final_section_writing - Begins")

    return [
        Send("write_final_sections", {"section_name": s.name,"section_description": s.description, "report_sections_from_research": state["report_sections_from_research"]}) 
        for s in state["sections"] 
        if not s.research
    ]


def compile_final_report(state: ReportState):
    """ Compile the final report """    
    print("============compile_final_report=====================")
    # Get sections
    sections = state["sections"]
    # print("+++++++++++++++++++++++")
    # print(state)
    # print("******************************")
    # print(type(state["completed_sections"]))
    # print("------------------------------")
    # print(state["completed_sections"])
    # print("+++++++++++++++++++++++")
    
    completed_sections = {s.name: s.content for s in state["completed_sections"]}

    # Update sections with completed content while maintaining original order
    for section in sections:
        if section.name in completed_sections:
            section.content = completed_sections[section.name]

    # Compile final report
    all_sections = "\n\n".join([s.content for s in sections])
    
    return {"research_answer": all_sections}


builder = StateGraph(ReportState, input=ReportStateInput, output=ReportStateOutput, config_schema=configuration.Configuration)
builder.add_node("generate_report_plan", generate_report_plan)
builder.add_node("build_section_with_web_research", section_builder.compile())
builder.add_node("gather_completed_sections", gather_completed_sections)
builder.add_node("write_final_sections", write_final_sections)


builder.add_node("compile_final_report", compile_final_report)



builder.add_edge(START, "generate_report_plan")
builder.add_conditional_edges("generate_report_plan", initiate_section_writing, ["build_section_with_web_research"])
builder.add_edge("build_section_with_web_research", "gather_completed_sections")

builder.add_conditional_edges("gather_completed_sections", initiate_final_section_writing, ["write_final_sections"])

# builder.add_edge("write_final_sections", END)
builder.add_edge("write_final_sections", "compile_final_report")
builder.add_edge("compile_final_report", END)



gr_researcher = builder

def get_report(state: dict):
    async def obs_researcher(topic: str):
        gr = gr_researcher.compile()
        report = await gr.ainvoke({
            "topic": topic
        })
        return {
            "research_answer": report
        }
    
    # Create and run an event loop to execute the asynchronous researcher
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        fr = loop.run_until_complete(obs_researcher(state["topic"]))
    finally:
        loop.close()
    return fr

# if __name__ == "__main__":
#     state = {"topic": "Oracle tablespace data file size alert configurations"}
#     res = get_report(state)  # Synchronous call
#     print(res)
