#!/usr/bin/env python3
"""
Build vectorstore from database data instead of CSV
Creates embeddings for interventions and habits from Supabase database
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from llm import get_embeddings

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.supabase_models import supabase_client

load_dotenv()

def build_interventions_vectorstore():
    """Build vectorstore from interventions and habits in database"""
    
    print("🔄 Building vectorstore from database data...")
    
    try:
        # Get all interventions with their habits
        interventions_result = supabase_client.client.table('interventions').select('*, habits(*)').execute()
        
        if not interventions_result.data:
            print("❌ No interventions found in database")
            return False
        
        print(f"📊 Found {len(interventions_result.data)} interventions in database")
        
        # Create documents for vectorstore
        documents = []
        
        for intervention in interventions_result.data:
            # Create intervention document
            intervention_text = f"""
            Intervention: {intervention['name']}
            Profile: {intervention['profile']}
            Scientific Source: {intervention['scientific_source']}
            """
            
            # Add habits to the text
            if intervention.get('habits'):
                intervention_text += "\nHabits:\n"
                for i, habit in enumerate(intervention['habits'], 1):
                    intervention_text += f"{i}. {habit['name']}\n"
            
            # Create document
            doc = Document(
                page_content=intervention_text.strip(),
                metadata={
                    "intervention_id": intervention['id'],
                    "intervention_name": intervention['name'],
                    "type": "intervention",
                    "scientific_source": intervention['scientific_source'],
                    "habit_count": len(intervention.get('habits', []))
                }
            )
            documents.append(doc)
            
            print(f"  📝 Created document for: {intervention['name']}")
        
        # Create separate documents for individual habits
        habits_result = supabase_client.client.table('habits').select('*, interventions(*)').execute()
        
        if habits_result.data:
            print(f"📊 Found {len(habits_result.data)} habits in database")
            
            for habit in habits_result.data:
                habit_text = f"""
                Habit: {habit['name']}
                Intervention: {habit['interventions'][0]['name'] if habit.get('interventions') else 'Unknown'}
                Scientific Source: {habit['scientific_source']}
                """
                
                doc = Document(
                    page_content=habit_text.strip(),
                    metadata={
                        "habit_id": habit['id'],
                        "habit_name": habit['name'],
                        "intervention_id": habit['intervention_id'],
                        "intervention_name": habit['interventions'][0]['name'] if habit.get('interventions') else 'Unknown',
                        "type": "habit",
                        "scientific_source": habit['scientific_source']
                    }
                )
                documents.append(doc)
        
        print(f"📚 Created {len(documents)} documents for vectorstore")
        
        # Build vectorstore
        embeddings = get_embeddings()
        vectorstore_path = "data/vectorstore/database_chroma"
        
        # Create directory if it doesn't exist
        Path(vectorstore_path).mkdir(parents=True, exist_ok=True)
        
        print(f"🔨 Building vectorstore at {vectorstore_path}...")
        
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=vectorstore_path,
            collection_name="interventions_and_habits"
        )
        
        # Persist the vectorstore
        vectorstore.persist()
        
        print("✅ Vectorstore built successfully!")
        
        # Test the vectorstore
        print("\n🧪 Testing vectorstore...")
        test_query = "blood sugar control"
        results = vectorstore.similarity_search(test_query, k=3)
        
        print(f"🔍 Test query: '{test_query}'")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.metadata.get('intervention_name', 'Unknown')} (score: {result.metadata.get('type', 'Unknown')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to build vectorstore: {e}")
        return False

def update_vectorstore_references():
    """Update code to use the new database-based vectorstore"""
    
    print("\n📝 Updating vectorstore references...")
    
    # Update retrievers/vectorstores.py
    vectorstores_file = "retrievers/vectorstores.py"
    
    if os.path.exists(vectorstores_file):
        print(f"📄 Updating {vectorstores_file}...")
        
        # Read current file
        with open(vectorstores_file, 'r') as f:
            content = f.read()
        
        # Update the vectorstore path
        new_content = content.replace(
            'VECTORSTORE_PATH = os.path.join(BASE_DIR, "data", "vectorstore", "chroma")',
            'VECTORSTORE_PATH = os.path.join(BASE_DIR, "data", "vectorstore", "database_chroma")'
        )
        
        # Write updated content
        with open(vectorstores_file, 'w') as f:
            f.write(new_content)
        
        print(f"✅ Updated {vectorstores_file}")
    
    print("✅ Vectorstore references updated!")

if __name__ == "__main__":
    print("🚀 Database Vectorstore Builder")
    print("=" * 40)
    
    # Build vectorstore from database
    success = build_interventions_vectorstore()
    
    if success:
        # Update references
        update_vectorstore_references()
        
        print("\n🎉 Database vectorstore setup completed!")
        print("📋 Next steps:")
        print("1. Update intervention matcher to use database")
        print("2. Test the complete system")
        print("3. Remove CSV dependencies")
    else:
        print("\n❌ Vectorstore build failed!")
        print("Please check the errors above and try again.")
