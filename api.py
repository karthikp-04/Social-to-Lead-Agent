import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from agent import create_agent

load_dotenv()

# Initialize FastAPI App
app = FastAPI(title="AutoStream Agent API")

# Setup CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the LangGraph agent once
agent = None
try:
    if os.getenv("GOOGLE_API_KEY"):
        agent = create_agent()
except Exception as e:
    print(f"Error initializing agent: {e}")

# Data Models
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default-session"

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    global agent
    if not agent:
        # Try initializing again if it failed before (e.g. late loaded env)
        if os.getenv("GOOGLE_API_KEY"):
             agent = create_agent()
        if not agent:
            raise HTTPException(status_code=500, detail="Agent not initialized (check GOOGLE_API_KEY).")
    
    config = {"configurable": {"thread_id": request.session_id}}
    
    try:
        # Invoke LangGraph agent
        result = agent.invoke(
            {"messages": [HumanMessage(content=request.message)]},
            config=config
        )
        
        # Extract response text
        ai_message = result["messages"][-1]
        
        # Gemini often returns a list of content blocks
        content = ai_message.content
        if isinstance(content, list):
            text_parts = [block["text"] for block in content if isinstance(block, dict) and "text" in block]
            content = "\n".join(text_parts)
            
        return ChatResponse(response=content, session_id=request.session_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "agent_ready": agent is not None}

if __name__ == "__main__":
    import uvicorn
    # Make sure to run this via standard uvicorn command for auto-reload, but allowing script execution
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
