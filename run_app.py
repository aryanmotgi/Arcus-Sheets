#!/usr/bin/env python3
"""
Run the Arcus Analytics & Task Management App
"""
import os
import uvicorn
from pathlib import Path

if __name__ == "__main__":
    # Get port from environment (Render sets PORT, default to 8000 for local)
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"  # Must be 0.0.0.0 for Render (not localhost)
    
    # Only enable reload in development (not on Render)
    reload = os.environ.get("ENVIRONMENT") != "production" and os.environ.get("RENDER") is None
    
    print(f"🚀 Starting FastAPI server...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Reload: {reload}")
    print(f"   Environment: {os.environ.get('ENVIRONMENT', 'development')}")
    
    # Run the FastAPI app
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        reload_dirs=["app", "src"] if reload else None
    )

