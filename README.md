# Social-to-Lead Agentic Workflow

An AI agent for AutoStream that converts social media conversations into qualified business leads. It implements intent detection, answers product questions using a local knowledge base (RAG), and handles lead capture via mock API tool execution.

## Features

- **Intent Detection** – LLM-powered classification of user intent (greeting, product inquiry, high-intent lead)
- **RAG-Powered Knowledge Retrieval** – Answers pricing, feature, and policy questions using a FAISS vector store built from a local knowledge base
- **Lead Capture Tool** – Collects name, email, and creator platform before executing `mock_lead_capture()` via LangGraph tool calling
- **Conversation Memory** – Retains full context across 5–6+ turns using LangGraph's `MemorySaver` checkpointer

## Project Structure

```
AutoStream/
├── knowledge_base.md      # Product info (pricing, features, policies, FAQs)
├── rag.py                 # RAG pipeline: load → split → embed → retrieve (FAISS)
├── tools.py               # Lead capture tool (@tool decorated)
├── prompts.py             # System prompt with intent classification rules
├── agent.py               # LangGraph StateGraph (agent node ↔ tool node)
├── main.py                # CLI entry point (interactive conversation loop)
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
└── README.md              # This file
```

## How to Run Locally

### Prerequisites
- Python 3.9+
- A free Google AI Studio API key ([Get one here](https://aistudio.google.com/apikey))

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/AutoStream.git
cd AutoStream

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 5. Run the agent
python main.py
```

### Example Conversation

```
🧑 You: Hi, tell me about your pricing.
🤖 Ava: Hello! We have two plans — Basic at $29/month (10 videos, 720p) and Pro at $79/month (unlimited videos, 4K, AI captions)...

🧑 You: That sounds good, I want to try the Pro plan for my YouTube channel.
🤖 Ava: Great choice! I'd love to get you started. Could you share your name?

🧑 You: John Doe
🤖 Ava: Thanks, John! And what's your email address?

🧑 You: john@example.com
✅ Lead captured successfully: John Doe, john@example.com, YouTube
🤖 Ava: You're all set! Our team will reach out shortly to help you get started with the Pro plan.
```

## Architecture Explanation

Here's a quick breakdown of how things are structured under the hood (about 200 words).

I decided to go with **LangGraph** instead of AutoGen or raw LangChain because it's much better suited for routing logic. A lead capture agent needs to strictly control when it's just chatting versus when it's actively pulling user data. LangGraph lets us define this as a state machine. We have an "Agent Node" that does the reasoning and intent detection, and a separate "Tool Node" that handles the actual function execution (`mock_lead_capture`). We can easily set conditional edges so the tool node only triggers when the LLM explicitly requests it.

For **State Management**, I didn't want to overcomplicate things with external databases. LangGraph has a built-in `MemorySaver` checkpointer that I'm using alongside a `TypedDict` for the agent's state. It basically intercepts every message in the conversation and appends it to a message history array. By passing a `thread_id` in the run config, the agent remembers the entire context of the chat—meaning it won't ask for a user's name if they already provided it two turns ago. 

Finally, the RAG setup is just a simple local FAISS vector store that gets queried via Google Embeddings before each LLM call.

## WhatsApp Deployment

To integrate this agent with WhatsApp using webhooks:

### Architecture

```
User (WhatsApp) → Meta Cloud API → Webhook Server → LangGraph Agent → Response → Meta Cloud API → User
```

### Implementation Steps

1. **Register a WhatsApp Business Account** on the [Meta Developer Portal](https://developers.facebook.com/) and set up a WhatsApp Business API app.

2. **Set up a Webhook Server** (e.g., using Flask or FastAPI) that:
   - Receives incoming messages via POST requests from Meta's Cloud API
   - Validates the webhook signature using the app secret
   - Extracts the user's message and phone number from the payload

3. **Connect to the LangGraph Agent**:
   - Use the phone number as the `thread_id` in the LangGraph config — this gives each WhatsApp user their own persistent conversation memory
   - Pass the incoming message as a `HumanMessage` to `agent.invoke()`
   - Extract the AI response from the returned state

4. **Send the Response** back via the WhatsApp Cloud API's `/messages` endpoint using the user's phone number.

5. **Deploy** the webhook server to a cloud service (AWS, GCP, Railway, etc.) with HTTPS enabled and register the public URL as the webhook callback in the Meta Developer Portal.

### Key Considerations
- **Session Management**: LangGraph's `MemorySaver` naturally handles multi-turn state per `thread_id` (phone number), so no additional session logic is needed.
- **Rate Limiting**: Implement rate limiting to handle message volume within WhatsApp API limits.
- **Security**: Validate webhook signatures and sanitize user inputs before passing to the agent.

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.9+ |
| Framework | LangGraph (LangChain) |
| LLM | Google Gemini 2.0 Flash |
| Embeddings | Google Embedding Model (`embedding-001`) |
| Vector Store | FAISS (local, in-memory) |
| State Management | LangGraph MemorySaver |

## License

This project was built as part of the ServiceHive/Inflx ML Intern assignment.