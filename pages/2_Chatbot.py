"""
2_chatbot.py
============

🔥 STL FOR STL KID-FRIENDLY CHATBOT — SMART HYBRID + AUTO-LEARNING 🎉🤖  
---------------------------------------------------------------------

This chatbot:
    • Learns instantly from PDFs you upload  
    • Answers questions about electives, schedules, programs, or ANY doc  
    • Detects question type (course? hybrid? program? random doc?)  
    • NEVER hallucinates — only answers from the text it was trained on  
    • If it can’t answer, it tells the kid *exactly* why and what to do  
    • Fun kid/teen vibe 😎

The bot auto-detects:
    • course codes  
    • module/week numbers  
    • subject areas (FIN, MKT, etc. if present)  

The bot *never* shows:
    • sources  
    • filenames  
    • citations  
"""
import os
import streamlit as st

# ============================================================
# 🔐 LOAD OPENAI API KEY FIRST — before ANY other imports
# ============================================================

# ============================================================
# 1) Load OpenAI key BEFORE importing LangChain
# ============================================================

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OPENAI_API_KEY is missing. Set it in Streamlit Secrets.")
    st.stop()

os.environ["OPENAI_API_KEY"] = api_key

# ============================================================
# AFTER KEY: Now safe to import LangChain
# ============================================================

import re
import difflib
from typing import List, Tuple, Optional
import random
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate


# ============================================================
# CONFIG
# ============================================================

PERSIST_DIR = "uploads/.chroma_data"
APPROVED_DIR = "uploads/approved"

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
DEFAULT_K = 8

# ✅ Cloud-safe: make sure folders exist
os.makedirs(PERSIST_DIR, exist_ok=True)
os.makedirs(APPROVED_DIR, exist_ok=True)


# ============================================================
# STREAMLIT PAGE SETUP
# ============================================================

st.set_page_config(page_title="STL For STL Kid Chatbot", page_icon="🤖")


# ============================================================
# LOAD EMBEDDINGS + CHROMA
# ============================================================

@st.cache_resource
def get_vectordb():
    embeddings = OpenAIEmbeddings(model=EMBED_MODEL)
    return Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )

try:
    vectordb = get_vectordb()
except Exception:
    vectordb = None


llm = ChatOpenAI(model=CHAT_MODEL, temperature=0.15)


# ============================================================
# AUTO-LEARNING HELPERS
# ============================================================

def get_all_chunks() -> List[str]:
    if vectordb is None:
        return []
    try:
        payload = vectordb.get(include=["documents"])
        return payload.get("documents", []) if payload else []
    except Exception:
        return []


ALL_CHUNKS = get_all_chunks()


def auto_detect_identifiers(chunks: List[str]) -> Tuple[set, set]:
    identifiers = set()
    prefixes = set()

    code_pattern = re.compile(r"\b([A-Z]{2,5})\s?-?\s?(\d{3,4}[A-Z]?)\b")

    section_pattern = re.compile(
        r"\b(Module|Unit|Week|Section|Chapter|Lesson)\s+([A-Z0-9]{1,3})\b",
        re.IGNORECASE
    )

    for text in chunks:
        for m in code_pattern.findall(text.upper()):
            prefix, num = m
            if prefix.isalpha() and len(prefix) <= 5:
                prefixes.add(prefix)
                identifiers.add(f"{prefix} {num}")

        for m in section_pattern.findall(text):
            label, val = m
            identifiers.add(f"{label.title()} {val}")

    return identifiers, prefixes


IDENTIFIERS, PREFIXES = auto_detect_identifiers(ALL_CHUNKS)


def build_alias_map(prefixes: set) -> dict:
    alias_map = {}
    possible = {
        "finance": "FIN",
        "marketing": "MKT",
        "accounting": "ACCT",
        "operations": "OPM",
        "analytics": "MEC",
        "strategy": "STR",
        "management": "MGT",
    }
    for word, pref in possible.items():
        if pref in prefixes:
            alias_map[word] = pref
    return alias_map


ALIAS_MAP = build_alias_map(PREFIXES)


# ============================================================
# DYNAMIC HEADER (ONLY SHOW REAL EXAMPLES)
# ============================================================

def build_dynamic_examples() -> str:
    course_like = [x for x in IDENTIFIERS if any(ch.isdigit() for ch in x)]
    module_like = [x for x in IDENTIFIERS if any(k in x.lower() for k in ["module", "unit", "week", "section", "chapter", "lesson"])]

    lines = []

    if course_like:
        picks = random.sample(course_like, min(2, len(course_like)))
        for p in picks:
            lines.append(f"• “What is {p}?”")
        if len(course_like) >= 2:
            a, b = random.sample(course_like, 2)
            lines.append(f"• “Compare {a} and {b}”")

    if module_like:
        p = random.choice(module_like)
        lines.append(f"• “Summarize {p} for me”")

    # Always-safe general examples
    lines += [
        "• “Summarize this PDF”",
        "• “What rules or requirements are in here?”",
        "• “What’s the hybrid/online format like?”",
    ]

    # De-dupe while preserving order
    seen = set()
    clean = []
    for l in lines:
        if l not in seen:
            clean.append(l)
            seen.add(l)

    return "\n".join(clean[:7])


