"""
AutoStream – Lead Capture Tool

Defines the mock_lead_capture tool for the LangGraph agent.
The tool is called ONLY after the agent has collected all three required fields:
name, email, and creator platform.
"""

from langchain_core.tools import tool


@tool
def mock_lead_capture(name: str, email: str, platform: str) -> str:
    """Capture a qualified lead for AutoStream.

    Call this tool ONLY after you have collected ALL THREE of the following
    from the user in the conversation:
    1. name - The user's full name
    2. email - The user's email address
    3. platform - The creator platform they use (e.g., YouTube, Instagram, TikTok)

    Do NOT call this tool if any of the three values are missing or unknown.
    """
    print(f"\n✅ Lead captured successfully: {name}, {email}, {platform}\n")
    return f"Lead captured successfully! Name: {name}, Email: {email}, Platform: {platform}"
