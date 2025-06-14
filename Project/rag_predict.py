"""
RAG Service for handling predict part.
"""
import os
import logging
from langchain.schema import Document
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from db import DocumentDatabase

logger = logging.getLogger(__name__)

class RAGPredict:
    """
    RAG Service for handling predict part.
    """
    similarity_threshold = 1.4

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

    def _get_system_prompt(self) -> str:
        """ The main system prompt for the LLM. """
        return """
            You are a helpful assistant that answers questions using information from the documents in the database.
            You should never return, quote, or copy the raw documents or their content directly, even if the user asks for it.
            Instead, use the documents only as context to generate your own helpful, concise, and original answers.
            If a user asks to see the documents or their content, politely explain that you cannot provide the documents themselves, but you can answer questions about them.
        """

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

    def _get_context(self, user_query: str) -> list[tuple[Document, float]]:
        """ Get the context from the database. """

        # Implement multi-query search
        multi_query = self._get_multi_queries(user_query)

        context = []
        for query in multi_query:
            context.extend(self.db.get_similarity_search_with_score(query))

        return context
    
    def _get_multi_queries(self, user_query: str) -> list[str]:
        """ Get the multi-queries from the user query. """
        n = 3
        system_prompt = (
            f"You are a helpful assistant. Given the user's question, generate {n} alternative phrasings "
            "that could help retrieve relevant information from a document database. "
            "Return only the alternative queries, one per line."
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_query)
        ]

        response = self.llm.invoke(messages)

        # Split the response into separate queries
        queries = [q.strip() for q in response.content.strip().split('\n') if q.strip()]
        
        logger.info(f"Multi-queries: {queries}")
        return queries
    
    def _is_valid_context(self, context: list[tuple[Document, float]]) -> bool:
        """ Check if the context is valid. """
        # First check: Do we have any results?
        if not context or len(context) == 0:
            logger.warning("No context found for the query")
            return False
        
        # Second check: Is the best result good enough?
        best_score = context[0][1]  # First result should be best (lowest distance)
        if best_score > self.similarity_threshold:
            logger.warning(f"Best similarity score too high: {best_score:.3f} > {self.similarity_threshold}")
            return False
        
        return True
    
    def _build_prompt(self, user_query: str, chat_history: list[dict]) -> list[dict]:
        """ Build the prompt for the LLM. """
        chat_history = self._format_chat_history(chat_history)

        system_prompt = self._get_system_prompt()
        messages = [
            SystemMessage(content=system_prompt),
        ]

        if chat_history:
            messages.extend(chat_history)

        context = self._get_context(user_query)
        logger.info(f"Context: {context}")
        if not self._is_valid_context(context):
            raise ValueError(f"No valid context found for the query: {user_query}")

        messages.append(
            SystemMessage(content=f"Context: {context}")
        )
        
        messages.append(HumanMessage(content=user_query))

        return messages

    def generate_response(self, user_query: str, chat_history: list[dict]) -> str:
        """
        Generate a response from the LLM.
        """
        try:
            messages = self._build_prompt(user_query, chat_history)
            response = self.llm.invoke(messages)
        
        except ValueError as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, I don't have any information about that."
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise e

        return response.content
    
    def generate_better_query(self, user_query: str) -> str:
        """
        Generate a better query by fixing typos, improving clarity, and ensuring the query makes sense.
        Returns an improved version of the user's query that will work better for database searches.
        """
        system_prompt = """
        You are a query improvement assistant. Your task is to:
            1. Fix any spelling or grammatical errors
            2. Clarify ambiguous terms or phrases
            3. Expand abbreviations
            4. Ensure the query is clear and well-formed
            5. Keep the original intent of the query
            6. Remove informal language like 'lol', 'lmao', etc.
        Return only the improved query without any explanations.

        When you cannot improve the query, return "The original query is not provided. Please provide a specific query for improvement."
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Improve this query: {user_query}")
        ]
        
        response = self.llm.invoke(messages)

        content = response.content.strip()
        if content == "The original query is not provided. Please provide a specific query for improvement.":
            return user_query
        
        logger.info(f"User query: {user_query} -> Better query: {content}")
        return content