# -*- coding: utf-8 -*-
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from backend.models import UserRole, TaskStatus, IDPStatus

class UserBase(BaseModel):
    full_name: str
    email: Optional[str] = None
    role: UserRole

class UserCreate(UserBase):
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    access_code: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: Optional[str] = None
    access_code: Optional[str] = None
    password: Optional[str] = None

class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str
    position: Optional[str] = None
    grade: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: Optional[str] = None
    deadline: Optional[datetime] = None
    linked_skills: Optional[dict] = None

class TaskCreate(TaskBase):
    idp_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[str] = None
    deadline: Optional[datetime] = None
    linked_skills: Optional[dict] = None

class TaskResponse(TaskBase):
    id: int
    idp_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class IDPBase(BaseModel):
    status: IDPStatus = IDPStatus.ACTIVE

class IDPCreate(BaseModel):
    mentee_full_name: str
    mentee_email: str
    mentee_position: Optional[str] = None
    mentee_grade: Optional[str] = None

class IDPResponse(IDPBase):
    id: int
    mentor_id: int
    mentee_id: int
    created_at: datetime
    mentor: UserResponse
    mentee: UserResponse
    tasks: List[TaskResponse] = []
    
    class Config:
        from_attributes = True


