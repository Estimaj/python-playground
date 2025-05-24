"""
RAG Service for handling predict part.
"""
import os
import re
import logging
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from db import DocumentDatabase
from lib.rag_load_helper import filter_meaningful_content, filter_notion_content

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

        # Add metadata
        for doc in split_docs:
            doc.metadata["document_type"] = "cv"
            doc.metadata["loader"] = "pdf"

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
        # https://python.langchain.com/docs/integrations/document_loaders/notion/

        files = [
            "./data/notion_2025.md",
            "./data/notion_old.md",
        ]
        
        all_filtered_docs = []
        
        for file_path in files:
            logger.info(f"Loading Notion file: {file_path}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}, skipping...")
                continue
            
            loader = UnstructuredMarkdownLoader(file_path=file_path)
            documents = loader.load()

            # Use smaller chunks for to-do lists
            text_splitter = RecursiveCharacterTextSplitter(
                separators=["\n\n", "\n", ".", " "],
                chunk_size=300,
                chunk_overlap=50,
            )

            split_docs = text_splitter.split_documents(documents)
            
            # Filter meaningful content (same function works for all notion files!)
            filtered_docs = filter_notion_content(split_docs)
            
            # Add metadata
            for doc in filtered_docs:
                doc.metadata["document_type"] = "notion"
                doc.metadata["loader"] = "markdown"
                doc.metadata["source_file"] = file_path  # Track which file it came from
            
            all_filtered_docs.extend(filtered_docs)
            logger.info(f"File {file_path}: {len(split_docs)} → {len(filtered_docs)} chunks after filtering")
        
        # Add all filtered documents to database
        if all_filtered_docs:
            self.db.add_documents(all_filtered_docs)
            logger.info(f"Total Notion documents added: {len(all_filtered_docs)}")
        else:
            logger.warning("No Notion documents were loaded")
    
    def load_documents(self):
        """
        Load the documents from the database.
        """
        try:
            self._load_cv_documents()
        except Exception as e:
            logger.error(f"Error loading documents from cv: {e}")
            raise e

        try:
            self._load_website_documents()
        except Exception as e:
            logger.error(f"Error loading documents from website: {e}")
            raise e

        try:
            self._load_notion_documents()
        except Exception as e:
            logger.error(f"Error loading documents from notion: {e}")
            raise e

        info = self.db.get_collection_info()
        logger.info(f"Database seeded successfully. Collection info: {info}")