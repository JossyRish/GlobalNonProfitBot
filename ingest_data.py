# --- ingest_data.py ---
"""
This script reads your PDF (rkf_data.pdf), extracts text, splits it into chunks,
generates embeddings using OpenAI, and stores them in a Chroma vector database.

Your Streamlit chatbot will later read from this Chroma database to answer questions.
"""

import os

# PDF loader from the LangChain community package.
# Much more reliable than PyPDF2 and fully compatible with LangChain 0.3+
from langchain_community.document_loaders import PyPDFLoader

# Splits long text into smaller overlapping chunks for embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# OpenAI embeddings wrapper (uses your OPENAI_API_KEY automatically)
from langchain_openai import OpenAIEmbeddings

# Vector database (Chroma) for storing your embeddings locally
from langchain_community.vectorstores import Chroma

# Load OpenAI key manually just for verification
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------------------------------------------------
# 1️⃣ VALIDATE OPENAI API KEY
# ---------------------------------------------------
if not openai.api_key:
    # If the API key is not set, LangChain embeddings will fail
    raise ValueError("❌ Missing OPENAI_API_KEY environment variable. Set it first.")

# ---------------------------------------------------
# 2️⃣ SPECIFY YOUR PDF FILE
# ---------------------------------------------------
pdf_path = "data/rkf_data.pdf"

# Make sure the PDF actually exists
if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"❌ Could not find {pdf_path}. Please check the path.")

print("📄 Loading PDF content...")

# PyPDFLoader loads your PDF and splits it into page-level Document objects
loader = PyPDFLoader(pdf_path)

# This loads each page of your PDF as a separate document
pages = loader.load()

# Basic validation — PDF must produce at least one page
if not pages:
    raise ValueError("❌ No text could be extracted from the PDF. Are you sure it has real text?")

print(f"📄 Loaded {len(pages)} pages from PDF")


# ---------------------------------------------------
# 3️⃣ EXTRACT RAW TEXT (keeping your behavior)
# ---------------------------------------------------
# You previously read text manually; now we extract page_content from each Document
text = ""
for p in pages:
    # Each `p` is a LangChain Document with content in `page_content`
    text += p.page_content + "\n"

print(f"📝 Extracted {len(text)} characters from PDF")


# ---------------------------------------------------
# 4️⃣ SPLIT THE TEXT INTO CHUNKS
# ---------------------------------------------------
# Large PDFs cannot be embedded as one giant text block.
# So we split into ~1000 character pieces with overlap for context.

print("✂️ Splitting text into chunks...")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,          # Each chunk is about 1000 characters
    chunk_overlap=100,        # Overlap helps keep context between chunks
    separators=[
        "\n\n",   # break at paragraph
        "\n",     # then at newline
        ".",      # then at sentence boundaries
        "!", "?", # punctuation
        " "       # finally at whitespace if needed
    ]
)

# Split the large `text` string into a list of chunk strings
chunks = splitter.split_text(text)

print(f"✅ Created {len(chunks)} text chunks for embedding.")

# Show the first 3 chunks so you can visually confirm things look good
for i, chunk in enumerate(chunks[:3]):
    print(f"\n--- Chunk {i+1} (length {len(chunk)} chars) ---")
    print(chunk[:250].strip() + "...")


# ---------------------------------------------------
# 5️⃣ CONVERT CHUNKS INTO DOCUMENT OBJECTS
# ---------------------------------------------------
# Chroma prefers "Document" objects instead of raw strings.
from langchain_core.documents import Document

documents = [Document(page_content=chunk) for chunk in chunks]


# ---------------------------------------------------
# 6️⃣ GENERATE EMBEDDINGS
# ---------------------------------------------------
# Embeddings = how we convert text → numeric vector representation
# These vectors allow similarity search in your chatbot.

print("🧠 Generating embeddings using OpenAI...")
embeddings = OpenAIEmbeddings()   # Uses model="text-embedding-3-small" by default


# ---------------------------------------------------
# 7️⃣ STORE EMBEDDINGS IN CHROMA
# ---------------------------------------------------
# Chroma stores the vector database locally in the folder "chroma_store"
# Your chatbot will load this folder and use it for retrieval.

print("💾 Saving embeddings into Chroma vectorstore...")

vectorstore = Chroma.from_documents(
    documents=documents,             # your chunked documents
    embedding=embeddings,            # embedding function
    persist_directory="chroma_store" # folder where the DB will be saved
)

print("\n🎉 SUCCESS!")
print("PDF ingested successfully.")
print("Embeddings stored in 'chroma_store/'.")
print("Your chatbot can now answer questions based on this PDF.")
