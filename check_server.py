#!/usr/bin/env python3
"""Quick script to check if backend server is running"""
import requests
import sys

try:
    response = requests.get("http://localhost:8000/api/health", timeout=2)
    if response.status_code == 200:
        print("✅ Backend server is running!")
        print(f"Response: {response.json()}")
        sys.exit(0)
    else:
        print(f"❌ Backend returned status code: {response.status_code}")
        sys.exit(1)
except requests.exceptions.ConnectionError:
    print("❌ Backend server is NOT running!")
    print("\nTo start it, run:")
    print("  python run_app.py")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

