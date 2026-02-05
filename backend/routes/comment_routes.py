from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from backend.database import get_db
from backend.models import TaskComment, Task, User
from backend.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/comments", tags=["Comments"])

class CommentCreate(BaseModel):
    task_id: int
    comment: str

class CommentResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    comment: str
    created_at: datetime
    user_name: str
    
    class Config:
        from_attributes = True

@router.post("/", response_model=CommentResponse)
def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == comment_data.task_id).first()
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
    
    comment = TaskComment(
        task_id=comment_data.task_id,
        user_id=current_user.id,
        comment=comment_data.comment
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return CommentResponse(
        id=comment.id,
        task_id=comment.task_id,
        user_id=comment.user_id,
        comment=comment.comment,
        created_at=comment.created_at,
        user_name=current_user.full_name
    )

@router.get("/task/{task_id}", response_model=List[CommentResponse])
def get_task_comments(
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
    
    comments = db.query(TaskComment).filter(
        TaskComment.task_id == task_id
    ).order_by(TaskComment.created_at).all()
    
    result = []
    for comment in comments:
        user = db.query(User).filter(User.id == comment.user_id).first()
        result.append(CommentResponse(
            id=comment.id,
            task_id=comment.task_id,
            user_id=comment.user_id,
            comment=comment.comment,
            created_at=comment.created_at,
            user_name=user.full_name if user else "Неизвестно"
        ))
    
    return result

class CommentUpdate(BaseModel):
    comment: str

@router.patch("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Редактировать комментарий (только автор)"""
    comment = db.query(TaskComment).filter(TaskComment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комментарий не найден"
        )
    
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете редактировать только свои комментарии"
        )
    
    # Обновляем текст комментария
    comment.comment = comment_data.comment
    db.commit()
    db.refresh(comment)
    
    # Получаем имя пользователя для ответа
    user = db.query(User).filter(User.id == comment.user_id).first()
    
    return CommentResponse(
        id=comment.id,
        task_id=comment.task_id,
        user_id=comment.user_id,
        comment=comment.comment,
        created_at=comment.created_at,
        user_name=user.full_name if user else "Неизвестно"
    )

@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить комментарий (только автор)"""
    comment = db.query(TaskComment).filter(TaskComment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комментарий не найден"
        )
    
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете удалять только свои комментарии"
        )
    
    db.delete(comment)
    db.commit()
    
    return {"message": "Комментарий удален"}


