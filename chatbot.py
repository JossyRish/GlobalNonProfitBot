# --- chatbot.py ---
import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

# Debug: See which file is being loaded in deployment
print("🔎 Loaded chatbot.py from:", __file__)

# -------------------------------------------------------
# 1️⃣ Load API Key
# -------------------------------------------------------
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY not found. Please set it in your environment variables.")

# -------------------------------------------------------
# 2️⃣ Load Embeddings + Vectorstore
# -------------------------------------------------------
persist_directory = "chroma_store"
embeddings = OpenAIEmbeddings()

vectorstore = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings
)

# Create retriever (fetches relevant chunks)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# -------------------------------------------------------
# 3️⃣ Load LLM
# -------------------------------------------------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# -------------------------------------------------------
# 4️⃣ Powerful Prompt with Smart Fallback
# -------------------------------------------------------
prompt = ChatPromptTemplate.from_template("""
You are a helpful, intelligent AI assistant inside the Global Nonprofit Bot.

You have two information sources:
1. The provided document context (PDF data).
2. Your general knowledge as an AI language model.

Here is how you MUST answer:

---

### 📌 RULE 1 — If the document context contains relevant information
Use it FIRST.  
Quote or reference the PDF content when appropriate.

### 📌 RULE 2 — If the context does NOT contain the answer:
Fallback to your general knowledge.
Answer helpfully and clearly, like ChatGPT would.

### 📌 RULE 3 — If the user asks about a person who might be a private individual:
Do NOT invent or guess.
Say:
"That name may refer to many different people, and I don't have enough information to identify who you mean."

### 📌 RULE 4 — If the user asks about a public figure or well-known topic:
Answer confidently using your general knowledge.

### 📌 RULE 5 — Always be helpful, clear, and friendly.

---

<context>
{context}
</context>

Question: {input}

Answer:
""")

# -------------------------------------------------------
# 5️⃣ Build Retrieval Chain
# -------------------------------------------------------
document_chain = create_stuff_documents_chain(llm, prompt)
qa_chain = create_retrieval_chain(retriever, document_chain)

# -------------------------------------------------------
# 6️⃣ Query Function for Streamlit
# -------------------------------------------------------
def ask_bot(query: str) -> str:
    try:
        result = qa_chain.invoke({"input": query})
        return result.get("answer", "⚠️ No answer returned.")
    except Exception as e:
        return f"⚠️ Error: {e}"

# -------------------------------------------------------
# 7️⃣ CLI Mode (optional)
# -------------------------------------------------------
if __name__ == "__main__":
    print("\n💬 Global Nonprofit Bot Ready!")
    print("Type your question below, or 'exit' to quit.\n")
    while True:
        query = input("You: ")
        if query.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break
        print(f"🤖 Bot: {ask_bot(query)}\n")
