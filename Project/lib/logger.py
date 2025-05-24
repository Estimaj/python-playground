import os
import logging
from datetime import datetime

def setup_logging():
    """Configure logging for both console and file output."""
    
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Create log filename with timestamp
    log_filename = os.path.join(logs_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Configure logging with both console and file handlers
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),  # File output
            logging.StreamHandler()              # Console output (for non-Streamlit)
        ]
    )
    
    return log_filename