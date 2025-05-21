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

# Configure logging - this will be shared across the entire application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file in parent directory
dotenv_path = os.path.join("..", ".env")
load_dotenv(dotenv_path)

# Export logger for other modules to import
__all__ = ['logger']

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
        return 0
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        return 1

def parse_arguments(args: List[str]) -> Dict[str, Any]:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Application description here")
    
    # Add arguments here
    parser.add_argument("--seed", "-s", action="store_true", help="Seed the database")
    # parser.add_argument("--output", "-o", type=str, default="output", help="Output directory")
    
    # Parse arguments
    return vars(parser.parse_args(args))

def main() -> int:
    """Application entry point."""
    args = parse_arguments(sys.argv[1:])
    
    if args.get('seed'):
        return seed_database()
    else:
        # Default behavior is to run streamlit
        return run_streamlit()

if __name__ == "__main__":
    sys.exit(main())
