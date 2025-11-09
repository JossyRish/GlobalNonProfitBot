# --- chatbot.py ---
import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA

# 1️⃣ Load API key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY not found. Please set it in your environment variables.")

# 2️⃣ Load stored embeddings (vector database)
persist_directory = "chroma_store"
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings
)

# 3️⃣ Create a retriever to fetch relevant chunks
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 4️⃣ Initialize the GPT model
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

# 5️⃣ Build the Retrieval QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

def ask_bot(query: str) -> str:
    """Run a single query through the chatbot and return the response text."""
    try:
        result = qa_chain({"query": query})
        return result["result"]
    except Exception as e:
        return f"⚠️ Error: {e}"

if __name__ == "__main__":
    print("\n💬 RKF Chatbot Ready!")
    print("Type your question below, or 'exit' to quit.\n")
    while True:
        query = input("You: ")
        if query.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break
        print(f"🤖 Chatbot: {ask_bot(query)}\n")
