from langchain_core.tools import tool


@tool
def mock_lead_capture(name: str, email: str, platform: str) -> str:
    """Capture a qualified lead for AutoStream. Requires name, email, and platform."""
    print(f"\n✅ Lead captured successfully: {name}, {email}, {platform}\n")
    return f"Lead captured successfully! Name: {name}, Email: {email}, Platform: {platform}"
