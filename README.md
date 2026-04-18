# LeadGraph: AI-Powered Social-to-Lead Agent

An intelligent conversational AI agent built to seamlessly convert social media interactions into qualified business leads. It leverages **LangGraph** for powerful stateful routing, **Retrieval-Augmented Generation (RAG)** to answer product questions accurately, and **tool calling** for structured lead capture.

## 🚀 Features

- **Dynamic Intent Detection** – An LLM-powered engine that naturally classifies user intent across states (greeting, product inquiry, high-intent lead).
- **RAG-Powered Knowledge Retrieval** – Intelligently answers pricing, feature, and policy questions using a local in-memory FAISS vector store.
- **Automated Lead Capture** – Securely collects crucial user details (Name, Email, Platform) before executing a lead generation webhook/tool.
- **Persistent Conversational Memory** – Retains deep context across multiple conversation turns using LangGraph's robust checkpointer, ensuring seamless and natural follow-up questions.

## 📂 Project Structure

```text
LeadGraph/
├── knowledge_base.md      # Product knowledge (pricing, features, FAQs) for RAG
├── rag.py                 # RAG pipeline: loads, splits, embeds, and retrieves context
├── tools.py               # Functional tools (Lead capture execution)
├── prompts.py             # System prompts and intent classification logic
├── agent.py               # LangGraph StateGraph (Routing logic between bot and tools)
├── main.py                # Interactive CLI entry point
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
└── README.md              # Project documentation
```

## 🛠️ How to Run Locally

### Prerequisites
- Python 3.9+
- A valid Google Gemini AI Studio API key ([Get one for free here](https://aistudio.google.com/apikey))

### Setup & Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/LeadGraph.git
cd LeadGraph

# 2. Create and activate a virtual environment
python -m venv venv
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 3. Install required dependencies
pip install -r requirements.txt

# 4. Configure your environment variables
cp .env.example .env
# Open .env and insert your GOOGLE_API_KEY

# 5. Start the conversation agent
python main.py
```

### 💬 Example Interaction

```text
🧑 You: Hi, tell me about your pricing plans.
🤖 Ava: Hello! We offer two distinct plans. The Basic plan is $29/month (10 videos, 720p). Our Pro plan is $79/month and includes unlimited videos at 4K resolution along with AI captions.

🧑 You: The Pro plan sounds perfect for my YouTube channel.
🤖 Ava: That's a great choice! I'd love to help you get started. Could I please get your name?

🧑 You: John Doe
🤖 Ava: Thanks, John! And what's the best email address to reach you at?

🧑 You: john@example.com
✅ [System] Lead captured securely: John Doe, john@example.com, YouTube
🤖 Ava: You're all set! A member of our team will reach out shortly to help finalize your Pro plan access.
```

## 🧠 System Architecture

The core of this project uses **LangGraph** to build a highly controllable state machine, rather than standard reactive chains. A lead capture agent requires strict routing—knowing exactly when to converse naturally vs. when it's actively extracting data. 

* **State Machine Logic**: An "Agent Node" processes intent detection and general chat, while a "Tool Node" strictly handles function invocation (e.g., `mock_lead_capture`). Conditional edges ensure data parsing tools are only fired when the LLM deems a user has provided all necessary parameters.
* **State Management**: Rather than relying on external databases for session state during prototyping, we lean on LangGraph's built-in `MemorySaver` alongside `TypedDict`. By passing a dynamic `thread_id`, the agent seamlessly manages conversation histories.
* **Retrieval-Augmented Generation**: Powered by Google Embeddings, user queries are semantically searched against a local FAISS vector store before the LLM generates a response, eliminating hallucinations regarding product constraints.

## 📱 WhatsApp Webhook Integration Guide

To expand this to platforms like WhatsApp:

1. **Meta Developer Portal**: Register a WhatsApp Business Account and set up the Cloud API.
2. **Webhook Listener**: Set up a Flask/FastAPI server to receive POST requests from Meta.
3. **Session Routing**: Pass the incoming WhatsApp phone number into the LangGraph config as the `thread_id`. This grants every unique user their own conversational state.
4. **Agent Invocation**: Send the incoming text as a `HumanMessage(content=...)` to the agent.
5. **Response**: Return the final agent output string back to Meta's `/messages` API.

## 💻 Tech Stack

| Component | Technology Used |
|---|---|
| **Language** | Python 3.9+ |
| **Orchestration Framework** | LangGraph / LangChain |
| **LLM** | Google Gemini 2.0 Flash |
| **Embeddings** | Google Embedding Model (`embedding-001`) |
| **Vector Store** | FAISS (In-memory) |
| **Memory** | LangGraph `MemorySaver` |

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
