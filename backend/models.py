from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum
from backend.database import Base

class UserRole(str, enum.Enum):
    MENTOR = "mentor"
    MENTEE = "mentee"

class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class IDPStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=True)
    role = Column(Enum(UserRole), nullable=False)
    access_code = Column(String, unique=True, nullable=True)
    position = Column(String, nullable=True)
    grade = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    mentored_idps = relationship("IDP", foreign_keys="IDP.mentor_id", back_populates="mentor")
    mentee_idps = relationship("IDP", foreign_keys="IDP.mentee_id", back_populates="mentee")

class IDP(Base):
    __tablename__ = "idps"
    
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mentee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(IDPStatus), default=IDPStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    mentor = relationship("User", foreign_keys=[mentor_id], back_populates="mentored_idps")
    mentee = relationship("User", foreign_keys=[mentee_id], back_populates="mentee_idps")
    tasks = relationship("Task", back_populates="idp", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    idp_id = Column(Integer, ForeignKey("idps.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(String, nullable=True)
    deadline = Column(DateTime, nullable=True)
    linked_skills = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    idp = relationship("IDP", back_populates="tasks")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User")

class TaskTemplate(Base):
    __tablename__ = "task_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False, index=True)
    skill_name = Column(String, nullable=False)
    level = Column(Integer, nullable=True)
    goal = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    criteria = Column(Text, nullable=True)
    duration_weeks = Column(Integer, nullable=True)
    source = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class TaskComment(Base):
    __tablename__ = "task_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    task = relationship("Task", back_populates="comments")
    user = relationship("User")