examples_block = build_dynamic_examples()

st.markdown(f"""
# 🤖🔥 STL For STL Chatbot — Kid & Teen Edition 🎉  
Hi friend! I’m your **Super Smart PDF Learning Bot** 📚✨  
I can learn anything you upload — class lists, rules, stories, science topics, ANYTHING!  

Ask me stuff like:

{examples_block}

If I don’t know something, I’ll tell you AND show you how to teach me by uploading a PDF!  
Let’s gooo 🚀🔥
""")

st.markdown("---")


# ============================================================
# RETRIEVAL HELPERS
# ============================================================

def smart_retrieve(query: str, k=DEFAULT_K):
    if vectordb is None:
        return []
    try:
        return vectordb.similarity_search(query, k=k)
    except Exception:
        return []


def is_trained() -> bool:
    try:
        files = [f for f in os.listdir(APPROVED_DIR) if f != ".gitkeep"]
        return len(files) > 0
    except Exception:
        return False


def closest_matches(code: str) -> List[str]:
    all_ids = sorted(list(IDENTIFIERS))
    return difflib.get_close_matches(code.upper(), all_ids, n=5, cutoff=0.35)


# ============================================================
# INTENT DETECTION
# ============================================================

def extract_two_ids_for_compare(q: str) -> List[str]:
    found = []

    for ident in IDENTIFIERS:
        if ident in q.upper():
            found.append(ident)

    code_pattern = re.compile(r"\b([A-Z]{2,5})\s?(\d{3,4}[A-Z]?)\b")
    for m in code_pattern.findall(q.upper()):
        found.append(f"{m[0]} {m[1]}")

    seen = set()
    uniq = []
    for x in found:
        if x not in seen:
            uniq.append(x)
            seen.add(x)

    return uniq[:2]


def detect_category_request(q: str):
    ql = q.lower()
    for word, pref in ALIAS_MAP.items():
        if word in ql and any(x in ql for x in ["list", "show", "electives", "courses"]):
            return word, pref
    return None, None


def detect_question_category(q: str) -> str:
    ql = q.lower()

    if "compare" in ql:
        return "course_compare"

    if "elective" in ql or "list courses" in ql or "list all" in ql:
        return "elective_list"

    if any(x in ql for x in ["hybrid", "online", "in person", "remote"]):
        return "hybrid_format"

    if any(x in ql for x in ["schedule", "calendar", "timeline", "duration", "weeks", "long"]):
        return "schedule_info"

    if any(x in ql for x in ["program", "degree", "overview"]):
        return "program_info"

    if any(x in ql for x in ["admission", "apply", "deadline"]):
        return "admissions"

    if any(x in ql for x in ["tuition", "cost", "fees", "scholarship"]):
        return "tuition"

    if any(x in ql for x in ["requirement", "prereq", "credits"]):
        return "requirements"

    for ident in IDENTIFIERS:
        if ident in q.upper():
            return "course_detail"

    return "general"


# ============================================================
# PROMPT ENGINE
# ============================================================

def answer_with_context(question: str, docs, style_hint="") -> str:
    context = "\n\n".join([d.page_content for d in docs])

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a super friendly kids/teen PDF bot 🤖✨. "
         "Answer ONLY using the context. NEVER make up facts. "
         "If you can't find the answer, say so nicely and tell the kid "
         "that they can upload a PDF to teach you!"),
        ("user",
         "Context:\n{context}\n\nQuestion:\n{question}\n\n{style_hint}")
    ])

    msgs = prompt.format_messages(
        context=context,
        question=question,
        style_hint=style_hint
    )

    response = llm.invoke(msgs)
    return response.content.strip()


def fallback_no_results(question: str) -> str:
    if not is_trained():
        return (
            "🤖 I haven’t learned anything yet! 📚\n\n"
            "But YOU can teach me! Just upload a PDF and I’ll learn it instantly! 🚀"
        )

    return (
        f"🤖 I looked everywhere in the documents but couldn't find anything about:\n\n"
        f"“{question}”\n\n"
        "But you can teach me! Upload a PDF with that topic and I’ll learn it! 📚✨"
    )


# ============================================================
# CATEGORY HANDLERS
# ============================================================

def handle_course_detail(question, ident):
    docs = smart_retrieve(
        f"full details {ident} description units prereqs format", k=10
    )
    if not docs:
        sug = closest_matches(ident)
        if sug:
            return f"🤔 I couldn't find **{ident}**. Did you mean: {', '.join(sug)}?"
        return fallback_no_results(question)

    style = (
        "Give a fun intro + bullet points. "
        "If prereqs or units aren't in context, say so."
    )
    return answer_with_context(question, docs, style)


