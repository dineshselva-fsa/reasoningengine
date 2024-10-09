
from langchain.agents.format_scratchpad.tools import format_to_tool_messages
from langchain.memory import ChatMessageHistory
from langchain_core import prompts
from vertexai.preview import reasoning_engines

from config_model import LLM_MODEL
from config_project import PROJECT_ID, PROJECT_LOCATION, DATASTORE_ID, DATASTORE_LOCATION, TXT_DATASTORE_ID, TXT_DATASTORE_LOCATION, STORAGE_BUCKET
from prompts import industries_prompt, customers_prompt, services_prompt, mergers_prompt, lawsuits_prompt

def agent_web_search(search_query: str) -> str:
  """
  Perform a search through a company's website and return the results.

  This function uses the Vertex Data store which has HTML files generated from crawling through a company's website.
  """

  from langchain_google_community import VertexAISearchRetriever

  retriever = VertexAISearchRetriever(
      project_id=PROJECT_ID,
      data_store_id=DATASTORE_ID,
      location_id=DATASTORE_LOCATION,
      engine_data_type=1,
      max_documents=10
  )

  result = str(retriever.invoke(search_query))
  return result

print (agent_web_search("CGMH"))

# Define prompt template
prompt = {
    "history": lambda x: x["history"],
    "input": lambda x: x["input"],
    "agent_scratchpad": (lambda x: format_to_tool_messages(x["intermediate_steps"])),
} | prompts.ChatPromptTemplate.from_messages(
    [
        prompts.MessagesPlaceholder(variable_name="history"),
        ("user", "{input}"),
        prompts.MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# Initialize session history
store = {}


def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

agent = reasoning_engines.LangchainAgent(
    prompt=prompt,
    model=LLM_MODEL,
    enable_tracing=True,
    chat_history=get_session_history,
    model_kwargs={"temperature": 0},
    tools=[agent_web_search],
    agent_executor_kwargs={"return_intermediate_steps": True},
)

response = agent.query(
    input=industries_prompt,
    config={"configurable": {"session_id": "demo"}},
)

print(response["output"])
