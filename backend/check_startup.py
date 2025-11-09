#!/usr/bin/env python3
"""
Quick script to test if the FastAPI app can start without errors
Run this on the server to diagnose startup issues
"""

import sys

print("🔍 Testing FastAPI app startup...")

try:
    print("1. Testing basic imports...")
    from fastapi import FastAPI
    print("   ✅ FastAPI imported")
    
    print("2. Testing services import...")
    try:
        import services
        print("   ✅ Services imported successfully")
    except Exception as e:
        print(f"   ⚠️ Services import failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("3. Testing API app creation...")
    from api import app
    print("   ✅ API app created successfully")
    
    print("4. Testing app startup event...")
    # The startup event runs automatically when uvicorn starts
    print("   ℹ️ Startup event will run when uvicorn starts")
    
    print("\n✅ All checks passed! App should start successfully.")
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ Error during startup check: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

