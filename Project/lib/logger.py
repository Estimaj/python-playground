import os
import logging
from datetime import datetime
import sys

def setup_logging():
    """Configure logging for both console and file output."""
    
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Create log filename with timestamp
    log_filename = os.path.join(logs_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")

    # Set up the handlers
    handlers = [
        logging.FileHandler(log_filename), # File output
    ]

    if len(sys.argv) > 1:
        handlers.append(logging.StreamHandler()) # Console output (for non-Streamlit)
    
    # Configure logging with both console and file handlers
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    return log_filename