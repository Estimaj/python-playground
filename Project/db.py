#!/usr/bin/env python3
"""
Database management for RAG application.
Handles document storage, embeddings, and similarity search.
"""
import os
import logging
from typing import Dict, Any
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)

class DocumentDatabase:
    """Handles document storage and retrieval for RAG."""
    
    def __init__(
        self,
        db_path: str = "./chroma_db",
        collection_name: str = "project_documents_collection"
    ) -> None:
        """Initialize the database connection."""
        self.db_path = db_path
        self.collection_name = collection_name
        self.embeddings = self._setup_embeddings()
        self.vector_store = self._connect()

    def _setup_embeddings(self):
        """Setup embedding function."""
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please add it to your .env file: OPENAI_API_KEY=your_key_here"
            )
        
        return OpenAIEmbeddings(model="text-embedding-3-small")

    def _connect(self):
        """Connect to ChromaDB using LangChain wrapper."""
        vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.db_path,
        )

        return vector_store
    
    def seed_database(self) -> bool:
        """Seed the database with initial documents."""
        try:
            logger.info("Starting database seeding...")
            
            # For now, let's add a simple test document
            # sample_documents = [
            #     {
            #         "id": "doc_1",
            #         "text": "This is a sample document for testing the RAG system.",
            #         "metadata": {"source": "test", "type": "sample"}
            #     }
            # ]
            
            # logger.info(f"Successfully seeded database with {len(sample_documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error seeding database: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the current collection."""
        try:
            vectors = self.vector_store.get()
            return {
                "document_count": len(vectors),
                "collection_name": self.collection_name
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}
