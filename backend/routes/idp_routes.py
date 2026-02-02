# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import User, IDP, UserRole, IDPStatus
from backend.schemas import IDPCreate, IDPResponse, UserResponse
from backend.auth import get_current_user, generate_access_code, hash_password

router = APIRouter(prefix="/api/idps", tags=["IDPs"])

@router.post("/", response_model=IDPResponse)
def create_idp(
    idp_data: IDPCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.MENTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менторы могут создавать ИПР"
        )
    
    existing_mentee = db.query(User).filter(User.email == idp_data.mentee_email).first()
    
    if existing_mentee:
        mentee = existing_mentee
        
        if mentee.full_name != idp_data.mentee_full_name:
            mentee.full_name = idp_data.mentee_full_name
        
        if idp_data.mentee_position:
            mentee.position = idp_data.mentee_position
        if idp_data.mentee_grade:
            mentee.grade = idp_data.mentee_grade
        
        # если у менти нет кода доступа — генерируем и сохраняем
        if not mentee.access_code:
            mentee.access_code = generate_access_code()
        
        active_idp = db.query(IDP).filter(
            IDP.mentee_id == mentee.id,
            IDP.mentor_id == current_user.id,
            IDP.status == IDPStatus.ACTIVE
        ).first()
        
        if active_idp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"У {mentee.full_name} уже есть активный ИПР с вами. Закройте предыдущий ИПР перед созданием нового."
            )
    else:
        access_code = generate_access_code()
        mentee = User(
            full_name=idp_data.mentee_full_name,
            email=idp_data.mentee_email,
            role=UserRole.MENTEE,
            access_code=access_code,
            position=idp_data.mentee_position,
            grade=idp_data.mentee_grade
        )
        db.add(mentee)
        db.flush()
    
    idp = IDP(
        mentor_id=current_user.id,
        mentee_id=mentee.id
    )
    db.add(idp)
    db.commit()
    db.refresh(idp)
    
    return IDPResponse.from_orm(idp)

@router.get("/", response_model=List[IDPResponse])
def get_my_idps(
    include_all: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == UserRole.MENTOR:
        query = db.query(IDP).filter(IDP.mentor_id == current_user.id)
        if not include_all:
            query = query.filter(IDP.status == IDPStatus.ACTIVE)
        idps = query.all()
    else:
        query = db.query(IDP).filter(IDP.mentee_id == current_user.id)
        if not include_all:
            query = query.filter(IDP.status == IDPStatus.ACTIVE)
        idps = query.all()
    
    return [IDPResponse.from_orm(idp) for idp in idps]

@router.get("/{idp_id}", response_model=IDPResponse)
def get_idp(
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
    
    return IDPResponse.from_orm(idp)

@router.get("/mentees/list", response_model=List[UserResponse])
def get_my_mentees(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.MENTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступно только для менторов"
        )
    
    idps = db.query(IDP).filter(
        IDP.mentor_id == current_user.id,
        IDP.status == IDPStatus.ACTIVE
    ).all()
    mentees = [idp.mentee for idp in idps]
    
    return [UserResponse.from_orm(mentee) for mentee in mentees]

@router.patch("/{idp_id}/close")
def close_idp(
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
    
    if idp.mentor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только ментор может закрыть ИПР"
        )
    
    idp.status = IDPStatus.COMPLETED
    db.commit()
    
    return {"message": "ИПР закрыт"}

@router.delete("/{idp_id}")
def delete_idp(
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
    
    if idp.mentor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только ментор может удалить ИПР"
        )
    
    db.delete(idp)
    db.commit()
    
    return {"message": "ИПР удален"}


