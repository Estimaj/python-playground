from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

# Load API key from .env file
load_dotenv()

# Initialize chat model
model = init_chat_model("gpt-4o-mini", model_provider="openai")

# Set up messages for translation
messages = [
    SystemMessage("Translate the following from English into Italian"),
    HumanMessage("hi!"),
]

# Get response and stream tokens
model.invoke(messages)
for token in model.stream(messages):
    print(token.content, end="", flush=True)

print("\n-----")