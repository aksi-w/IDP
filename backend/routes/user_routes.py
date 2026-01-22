from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User
from backend.auth import get_current_user
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter(prefix="/api/users", tags=["Users"])

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    position: Optional[str] = None
    grade: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    position: Optional[str] = None
    grade: Optional[str] = None
    access_code: Optional[str] = None
    
    class Config:
        from_attributes = True

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return UserResponse(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        role=current_user.role.value,
        position=current_user.position,
        grade=current_user.grade,
        access_code=current_user.access_code
    )

@router.patch("/me", response_model=UserResponse)
def update_current_user_profile(
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name
    
    if update_data.email is not None:
        existing_user = db.query(User).filter(
            User.email == update_data.email,
            User.id != current_user.id
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже используется другим пользователем"
            )
        
        current_user.email = update_data.email
    
    if update_data.position is not None:
        current_user.position = update_data.position
    
    if update_data.grade is not None:
        current_user.grade = update_data.grade
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        role=current_user.role.value,
        position=current_user.position,
        grade=current_user.grade,
        access_code=current_user.access_code
    )


