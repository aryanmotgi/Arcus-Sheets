#!/usr/bin/env python3
"""
Run the Arcus Analytics & Task Management App
"""
import uvicorn
from pathlib import Path

if __name__ == "__main__":
    # Run the FastAPI app
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app", "src"]
    )

