# from gradio as gr

from langchain_community.document_loaders import PyPDFLoader
import re
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain_openai import ChatOpenAI
import json

load_dotenv()

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

vector_store = Chroma(
    collection_name="bitcoin",
    embedding_function=embedding_model,
    persist_directory="class_4" # Keeps the database in the vector_store folder
)

def ingestion_phase():
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

# ingestion_phase()

# user_query = "What do you know about England?" # AI: I don't have the provided context for that question.
# user_query = "What is ethereum?" # AI: I don't have the provided context for that question.
user_query = "What is bitcoin?" 

# Multiple sub-queries generation
# prompt_query_transformed = f"""
# Given the following user query, deconstruct it into several sub-queries, based on the number of queries done.

# User Query:
# {user_query}

# Return the sub-queries in a JSON format with the following structure:
# {{
#     "sub_queries": [
#         "sub_query_1",
#         "sub_query_2",
#         "sub_query_3"
#     ]
# }}
# """

# Sub-queries generation
# prompt_query_transformed = f"""
# Given the following user query, deconstruct it into several sub-queries, based on the number of queries done.
# If the user is only asking about one thing, then only return one sub-query.

# User Query:
# {user_query}

# Return the sub-queries in a JSON format with the following structure:
# {{
#     "sub_queries": [
#         "sub_query_1",
#         "sub_query_2",
#         "sub_query_3"
#     ]
# }}
# """

# llm_json = ChatOpenAI(model="gpt-4o-mini")
# llm_json_with_format = llm_json.bind(response_format={"type": "json_object"})
# query_transformed = llm_json_with_format.invoke(prompt_query_transformed)
# query_transformed_json = json.loads(query_transformed.content)

# print("-" * 40)
# print(query_transformed_json["sub_queries"])
# print("-" * 40)

# relevant_chunks_list = []
# for sub_query in query_transformed_json["sub_queries"]:
# # Search vector store
#     relevant_chunks = vector_store.similarity_search_with_score(
#         query=sub_query,
#         k=2
#     )
#     relevant_chunks_list.extend(relevant_chunks)

# prompt_hyde
# prompt_hyde = f"""
# Answer the following user query with a brief response.
# Just answer the question, don't add any other information.

# User Query:
# {user_query}
# """


system_prompt = f"""
    You are a professional assistant in the crypto area and know a lot about bitcoin.

    Instructions:
    Answer the provided user query based on the provided Context.
    If the answer for the question is not on the provided Context, check if it's on the Chat History, if it's answer based on that.
    If after checking the context and chat history you still don't know the answer,
        don't use internal knowledge, answer with 'I don't have the provided context for that question'.
    Always answer in English language.
"""

relevant_chunks_list = []
for sub_query in query_transformed_json["sub_queries"]:
# Search vector store
    relevant_chunks = vector_store.similarity_search_with_score(
        query=sub_query,
        k=2
    )
    relevant_chunks_list.extend(relevant_chunks)

# Create Prompt
relevant_chunks_str = ""
for chunk, score in relevant_chunks_list:
    relevant_chunks_str += chunk.page_content + '\n'

# Human or User and Assistant and AI
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "ai", "content": relevant_chunks_str},
]

chat_history = [
]

messages.extend(chat_history)
messages.append({"role": "user", "content": user_query})

print("-" * 40)
print(messages)
print("-" * 40)

# 5.1 Create LLM
llm = OpenAI(model="gpt-4o-mini")

llm_response = llm.invoke(messages)
print("-" * 40)
print(llm_response)
print("-" * 40)