from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
import os

from app.database import get_db, User, Task
from app.models import UserCreate, UserResponse, TaskCreate, TaskUpdate, TaskResponse
from app.routers import analytics, tasks, ai_agent

logger = logging.getLogger(__name__)

app = FastAPI(title="Arcus Analytics & Task Management", version="1.0.0")

# Log startup info
logger.info("=" * 60)
logger.info("Starting Arcus Analytics & Task Management API")
logger.info(f"Environment: {os.environ.get('ENVIRONMENT', 'development')}")
logger.info(f"PORT: {os.environ.get('PORT', '8000')}")
logger.info("=" * 60)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(ai_agent.router, prefix="/api/agent", tags=["ai-agent"])


@app.get("/")
async def root():
    """Root endpoint - basic API info"""
    return {
        "message": "Arcus Analytics & Task Management API",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "agent_command": "/api/agent/command",
            "capabilities": "/api/agent/capabilities"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint - used by Render to verify service is running"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Arcus Analytics & Task Management API",
        "version": "1.0.0"
    }

@app.get("/health")
async def simple_health():
    """Simple health check (alternative endpoint)"""
    return {"status": "ok"}

