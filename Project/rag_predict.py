"""
RAG Service for handling predict part.
"""
from db import DocumentDatabase
import os
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import logging

logger = logging.getLogger(__name__)

class RAGPredict:
    """
    RAG Service for handling predict part.
    """

    def __init__(self):
        """
        Initialize the RAGPredict service.
        """
        self.db = DocumentDatabase()
        self.llm = self._setup_llm()

    def _setup_llm(self):
        """
        Setup the LLM.
        """
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please add it to your .env file: OPENAI_API_KEY=your_key_here"
            )

        return ChatOpenAI(model="gpt-4o-mini")
    

    def _format_chat_history(self, chat_history: list[dict]) -> list[dict]:
        """ Build the chat history for the LLM. """
        # Convert each message to appropriate LangChain message type
        formatted_history = []
        for msg in chat_history:
            if msg["role"] == "user":
                formatted_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                formatted_history.append(AIMessage(content=msg["content"]))
                
        return formatted_history

    def _get_context(self, user_query: str) -> str:
        """ Get the context from the database. """
        return self.db.get_similarity_search_with_score(user_query)
    
    def _build_prompt(self, user_query: str, chat_history: list[dict]) -> list[dict]:
        """ Build the prompt for the LLM. """
        chat_history = self._format_chat_history(chat_history)

        system_prompt = "You are a helpful assistant that can answer questions about the documents in the database."
        messages = [
            SystemMessage(content=system_prompt),
        ]

        if chat_history:
            messages.extend(chat_history)

        # TODO: Get the context from the database
        context = self._get_context(user_query)
        logger.info(f"Context: {context}")
        # if not self._isValidContext(context):
        #     return "I'm sorry, I don't have any information about that."
        messages.append(
            SystemMessage(content=f"Context: {context}")
        )
        
        messages.append(HumanMessage(content=user_query))

        return messages

    def generate_response(self, user_query: str, chat_history: list[dict]) -> str:
        """
        Generate a response from the LLM.
        """
        messages = self._build_prompt(user_query, chat_history)
        response = self.llm.invoke(messages)
        return response.content