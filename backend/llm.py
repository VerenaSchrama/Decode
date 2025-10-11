"""
LLM and Embeddings initialization
Handles API key loading and model setup
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Load environment variables once
load_dotenv()

# Initialize models
llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

def get_llm():
    """Get the initialized LLM instance"""
    return llm

def get_embeddings():
    """Get the initialized embeddings instance"""
    return embeddings

def is_api_key_available():
    """Check if OpenAI API key is available"""
    return os.getenv("OPENAI_API_KEY") is not None
