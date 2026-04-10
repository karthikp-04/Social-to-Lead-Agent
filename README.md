# AutoStream – Social-to-Lead Agentic Workflow

A conversational AI agent for **AutoStream**, a fictional SaaS product that provides automated video editing tools for content creators. The agent identifies user intent, answers product questions using RAG, and captures qualified leads through natural conversation.

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

## Architecture Explanation (~200 words)

This project uses **LangGraph** as the orchestration framework because it provides explicit, graph-based control over the agent's workflow — unlike simple chain-based approaches, LangGraph lets us define distinct nodes (agent reasoning, tool execution) with conditional routing between them, making the intent → RAG → lead capture flow transparent and debuggable.

The architecture is built around a **StateGraph** with two nodes:

1. **Agent Node** – Invokes Google's Gemini 2.0 Flash LLM with the full conversation history and dynamically retrieved RAG context. The system prompt instructs the LLM to classify intent and follow a strict lead qualification protocol.

2. **Tool Node** – Uses LangGraph's pre-built `ToolNode` to execute `mock_lead_capture()` only when the LLM explicitly requests it (after collecting all three required fields).

**State management** uses LangGraph's `MemorySaver` checkpointer with the `add_messages` reducer. Each conversation turn appends to the message history rather than overwriting it, preserving full context across 5-6+ turns. A `thread_id` in the config ties all turns to the same session.

**RAG** is implemented using FAISS as a local vector store with Google's embedding model. The knowledge base (`knowledge_base.md`) is split into semantic chunks and embedded at startup, enabling accurate retrieval of pricing, features, and policy information.

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