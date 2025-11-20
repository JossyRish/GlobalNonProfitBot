# --- chatbot.py ---
import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains.retrieval_qa.base import RetrievalQA

# Load API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY not found. Add it in Streamlit Secrets.")

# Initialize Chroma Vector Store
persist_directory = "chroma_store"
embeddings = OpenAIEmbeddings()

vectorstore = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.3
)

# Retrieval QA Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

def ask_bot(query: str):
    """Simple wrapper for Streamlit UI"""
    result = qa_chain({"query": query})
    return result["result"]
