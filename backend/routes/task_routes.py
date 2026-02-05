from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import User, Task, IDP, UserRole
from backend.schemas import TaskCreate, TaskUpdate, TaskResponse
from backend.auth import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskResponse)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    idp = db.query(IDP).filter(IDP.id == task_data.idp_id).first()
    if not idp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ИПР не найден"
        )
    
    if idp.mentor_id != current_user.id and idp.mentee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому ИПР"
        )
    
    task = Task(**task_data.dict())
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return TaskResponse.from_orm(task)

@router.get("/idp/{idp_id}", response_model=List[TaskResponse])
def get_tasks_by_idp(
    idp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    idp = db.query(IDP).filter(IDP.id == idp_id).first()
    if not idp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ИПР не найден"
        )
    
    if idp.mentor_id != current_user.id and idp.mentee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому ИПР"
        )
    
    # Просто возвращаем задачи без сортировки
    # Вся сортировка на фронтенде
    tasks = db.query(Task).filter(Task.idp_id == idp_id).all()
    return [TaskResponse.from_orm(task) for task in tasks]

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )
    
    idp = task.idp
    if idp.mentor_id != current_user.id and idp.mentee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этой задаче"
        )
    
    return TaskResponse.from_orm(task)

@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )
    
    idp = task.idp
    if idp.mentor_id != current_user.id and idp.mentee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этой задаче"
        )
    
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return TaskResponse.from_orm(task)

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )
    
    idp = task.idp
    if idp.mentor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только ментор может удалять задачи"
        )
    
    db.delete(task)
    db.commit()
    
    return {"message": "Задача удалена"}


