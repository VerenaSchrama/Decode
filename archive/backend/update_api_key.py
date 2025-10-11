#!/usr/bin/env python3
"""
Helper script to update the Supabase API key
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def update_api_key():
    """Update the Supabase API key in .env file"""
    
    print("🔑 Supabase API Key Update Helper")
    print("=" * 40)
    
    # Show current values
    print("\n📋 Current Configuration:")
    print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
    print(f"SUPABASE_ANON_KEY: {os.getenv('SUPABASE_ANON_KEY')[:20]}...")
    
    print("\n🔍 Issue Identified:")
    print("✅ URL is correct: https://qyydgmcfrfezdcejqxgo.supabase.co")
    print("❌ API key is invalid: This key is from the old project")
    
    print("\n📋 Next Steps:")
    print("1. Go to your Supabase dashboard: https://supabase.com/dashboard")
    print("2. Select project: qyydgmcfrfezdcejqxgo")
    print("3. Go to Settings → API")
    print("4. Copy the 'anon public' key")
    print("5. Update the .env file with the new key")
    
    print("\n🔧 Manual Update Instructions:")
    print("1. Open .env file in your editor")
    print("2. Replace the SUPABASE_ANON_KEY value")
    print("3. Save the file")
    print("4. Run: python test_connection.py")
    
    print("\n📝 Example .env format:")
    print("SUPABASE_URL=https://qyydgmcfrfezdcejqxgo.supabase.co")
    print("SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    
    # Check if user wants to update automatically
    print("\n🤖 Automatic Update:")
    print("If you have the new API key, you can update it automatically.")
    print("Enter the new API key (or press Enter to skip):")
    
    new_key = input("New API Key: ").strip()
    
    if new_key and new_key.startswith('eyJ'):
        # Update the .env file
        env_file = Path('.env')
        if env_file.exists():
            content = env_file.read_text()
            # Replace the old key with the new one
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('SUPABASE_ANON_KEY='):
                    lines[i] = f'SUPABASE_ANON_KEY={new_key}'
                    break
            
            # Write back to file
            env_file.write_text('\n'.join(lines))
            print("✅ API key updated successfully!")
            
            # Test the connection
            print("\n🧪 Testing new connection...")
            try:
                from supabase import create_client
                client = create_client(os.getenv('SUPABASE_URL'), new_key)
                result = client.table('InterventionsBASE').select('count').execute()
                print("✅ Connection successful!")
                print(f"InterventionsBASE table accessible: {result}")
                return True
            except Exception as e:
                print(f"❌ Connection test failed: {e}")
                return False
        else:
            print("❌ .env file not found")
            return False
    else:
        print("⏭️  Skipping automatic update")
        print("\n📋 Please update the API key manually and run:")
        print("python test_connection.py")
        return False

if __name__ == "__main__":
    update_api_key()

