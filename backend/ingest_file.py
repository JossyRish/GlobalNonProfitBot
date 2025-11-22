import os
import shutil
import hashlib
from datetime import datetime

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# ==========================================================
#  INGEST FILE MODULE — FINAL FIXED VERSION
# ==========================================================

PENDING_DIR = "uploads/pending"
APPROVED_DIR = "uploads/approved"
PERSIST_DIR = "uploads/.chroma_data"

# -----------------------------------------------------------
# SHA-256 HASH FOR DUP DETECTION
# -----------------------------------------------------------
def compute_hash(filepath: str) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        sha.update(f.read())
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

    BEHAVIOR FIX:
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

    # 2) Hash check
    file_hash = compute_hash(pdf_path)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )

    existing = vectorstore.get(include=["metadatas"])
    for meta in existing.get("metadatas", []):
        if meta.get("hash") == file_hash:
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
        # This is admin fast upload → ALREADY in APPROVED
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

    try:
        vectorstore._client.persist()
    except Exception:
        pass

    # 7) Return clean output
    return {
        "status": "success",
        "message": f"🎉 Ingested {len(docs)} chunks from **{new_name}**",
        "chunks": len(docs),
        "filename": new_name
    }
