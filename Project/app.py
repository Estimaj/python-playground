#!/usr/bin/env python3
"""
Main application entry point and configuration.
"""
import os
import sys
import logging
import argparse
import subprocess
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from rag_load import RAGLoad
from db import DocumentDatabase
from lib.logger import setup_logging

# Call this instead of the old basicConfig
log_file = setup_logging()
logger = logging.getLogger(__name__)
logger.info(f"Logging configured. Log file: {log_file}")

# Load environment variables from .env file in parent directory
dotenv_path = os.path.join("..", ".env")
load_dotenv(dotenv_path)

# Export logger for other modules to import
__all__ = ['logger']

# TODO: List of things to do:
# 1. Get a function tool to return the website url

def run_streamlit() -> int:
    """Run the Streamlit application."""
    try:
        logger.info("Launching Streamlit application")
        streamlit_path = os.path.join(os.path.dirname(__file__), "streamlit_app.py")
        subprocess.run(["streamlit", "run", streamlit_path])
        return 0
    except Exception as e:
        logger.error(f"Error running Streamlit: {e}")
        return 1

def seed_database() -> int:
    """Seed the database."""
    try:
        logger.info("Seeding database")
        # Database seeding logic here
        rag_load = RAGLoad()
        rag_load.load_documents()

        return 1
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        return 0

def reset_database() -> int:
    """Reset the database."""
    try:
        logger.info("Resetting database")
        DocumentDatabase().reset_collection()

        return 1
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        return 0

def get_database_size() -> int:
    """Get the size of the database."""
    try:
        logger.info("Getting database size")
        return DocumentDatabase().get_collection_info()
    except Exception as e:
        logger.error(f"Error getting database size: {e}")
        return 0

def parse_arguments(args: List[str]) -> Dict[str, Any]:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Application description here")
    
    # Add arguments here
    parser.add_argument("--seed", "-s", action="store_true", help="Seed the database")
    parser.add_argument("--reset", action="store_true", help="Reset the database")
    parser.add_argument("--size", action="store_true", help="Get the size of the database")
    # parser.add_argument("--output", "-o", type=str, default="output", help="Output directory")
    
    # Parse arguments
    return vars(parser.parse_args(args))

def main() -> int:
    """Application entry point."""
    args = parse_arguments(sys.argv[1:])
    
    if args.get('seed'):
        return seed_database()
    elif args.get('reset'):
        return reset_database()
    elif args.get('size'):
        return get_database_size()
    else:
        # Default behavior is to run streamlit
        return run_streamlit()

if __name__ == "__main__":
    sys.exit(main())
