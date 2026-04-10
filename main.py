"""
AutoStream – CLI Entry Point

Interactive conversation loop that runs the LangGraph agent.
Supports multi-turn conversations with persistent memory.
"""

import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from agent import create_agent


def main():
    # Load environment variables (.env file with GOOGLE_API_KEY)
    load_dotenv(override=True)

    # Verify API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not found.")
        print("   Please set it in a .env file or as an environment variable.")
        print("   Get a free key at: https://aistudio.google.com/apikey")
        return

    # Build the agent
    print("=" * 50)
    print("🚀 AutoStream AI Agent")
    print("=" * 50)

    api_key = os.getenv("GOOGLE_API_KEY")
    agent = create_agent(api_key)

    # Configuration for memory persistence (same thread_id = same conversation)
    config = {"configurable": {"thread_id": "autostream-session-1"}}

    print("Type 'quit' or 'exit' to end the conversation.\n")
    print("─" * 50)

    while True:
        try:
            user_input = input("\n🧑 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit"):
            print("\n👋 Thanks for chatting with AutoStream! Goodbye!")
            break

        # Invoke the agent with the user's message
        response = agent.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config
        )

        # Extract and display the agent's response
        ai_message = response["messages"][-1]
        content = ai_message.content
        
        # Sometime LangChain returns Gemini responses as a stringified list of dicts
        if isinstance(content, str) and content.startswith("[{") and "'text':" in content:
            import ast
            try:
                parsed_list = ast.literal_eval(content)
                text_parts = [block["text"] for block in parsed_list if isinstance(block, dict) and "text" in block]
                content = "\n".join(text_parts)
            except Exception:
                pass
        elif isinstance(content, list):
            # If it's a raw python list
            text_parts = [block.get("text", "") for block in content if isinstance(block, dict)]
            content = "\n".join(text_parts)

        print(f"\n🤖 Ava: {content}")


if __name__ == "__main__":
    main()