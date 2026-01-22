from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from backend.database import get_db
from backend.models import TaskTemplate, User
from backend.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/templates", tags=["Task Templates"])

class TaskTemplateResponse(BaseModel):
    id: int
    category: str
    skill_name: str
    level: int | None
    goal: str | None
    description: str | None
    criteria: str | None
    duration_weeks: int | None
    source: str
    
    class Config:
        from_attributes = True

class CategoryResponse(BaseModel):
    category: str
    count: int

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    categories = db.query(
        TaskTemplate.category,
        func.count(TaskTemplate.id).label('count')
    ).group_by(TaskTemplate.category).order_by(TaskTemplate.category).all()
    
    return [{"category": cat, "count": count} for cat, count in categories]

@router.get("/by-category/{category}", response_model=List[TaskTemplateResponse])
def get_templates_by_category(
    category: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    templates = db.query(TaskTemplate).filter(
        TaskTemplate.category == category
    ).order_by(TaskTemplate.skill_name, TaskTemplate.level).all()
    
    if not templates:
        return []
    
    return [TaskTemplateResponse.from_orm(t) for t in templates]

@router.get("/search", response_model=List[TaskTemplateResponse])
def search_templates(
    q: str = "",
    category: str = None,
    level: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(TaskTemplate)
    
    if q:
        search_pattern = f"%{q}%"
        query = query.filter(
            (TaskTemplate.skill_name.ilike(search_pattern)) |
            (TaskTemplate.goal.ilike(search_pattern)) |
            (TaskTemplate.description.ilike(search_pattern))
        )
    
    if category:
        query = query.filter(TaskTemplate.category == category)
    
    if level is not None:
        query = query.filter(TaskTemplate.level == level)
    
    templates = query.order_by(TaskTemplate.category, TaskTemplate.skill_name).all()
    
    return [TaskTemplateResponse.from_orm(t) for t in templates]

@router.get("/{template_id}", response_model=TaskTemplateResponse)
def get_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    template = db.query(TaskTemplate).filter(TaskTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Шаблон не найден"
        )
    
    return TaskTemplateResponse.from_orm(template)

