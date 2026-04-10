"""
AutoStream – LangGraph Agent

Implements the core agentic workflow using LangGraph:
- Agent node: LLM reasoning with RAG context injection
- Tool node: Executes mock_lead_capture when triggered
- Conditional routing: Routes between agent ↔ tools ↔ END
- MemorySaver: Persists conversation state across turns
"""

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


# ─────────────────────────────────────────────
# 1. Define Agent State
# ─────────────────────────────────────────────
class AgentState(TypedDict):
    """State shared across all nodes in the graph.

    'messages' stores the full conversation history.
    The add_messages reducer appends new messages instead of overwriting.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]


# ─────────────────────────────────────────────
# 2. Build the Agent Graph
# ─────────────────────────────────────────────
def create_agent():
    """Create and compile the LangGraph agent with RAG and tool calling."""

    # --- Initialize LLM with tools ---
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
    )

    tools = [mock_lead_capture]
    llm_with_tools = llm.bind_tools(tools)

    # --- Initialize RAG ---
    print("📚 Building knowledge base...")
    vector_store = build_vector_store()
    retriever = get_retriever(vector_store)
    print("✅ Knowledge base ready!\n")

    # --- Define Agent Node ---
    def agent_node(state: AgentState):
        """The 'brain' of the agent.

        1. Extracts the latest user message
        2. Retrieves relevant RAG context
        3. Builds system prompt with context
        4. Invokes the LLM with full conversation history
        """
        messages = state["messages"]

        # Get the latest user message for RAG retrieval
        latest_user_msg = ""
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                latest_user_msg = msg.content
                break

        # Retrieve relevant context from knowledge base
        context = retrieve_context(retriever, latest_user_msg)

        # Build the system message with RAG context injected
        system_msg = SystemMessage(content=SYSTEM_PROMPT.format(context=context))

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

    # --- Build the State Graph ---
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))

    # Add edges
    workflow.add_edge(START, "agent")

    # Conditional edge: if LLM requested a tool call → go to tools, else → END
    workflow.add_conditional_edges("agent", tools_condition)

    # After tool execution, return to agent for follow-up response
    workflow.add_edge("tools", "agent")

    # Compile with memory checkpointer for cross-turn persistence
    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory)

    return graph
