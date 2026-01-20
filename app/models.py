from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    name: str
    email: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    deadline: Optional[datetime] = None
    status: str = "in_progress"


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    assigned_to: Optional[int]
    status: str
    deadline: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    assigned_user: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    platform: str
    metrics: dict
    updated_at: datetime

