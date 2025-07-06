from dotenv import load_dotenv
from llm_client.openai_client import OpenAIClient

# Load .env variables
load_dotenv()

# Create OpenAI client instance
llm = OpenAIClient()

# Simple test prompt
response = llm.chat("Just checking if you're awake, Chat GPT!")

# Output the response
print("LLM Response:", response)