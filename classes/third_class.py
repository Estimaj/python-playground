# from gradio as gr

from langchain_community.document_loaders import PyPDFLoader
import re
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings

load_dotenv()

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

vector_store = Chroma(
    collection_name="bitcoin",
    embedding_function=embedding_model,
    persist_directory="class_3" # Keeps the database in the vector_store folder
)

def loading_phase():
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

    # Save vector store
    ids = vector_store.add_documents(split_docs)

    print(f"Added {len(ids)} documents to the vector store")
    # End of Phase 1

# loading_phase()

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

chat_history = "User Query 1: What is Bitcoin? Assistant: Bitcoin is a peer-to-peer electronic cash system that allows online payments to be sent directly from one party to another without going through a financial institution. It uses a system based on cryptographic proof to prevent double-spending and enables transactions between parties without the need for a trusted third party. Bitcoin transactions are secured through digital signatures, and a consensus mechanism is used to ensure the integrity of the transaction history."

prompt = f"""
    Instructions:
    Answer the provided user query based on the provided Context.
    If the answer for the question is not on the provided Context, check if it's on the Chat History, if it's answer based on that.
    Always answer in English.
    If the user asks the question in another language that is not English, say that you just talk know English.

    User Query: 
    {user_query}

    Context:
    {relevant_chunks_str}

    Chat History:
    {chat_history}
"""

print(prompt)

# 5.1 Create LLM
from langchain.llms import OpenAI

llm = OpenAI(model="gpt-4o-mini")

messages = [
    {"role": "human", "content": prompt}
]

llm_response = llm.invoke(messages)

print(llm_response)