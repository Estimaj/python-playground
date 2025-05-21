# from gradio as gr

from langchain_community.document_loaders import PyPDFLoader
import re
from dotenv import load_dotenv

load_dotenv()

# Load Phase 1.1
file_path = "../documents/bitcoin.pdf"
loader = PyPDFLoader(file_path, mode="single")
documents = loader.load()

# Format Phase 1.2
for doc in documents:
    # Remove duplicate newlines and extra whitespace
    doc.page_content = re.sub(r'\s+', ' ', doc.page_content)
    # Remove any non-breaking spaces
    doc.page_content = doc.page_content.replace('\xa0', ' ')
    # Strip leading/trailing whitespace
    doc.page_content = doc.page_content.strip()

# print(documents)

# Document transformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

# # Create text splitter to handle newlines
text_splitter = RecursiveCharacterTextSplitter(
    # separators=["\n\n", "\n", " "],
    chunk_size=500, # 500 or 1000 and adapt 100 upwards
    chunk_overlap=100, # 0.15 - 0.3 only for structure data
    # length_function=len,
)

# Split documents 2.1
split_docs = text_splitter.split_documents(documents)

print(f"Split into {len(split_docs)} chunks")
print("-" * 40)

# Embeddings 3.1
from langchain.embeddings import OpenAIEmbeddings

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
