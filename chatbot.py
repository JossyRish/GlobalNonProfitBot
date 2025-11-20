# --- chatbot.py ---
import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

# Load API key
print("🔐 OPENAI_API_KEY exists:", "OPENAI_API_KEY" in os.environ)

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY not found. Please set it in your environment variables.")

# Vectorstore / embeddings
persist_directory = "chroma_store"
embeddings = OpenAIEmbeddings()

vectorstore = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings
)

# Retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# Prompt
prompt = ChatPromptTemplate.from_template("""
Use the following context to answer the user question.

<context>
{context}
</context>

Question: {input}

Answer:
""")

# Retrieval chain
document_chain = create_stuff_documents_chain(llm, prompt)
qa_chain = create_retrieval_chain(retriever, document_chain)

def ask_bot(query: str) -> str:
    try:
        result = qa_chain.invoke({"input": query})
        return result.get("answer", "⚠️ No answer returned.")
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
