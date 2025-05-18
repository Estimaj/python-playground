from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Load API key from .env file
load_dotenv()

# Initialize OpenAI model
llm = OpenAI(temperature=0.7)

# Create a prompt template
prompt = PromptTemplate(
    input_variables=["question"],
    template="Answer the following question: {question}"
)

# Create and run a chain
chain = LLMChain(llm=llm, prompt=prompt)
response = chain.run("What are three benefits of using LangChain?")

print(response)