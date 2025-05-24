#!/usr/bin/env python3
"""
Streamlit application for chat interface.
"""
import streamlit as st
import logging
from datetime import datetime

# Create logger for this module
logger = logging.getLogger(__name__)

class StreamlitApp:
    """Simple Streamlit chat application."""
    
    def __init__(self):
        """Initialize the Streamlit app."""
        self._setup_page()
        self._initialize_chat_history()
    
    def _setup_page(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="Chat Interface",
            page_icon="💬"
        )

    def _initialize_chat_history(self):
        """Initialize chat history in session state."""
        if "messages" not in st.session_state:
            st.session_state.messages = []
            logger.info("Chat history initialized")
    
    def _render_chat_interface(self):
        """Render the main chat interface."""
        st.title("💬 Chat Interface")
        st.write("Welcome to the chat application!")
        
        # Display all previous messages
        self._display_chat_history()

        # Simple chat input
        user_input = st.chat_input("Type a message...")
        
        if user_input:
            self._add_message(role="user", content=user_input)
            assistant_response = "..."
            self._add_message(role="assistant", content=assistant_response)

            # Rerun to show the new messages
            st.rerun()

    def _display_chat_history(self):
        """Display all messages from chat history."""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                # Optionally show timestamp
                st.caption(f"_{message['timestamp'].strftime('%H:%M:%S')}_")
    
    def _add_message(self, role: str, content: str):
        """Add a message to chat history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        }
        st.session_state.messages.append(message)
        logger.info(f"Added {role} message: {content}")

    def run(self):
        """Main application entry point."""
        logger.info("Starting Streamlit chat application")
        self._render_chat_interface()

def main():
    """Application entry point."""
    app = StreamlitApp()
    app.run()

if __name__ == "__main__":
    main() 