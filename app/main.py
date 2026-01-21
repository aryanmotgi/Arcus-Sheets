from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db, User, Task
from app.models import UserCreate, UserResponse, TaskCreate, TaskUpdate, TaskResponse
from app.routers import analytics, tasks, ai_agent

app = FastAPI(title="Arcus Analytics & Task Management", version="1.0.0")

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
    return {"message": "Arcus Analytics & Task Management API"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

