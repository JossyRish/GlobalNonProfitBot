import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


# 1️⃣ Load your OpenAI API key from environment variable
# This allows the code to securely access OpenAI services without hardcoding your key.
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

# 2️⃣ Define the path to your PDF document
pdf_path = "data/rkf_data.pdf"

# Check if the file exists to avoid runtime errors
if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"❌ Could not find {pdf_path}. Please check the path.")

# 3️⃣ Read and extract text from the PDF
# PyPDF2 reads each page, and we combine all the text into a single string.
print("📄 Reading PDF content...")
reader = PdfReader(pdf_path)
text = ""
for page in reader.pages:
    text += page.extract_text() or ""

if not text.strip():
    raise ValueError("❌ No text could be extracted from the PDF. Check file contents.")

print(f"Extracted {len(text)} characters from PDF")


# 4️⃣ Split text into smaller pieces (chunks)
# Large text blocks are difficult for the model to process efficiently.
# We split them into smaller, overlapping chunks to maintain context.
print("✂️ Splitting text into chunks...")
# This splitter is smarter — it tries multiple levels of separators (paragraphs, sentences, etc.)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,          # Each chunk will be ~1000 characters
    chunk_overlap=100,        # Overlap helps preserve context between chunks
    separators=["\n\n", "\n", ".", "!", "?", " "]
)

chunks = splitter.split_text(text)
print(f"✅ Created {len(chunks)} text chunks for embedding.")

# Optional: peek at first few chunks
for i, chunk in enumerate(chunks[:3]):
    print(f"\n--- Chunk {i+1} (length {len(chunk)} chars) ---")
    print(chunk[:250].strip() + "...")

# 5️⃣ Generate embeddings
# Embeddings convert text into numerical vectors — a mathematical representation of meaning.
# These vectors allow the chatbot to find and compare the *semantic similarity* between queries and stored text.
print("🧠 Generating embeddings (turning text into vector representations)...")
embeddings = OpenAIEmbeddings()

# 6️⃣ Store embeddings in a Chroma vector database
# Chroma saves these vector representations locally, so we can search for relevant text later.
# This is the foundation of the Retrieval-Augmented Generation (RAG) approach.
print("💾 Storing embeddings in Chroma database...")
vectorstore = Chroma.from_texts(
    chunks,
    embeddings,
    persist_directory="chroma_store"
)

print("\n Success! PDF ingested and embeddings stored in 'chroma_store/'")
print("You can now use these embeddings to answer questions about your document.")
