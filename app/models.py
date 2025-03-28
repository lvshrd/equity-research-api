# app/models.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Request/Response Models
class TaskCreate(BaseModel):
    company_id: str

class TaskStatus(BaseModel):
    task_id: str
    company_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    report_path: Optional[str]

class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None

class UserLogin(BaseModel):
    """User login request model"""
    username: str
    password: str