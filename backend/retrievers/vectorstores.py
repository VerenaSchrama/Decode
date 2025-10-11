"""
Vectorstore setup and retrievers
Handles ChromaDB initialization and error handling
"""

import os
from langchain_community.vectorstores import Chroma
from llm import get_embeddings

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTORSTORE_PATH = os.path.join(BASE_DIR, "data", "vectorstore", "chroma")

# Initialize vectorstore and retriever
vectorstore = None
main_retriever = None

def initialize_vectorstore():
    """Initialize the InFlo book vectorstore"""
    global vectorstore, main_retriever
    
    try:
        embeddings = get_embeddings()
        vectorstore = Chroma(
            persist_directory=VECTORSTORE_PATH,
            embedding_function=embeddings
        )
        main_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        print("✅ InFlo book vectorstore loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to load vectorstore: {e}")
        print("App will continue without InFlo book context")
        return False

def get_main_retriever():
    """Get the main retriever for InFlo book context"""
    return main_retriever

def get_vectorstore():
    """Get the vectorstore instance"""
    return vectorstore

def is_vectorstore_available():
    """Check if vectorstore is available"""
    return main_retriever is not None

def get_user_interventions_vectorstore():
    """Get a separate vectorstore for user-generated interventions"""
    try:
        embeddings = get_embeddings()
        user_vectorstore = Chroma(
            collection_name="user_interventions",
            persist_directory=VECTORSTORE_PATH,
            embedding_function=embeddings
        )
        return user_vectorstore
    except Exception as e:
        print(f"❌ Failed to create user interventions vectorstore: {e}")
        raise e

# Initialize on import
initialize_vectorstore()
