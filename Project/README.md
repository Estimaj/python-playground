# RAG Chat Application

A Retrieval-Augmented Generation (RAG) chatbot that answers questions based on document context.

## Setup

1. Install dependencies (recommended to use a virtual environment)
    ```
    pip install -r ../requirements.txt
    ```
2. Add your OpenAI API key to a `.env` file in the parent directory:
    ```
    OPENAI_API_KEY=your_key_here
    ```

## Usage

```bash
# Start the chat application
python app.py

# Seed the database with documents
python app.py --seed

# Reset the database
python app.py --reset

# Check database size
python app.py --size
```

## Features

- Document retrieval and embedding using vector database
- Multi-query generation for improved search results
- Chat history preservation between sessions
- LLM-powered query improvement