def handle_compare(question, id1, id2):
    d1 = smart_retrieve(id1, k=6)
    d2 = smart_retrieve(id2, k=6)

    missing = []
    if not d1:
        missing.append(id1)
    if not d2:
        missing.append(id2)

    if missing:
        msg = f"🤔 I couldn't find: {', '.join(missing)}.\n"
        for m in missing:
            sug = closest_matches(m)
            if sug:
                msg += f"Maybe you meant: {', '.join(sug)}\n"
        return msg

    left = answer_with_context(f"summary {id1}", d1, "Use 4–6 bullets.")
    right = answer_with_context(f"summary {id2}", d2, "Use 4–6 bullets.")

    return f"""
📘 **{id1}**  
{left}

📗 **{id2}**  
{right}

Want help choosing which one fits your goals? 😎
"""


def handle_category_list(word, prefix):
    matches = [i for i in IDENTIFIERS if i.startswith(prefix + " ")]

    if not matches:
        return fallback_no_results(word)

    out = f"🎓 Here are the {word.title()}-related items I learned:\n\n"
    for ident in sorted(matches):
        snippet_docs = smart_retrieve(ident, k=1)
        snippet = snippet_docs[0].page_content[:150].replace("\n", " ") + "..." if snippet_docs else ""
        out += f"• **{ident}** — {snippet}\n\n"
    return out


def handle_hybrid_format(q):
    docs = smart_retrieve("hybrid online in person format", k=10)
    if not docs:
        return fallback_no_results(q)
    return answer_with_context(q, docs, "Explain hybrid format using bullets + a fun intro.")


def handle_schedule_info(q):
    docs = smart_retrieve("schedule calendar timeline weeks", k=10)
    if not docs:
        return fallback_no_results(q)
    return answer_with_context(q, docs, "Use bullets for dates/times if present.")


def handle_program_info(q):
    docs = smart_retrieve("program overview description degree info", k=10)
    if not docs:
        return fallback_no_results(q)
    return answer_with_context(q, docs, "Give a short intro + bullet points.")


def handle_admissions(q):
    docs = smart_retrieve("admission apply deadline eligibility steps", k=10)
    if not docs:
        return fallback_no_results(q)
    return answer_with_context(q, docs, "Use intro + bullets for steps/dates.")


def handle_tuition(q):
    docs = smart_retrieve("tuition cost fees scholarship", k=10)
    if not docs:
        return fallback_no_results(q)
    return answer_with_context(q, docs, "Use intro + bullets. Only quote exact numbers if found.")


def handle_requirements(q):
    docs = smart_retrieve("requirements prereq credits", k=10)
    if not docs:
        return fallback_no_results(q)
    return answer_with_context(q, docs, "Use bullets for prereqs/requirements.")


def handle_general(q):
    docs = smart_retrieve(q, k=DEFAULT_K)
    if not docs:
        return fallback_no_results(q)
    return answer_with_context(q, docs, "Use fun intro + bullet points.")


# ============================================================
# MAIN ROUTER
# ============================================================

def answer_question(question: str) -> str:
    q = question.strip()

    cat_word, pref = detect_category_request(q)
    if cat_word and pref:
        return handle_category_list(cat_word, pref)

    cat = detect_question_category(q)

    if cat == "course_compare":
        ids = extract_two_ids_for_compare(q)
        if len(ids) == 2:
            return handle_compare(q, ids[0], ids[1])
        return fallback_no_results(q)

    if cat == "course_detail":
        for ident in IDENTIFIERS:
            if ident in q.upper():
                return handle_course_detail(q, ident)
        return fallback_no_results(q)

    if cat == "hybrid_format":
        return handle_hybrid_format(q)

    if cat == "schedule_info":
        return handle_schedule_info(q)

    if cat == "program_info":
        return handle_program_info(q)

    if cat == "admissions":
        return handle_admissions(q)

    if cat == "tuition":
        return handle_tuition(q)

    if cat == "requirements":
        return handle_requirements(q)

    return handle_general(q)


# ============================================================
# STREAMLIT INPUT UI (MORE ALIVE + FUN)
# ============================================================

st.markdown("### 💬 Ask me anything you want:")

alive_placeholders = [
    "Whatcha wanna know? 😄",
    "Ask me something from the PDF! 📚✨",
    "Type a question… I’m listening 👂🤖",
    "Let’s explore together! 🚀",
    "Got a course code? Throw it here 😎",
    "Ask about rules, schedules, or anything inside 🔎",
    "Teach me something cool by uploading a PDF! 🦖📄",
]

placeholder_text = random.choice(alive_placeholders)

user_q = st.text_input(
    "",
    placeholder=placeholder_text,
    key="kid_input"
)

if user_q:
    st.toast("🤖 Thinking…", icon="🧠")
    answer = answer_question(user_q)

    st.markdown("---")
    st.subheader("📘 Your Answer:")
    st.info(answer)

    # 🎈 Balloons ONLY if we found a real answer
    ans_lower = answer.lower() if answer else ""
    if answer and ("couldn't find" not in ans_lower) and ("haven’t learned" not in ans_lower) and ("upload a pdf" not in ans_lower):
        st.balloons()
