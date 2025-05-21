#!/usr/bin/env python3
"""
Streamlit application for chat interface.
"""
import os
import sys
import streamlit as st

# Add parent directory to path to import from app.py
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import logger from main application
from Project.app import logger

def main():
    """Main Streamlit application."""
    logger.info("Starting Streamlit application interface")
    
    st.title("Chat Interface")
    st.write("Welcome to the chat application!")
    
    # Simple chat input
    user_input = st.chat_input("Type a message...")
    if user_input:
        logger.info(f"Received user input: {user_input}")
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.write(f"You said: {user_input}")

if __name__ == "__main__":
    main() 