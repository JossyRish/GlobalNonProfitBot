"""
backend/ingest_all.py

Rebuilds the entire Chroma database by re-ingesting every
PDF in uploads/approved.

Usage:
    python backend/ingest_all.py
"""

import os
import shutil
from backend.ingest_file import ingest_file

APPROVED = "uploads/approved"
CHROMA = "uploads/.chroma_data"


def ingest_all():
    print("🧹 Clearing Chroma DB...")
    shutil.rmtree(CHROMA, ignore_errors=True)
    os.makedirs(CHROMA, exist_ok=True)

    print("📄 Scanning approved PDFs...")
    files = [f for f in os.listdir(APPROVED) if f.lower().endswith(".pdf")]

    if not files:
        print("⚠️ No approved files found.")
        return

    for f in files:
        path = os.path.join(APPROVED, f)
        print(f"➡️ Re-ingesting: {f}")
        msg = ingest_file(path, move_to_approved=False)  # don't re-move
        print(msg)

    print("🎉 DONE — All PDFs re-ingested!")


if __name__ == "__main__":
    ingest_all()
