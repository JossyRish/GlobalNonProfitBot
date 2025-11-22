"""
backend/ingest_file.py
======================

✅ Cloud-safe, Windows-safe ingestion with NO UI debug spam.
Fixes:
  • Approve blink/no-move bug (safe empty-DB duplicate check)
  • Uses public Chroma persist() (no private _client call)
  • Creates required folders on first run
  • Keeps your original behavior + signature intact
"""

import os
import shutil
import hashlib
from datetime import datetime

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


# ==========================================================
# DIRECTORIES
# ==========================================================

PENDING_DIR = "uploads/pending"
APPROVED_DIR = "uploads/approved"
PERSIST_DIR = "uploads/.chroma_data"

os.makedirs(PENDING_DIR, exist_ok=True)
os.makedirs(APPROVED_DIR, exist_ok=True)
os.makedirs(PERSIST_DIR, exist_ok=True)


# -----------------------------------------------------------
# SHA-256 HASH FOR DUP DETECTION
# -----------------------------------------------------------
def compute_hash(filepath: str) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        # read in chunks to avoid memory spikes on large PDFs
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


# -----------------------------------------------------------
# INGEST FILE
# -----------------------------------------------------------
def ingest_file(pdf_path: str, move_to_approved: bool = True):
    """
    Ingest a PDF file:

      ✓ Duplicate detection
      ✓ Optional move → APPROVED
      ✓ Chunk text
      ✓ Embed (OpenAI text-embedding-3-small)
      ✓ Store in Chroma

    ALWAYS returns a dict:
        {
            status: "success" | "duplicate" | "error",
            message: "...",
            chunks: int,
            filename: "stored_filename.pdf"
        }

    BEHAVIOR:
      🔥 Admin Fast Upload passes move_to_approved=False
         → file is already correctly in APPROVED folder
      🔥 Public uploads use default = True → safely moved from PENDING → APPROVED
    """

    # 1) Validate path
    if not pdf_path.lower().endswith(".pdf"):
        return {
            "status": "error",
            "message": "❌ Only PDF files can be ingested.",
            "chunks": 0,
            "filename": None
        }

    if not os.path.exists(pdf_path):
        return {
            "status": "error",
            "message": f"❌ PDF not found: {pdf_path}",
            "chunks": 0,
            "filename": None
        }

    # 2) Hash check (dup detection)
    file_hash = compute_hash(pdf_path)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )

    # ✅ SAFE duplicate check even when DB is empty or initializing on Cloud
    try:
        existing = vectorstore.get(include=["metadatas"])
        metadatas = existing.get("metadatas", []) if existing else []
        if not isinstance(metadatas, list):
            metadatas = []
    except Exception as e:
        # console-only visibility; no Streamlit UI spam
        print(f"[ingest_file] Duplicate check skipped (empty/locked DB): {e}")
        metadatas = []

    for meta in metadatas:
        # meta can sometimes be None or empty dict
        if isinstance(meta, dict) and meta.get("hash") == file_hash:
            return {
                "status": "duplicate",
                "message": "⚠️ This PDF was already ingested.",
                "chunks": 0,
                "filename": os.path.basename(pdf_path)
            }

    # 3) Determine APPROVED destination
    original_name = os.path.basename(pdf_path)

    if move_to_approved:
        # This is public upload → move & timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"{timestamp}_{original_name}"
        approved_path = os.path.join(APPROVED_DIR, new_name)
        shutil.move(pdf_path, approved_path)
    else:
        # This is admin fast upload → already in APPROVED
        approved_path = pdf_path
        new_name = original_name

    # 4) Load PDF pages
    loader = PyPDFLoader(approved_path)
    pages = loader.load()

    # 5) Chunk
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )
    docs = splitter.split_documents(pages)

    # Add metadata
    for d in docs:
        d.metadata["source"] = new_name
        d.metadata["hash"] = file_hash

    # 6) Store in Chroma
    vectorstore.add_documents(docs)

    # ✅ Public persist call (cloud-safe)
    try:
        vectorstore.persist()
    except Exception as e:
        print(f"[ingest_file] Persist skipped (cloud lock ok): {e}")

    # 7) Return clean output
    return {
        "status": "success",
        "message": f"🎉 Ingested {len(docs)} chunks from **{new_name}**",
        "chunks": len(docs),
        "filename": new_name
    }
