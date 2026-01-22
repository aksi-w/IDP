from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, UserRole
from backend.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from backend.auth import verify_password, create_session, hash_password, delete_session

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = None
    
    if login_data.email and login_data.password:
        user = db.query(User).filter(
            User.email == login_data.email,
            User.role == UserRole.MENTOR
        ).first()
        
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
    
    elif login_data.access_code:
        user = db.query(User).filter(
            User.access_code == login_data.access_code,
            User.role == UserRole.MENTEE
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный код доступа"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать email+password или access_code"
        )
    
    session_token = create_session(user.id, db)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=86400
    )
    
    return TokenResponse(
        access_token=session_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )

@router.post("/register", response_model=UserResponse)
def register_mentor(
    register_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.email == register_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    mentor = User(
        full_name=register_data.full_name,
        email=register_data.email,
        password_hash=hash_password(register_data.password),
        role=UserRole.MENTOR,
        position=register_data.position,
        grade=register_data.grade
    )
    db.add(mentor)
    db.commit()
    db.refresh(mentor)
    
    return UserResponse.from_orm(mentor)

