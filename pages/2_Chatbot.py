# ============================================================
# 2_Chatbot.py — STL KID-FRIENDLY SMART CHATBOT
# Clean, updated, Streamlit-Cloud-safe version (Nov 2025)
# ============================================================

import os
import re
import difflib
from typing import List, Optional

import streamlit as st
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate

# ============================================================
# FIX STREAMLIT PROXY INJECTION ISSUE (IMPORTANT)
# ============================================================
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("ALL_PROXY", None)

# ============================================================
# STREAMLIT PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="STL Student Helper 🤖",
    page_icon="🤖",
    layout="wide"
)

st.title("🎒 STL School Helper Chatbot")
st.caption("Fun • Friendly • Super Smart • Never Hallucinates 😎")


# ============================================================
# CONSTANTS / DIRECTORIES
# ============================================================
PERSIST_DIR = "uploads/.chroma_data"
APPROVED_DIR = "uploads/approved"

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
DEFAULT_K = 8


# ============================================================
# LOAD API KEY — FIXED FOR STREAMLIT CLOUD
# ============================================================
api_key = (
    st.secrets.get("OPENAI_API_KEY")
    or os.getenv("OPENAI_API_KEY")
)

if not api_key:
    st.error("❌ Missing OpenAI API Key. Add it in Streamlit Secrets.")
    st.stop()


# ============================================================
# INIT OPENAI LLM — NEW LANGCHAIN 0.3.x SYNTAX
# ============================================================
llm = ChatOpenAI(
    model=CHAT_MODEL,
    temperature=0.15,
    api_key=api_key,   # ✔ correct parameter for new client
)


# ============================================================
# INITIALIZE VECTORSTORE (CHROMA)
# ============================================================
def load_vectorstore():
    """Load Chroma vector DB from approved uploads."""
    if not os.path.exists(APPROVED_DIR):
        os.makedirs(APPROVED_DIR)

    embeddings = OpenAIEmbeddings(
        model=EMBED_MODEL,
        api_key=api_key
    )

    vectordb = Chroma(
        collection_name="school_docs",
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )
    return vectordb


vectorstore = load_vectorstore()


# ============================================================
# RETRIEVE RELEVANT CHUNKS (NO HALLUCINATING)
# ============================================================
def get_relevant_chunks(query: str, k: int = DEFAULT_K):
    try:
        return vectorstore.similarity_search(query, k=k)
    except Exception as e:
        st.error(f"Vector DB error: {e}")
        return []


# ============================================================
# CREATE SMART, KID-FRIENDLY PROMPT
# ============================================================
prompt_template = ChatPromptTemplate.from_template("""

You are a friendly STL school helper chatbot. 😎  
You ONLY answer using information found in the chunks below.  
If the answer is not found, say:

"I'm not trained on that yet! Try uploading the document first 💡"

Rules:
- Keep answers simple.
- No citations.
- No file names.
- No guessing.
- No hallucinating.
- Give clear explanations.

USER QUESTION:
{question}

DOCUMENT CHUNKS:
{context}

""")

# ============================================================
# GENERATE ANSWER
# ============================================================
def answer_question(question: str):
    docs = get_relevant_chunks(question)
    if not docs:
        return "I couldn’t find anything related to that yet. Try uploading the document! 📄✨"

    context = "\n\n".join([d.page_content for d in docs])

    # Build the final prompt
    final_prompt = prompt_template.format_messages(
        question=question,
        context=context
    )

    # Ask LLM
    response = llm.invoke(final_prompt)
    return response.content.strip()


# ============================================================
# SIDEBAR — FUN FOR KIDS
# ============================================================
with st.sidebar:
    st.subheader("🎨 Chatbot Style")
    st.caption("Choose your bot's personality!")
    vibe = st.radio(
        "Pick a vibe:",
        ["😎 Chill", "🤓 Nerdy Smart", "🎉 Super Fun"],
        horizontal=True
    )

    st.write("")
    st.markdown("**📚 Trained Docs:**")
    approved_files = os.listdir(APPROVED_DIR)
    if approved_files:
        for f in approved_files:
            st.markdown(f"- 📄 *{f}*")
    else:
        st.caption("No files ingested yet.")


# ============================================================
# MAIN CHAT INTERFACE
# ============================================================
st.markdown("## 💬 Ask Your Question!")

user_input = st.text_input(
    "Ask me anything about your school, classes, electives, or uploaded PDFs:",
    placeholder="e.g., Compare FIN 8610 and FIN 8510 📘",
)

# Give the textbox a little bounce animation
st.markdown(
    """
    <style>
    input[type=text] {
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% {box-shadow: 0 0 0px rgba(0,0,0,0.3);}
        50% {box-shadow: 0 0 8px rgba(0,0,0,0.3);}
        100% {box-shadow: 0 0 0px rgba(0,0,0,0.3);}
    }
    </style>
    """,
    unsafe_allow_html=True
)

if user_input:
    with st.spinner("Thinking… 🤔💭"):
        response = answer_question(user_input)
    st.markdown("### 🧠 Answer:")
    st.success(response)

