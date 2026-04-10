import time
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI

from tools import mock_lead_capture
from prompts import SYSTEM_PROMPT
from rag import build_vector_store, get_retriever, retrieve_context


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def create_agent(api_key: str):

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        google_api_key=api_key
    )

    tools = [mock_lead_capture]
    llm_with_tools = llm.bind_tools(tools)

    print("Building knowledge base...")
    vector_store = build_vector_store(api_key)
    retriever = get_retriever(vector_store)
    print("Knowledge base ready!\n")

    def agent_node(state: AgentState):
        messages = state["messages"]

        # Get the latest user message for RAG retrieval
        latest_user_msg = ""
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                latest_user_msg = msg.content
                break

        print("[DEBUG] Fetching RAG context for:", latest_user_msg)
        # Retrieve relevant context from knowledge base
        context = retrieve_context(retriever, latest_user_msg)
        print("[DEBUG] RAG context fetched.")

        # Build the system message with RAG context injected
        system_msg = SystemMessage(content=SYSTEM_PROMPT.format(context=context))

        print("[DEBUG] Invoking Gemini model...")
        # Invoke LLM with retry logic for rate limits
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = llm_with_tools.invoke([system_msg] + list(messages))
                return {"messages": [response]}
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    wait_time = 15 * (attempt + 1)
                    print(f"\n⏳ Rate limited. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise e

        # Final attempt without catch
        response = llm_with_tools.invoke([system_msg] + list(messages))
        return {"messages": [response]}

    workflow = StateGraph(AgentState)

    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")

    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory)

    return graph
