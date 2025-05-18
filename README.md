# Python LangChain Project

This project demonstrates the use of LangChain with OpenAI integration.

## Prerequisites

- Python 3.8 or higher
- OpenAI API key

## Installation

1. Clone the repository:
```
git clone https://github.com/Estimaj/python-playground.git
cd python-playground
```

2. Install dependencies:
```
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root directory with your OpenAI API key:
```
OPENAI_API_KEY=your-api-key-here
```

You can copy the provided `env.example` file as a starting point:
```
cp .env.example .env
```

Then edit the `.env` file and replace the placeholder with your actual OpenAI API key.

## Running the Application

To run the example script:
```
python hello.py
```

This will execute a simple LangChain with OpenAI example that demonstrates basic functionality.

## Project Structure

- `requirements.txt` - Project dependencies
- `.env` - Example environment variables file

## Additional Resources

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [OpenAI API Documentation](https://platform.openai.com/docs/introduction) 