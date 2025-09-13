import os
import pandas as pd
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()

# Define paths
CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "strategies.csv")
PERSIST_DIR = os.path.join(os.path.dirname(__file__), "data", "vectorstore", "strategies_chroma")
COLLECTION_NAME = "strategies"

# Load data from CSV
try:
    df = pd.read_csv(CSV_PATH, sep=',')
except FileNotFoundError:
    print(f"Error: Could not find the CSV file at {CSV_PATH}")
    exit()

# Map new English column names to expected structure
column_mapping = {
    'Strategy Name': 'Strategie naam',
    'What will you be doing': 'Uitleg', 
    'Why does it work': 'Waarom',
    'Symptoms': 'Verhelpt klachten bij',
    'Sources': 'Bron(nen)',
    'Tips for today': 'Praktische tips'
}

# Rename columns to match expected structure
df = df.rename(columns=column_mapping)

# Clean the data - remove rows where strategy name is empty or NaN
df = df.dropna(subset=['Strategie naam'])
df = df[df['Strategie naam'].str.strip() != '']

# Fill NaN values with empty strings for text columns
text_columns = ['Uitleg', 'Waarom', 'Verhelpt klachten bij', 'Bron(nen)', 'Praktische tips']
for col in text_columns:
    if col in df.columns:
        df[col] = df[col].fillna('')

# Create LangChain Documents
documents = []
for _, row in df.iterrows():
    # Skip rows with invalid strategy names
    if pd.isna(row['Strategie naam']) or str(row['Strategie naam']).strip() == '':
        continue
        
    # A more descriptive content for better retrieval
    content = (
        f"Strategy '{row['Strategie naam']}' is designed to help with the following symptoms and goals: {row['Verhelpt klachten bij']}. "
        f"Here is an explanation of the strategy: {row['Uitleg']}. "
        f"This is why it works: {row['Waarom']}. "
        f"Here are some practical tips: {row['Praktische tips']}."
    )
    metadata = {
        "strategy_name": row['Strategie naam'],
        "explanation": row['Uitleg'],
        "why": row['Waarom'],
        "helps_with": row['Verhelpt klachten bij'],
        "sources": row['Bron(nen)'],
        "practical_tips": row['Praktische tips']
    }
    documents.append(Document(page_content=content, metadata=metadata))

# Initialize OpenAI embeddings
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY not found in environment variables.")
    exit()
embedding_model = OpenAIEmbeddings(api_key=api_key)

# Create and persist the vector store
vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embedding_model,
    collection_name=COLLECTION_NAME,
    persist_directory=PERSIST_DIR,
)