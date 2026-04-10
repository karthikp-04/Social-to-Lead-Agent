import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def build_vector_store(api_key: str):

    # Get the directory where this script lives
    base_dir = os.path.dirname(os.path.abspath(__file__))
    kb_path = os.path.join(base_dir, "knowledge_base.md")

    # Load the knowledge base document
    loader = TextLoader(kb_path, encoding="utf-8")
    documents = loader.load()

    # Split into smaller chunks for better retrieval
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "]
    )
    chunks = text_splitter.split_documents(documents)

    # Create embeddings and build FAISS index
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key
    )
    vector_store = FAISS.from_documents(chunks, embeddings)

    return vector_store


def get_retriever(vector_store, k=3):
    """Return a retriever that fetches the top-k most relevant chunks."""
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )


def retrieve_context(retriever, query: str) -> str:
    """Retrieve relevant context from the knowledge base for a given query."""
    docs = retriever.invoke(query)
    if not docs:
        return "No relevant product information found."

    context_parts = []
    for i, doc in enumerate(docs, 1):
        context_parts.append(f"[Source {i}]\n{doc.page_content}")

    return "\n\n".join(context_parts)
