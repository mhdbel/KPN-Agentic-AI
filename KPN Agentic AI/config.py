import os
from langchain_google_genai import ChatGoogleGenerativeAI

# Load API key (set via environment variable)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Shared LLM configuration
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=GOOGLE_API_KEY,
    temperature=0.3
)
