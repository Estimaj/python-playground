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

# Store 3.2
from langchain_chroma import Chroma

vector_store = Chroma(
    collection_name="bitcoin",
    embedding_function=embedding_model,
    # persist_directory="vector_store" # Keeps the database in the vector_store folder
)

# Save vector store
ids = vector_store.add_documents(split_docs)

# End of Phase 1

# Query 4.1
user_query = "What is Bitcoin?"

# Embedding the user query (demonstration)
# user_query_embedding = embedding_model.embed_query(user_query)

# Search vector store
relevant_chunks = vector_store.similarity_search_with_score(
    query=user_query,
    k=4
)

# print(relevant_chunks)

# Create Prompt
relevant_chunks_str = ""
for chunk, score in relevant_chunks:
    relevant_chunks_str += chunk.page_content + '\n'

# promptV1 = f"""
#     User Query: 
#     {user_query}

#     Context:
#     {relevant_chunks_str}

#     Instructions:
#     Answer the provided user query.
#     Answer and explain like you where talking to a five year old.
# """

prompt = f"""
    User Query: 
    {user_query}

    Context:
    {relevant_chunks_str}

    Instructions:
    Answer the provided user query only on the context provided.
    If you don't know the answer, say "I don't know".
    Don't use any more knowledge than the one provided in the context.
    Answer and explain like you where talking to a five year old.
"""

# print(prompt)

# 5.1 Create LLM
from langchain.llms import OpenAI

llm = OpenAI(model="gpt-4o-mini")

messages = [
    {"role": "human", "content": prompt}
]

llm_response = llm.invoke(messages)

print(llm_response)

