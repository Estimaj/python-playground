"""
RAG Service for handling predict part.
"""
import os
import re
import logging
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from db import DocumentDatabase
from lib.rag_load_helper import filter_meaningful_content

logger = logging.getLogger(__name__)

class RAGLoad:
    """
    RAG Service for handling predict part.
    """

    def __init__(self):
        """
        Initialize the RAGPredict service.
        """
        self.db = DocumentDatabase()

    def _load_cv_documents(self) -> None:
        """Load the CV document."""
        cv_path = "./data/cv.pdf"
        loader = PyPDFLoader(cv_path)
        documents = loader.load()

        # # Create text splitter to handle newlines
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ".", " "],
            chunk_size=500, # 500 or 1000 and adapt 100 upwards
            chunk_overlap=100, # 0.15 - 0.3 only for structure data
        )
        split_docs = text_splitter.split_documents(documents)

        self.db.add_documents(split_docs)

    def _load_website_documents(self, website_url: str = "https://joaoestima.com") -> None:
        """Load the website documents."""
        # https://python.langchain.com/docs/integrations/document_loaders/web_base/

        loader = WebBaseLoader(website_url)
        documents = loader.load()

        # Use the same text splitter as PDF documents
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ".", " "],
            chunk_size=1000,  # Slightly larger for web content
            chunk_overlap=100,
        )
        split_docs = text_splitter.split_documents(documents)

        logger.info(f"Split into {len(split_docs)} initial chunks")
        
        # Clean and filter content
        cleaned_docs = filter_meaningful_content(split_docs)
        
        logger.info(f"After cleaning: {len(cleaned_docs)} meaningful chunks")
        
        # Add metadata to identify source
        for doc in cleaned_docs:
            doc.metadata["document_type"] = "website"
            doc.metadata["loader"] = "web"
            doc.metadata["source"] = website_url
        
        self.db.add_documents(cleaned_docs)

    def _load_notion_documents(self):
        """Load the Notion documents."""
        # TODO: Implement this https://python.langchain.com/docs/integrations/document_loaders/notion/
        raise NotImplementedError("Loading Notion documents is not implemented yet.")
    
    def load_documents(self):
        """
        Load the documents from the database.
        """
        # try:
        #     self._load_cv_documents()
        # except Exception as e:
        #     logger.error(f"Error loading documents from cv: {e}")
        #     raise e

        # try:
        #     self._load_website_documents()
        # except Exception as e:
        #     logger.error(f"Error loading documents from website: {e}")
        #     raise e

        info = self.db.get_collection_info()
        logger.info(f"Database seeded successfully. Collection info: {info}")