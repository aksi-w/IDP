from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session as DBSession
import secrets
import string
from datetime import datetime, timedelta
from backend.database import get_db
from backend.models import User, Session

def hash_password(password: str) -> str:
    return f"hashed_{password}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return f"hashed_{plain_password}" == hashed_password

def generate_access_code() -> str:
    random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    return f"idp-{random_part}"

def create_session(user_id: int, db: DBSession = None) -> str:
    if not db:
        return secrets.token_urlsafe(32)
    
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    session = Session(
        token=session_token,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(session)
    db.commit()
    
    return session_token

def get_current_user(request: Request, db: DBSession = Depends(get_db)) -> User:
    session_token = request.cookies.get("session_token")
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.replace("Bearer ", "")
    
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    session = db.query(Session).filter(
        Session.token == session_token,
        Session.is_active == True,
        Session.expires_at > datetime.utcnow()
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    user = db.query(User).filter(User.id == session.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

def delete_session(session_token: str, db: DBSession = None):
    if db and session_token:
        session = db.query(Session).filter(Session.token == session_token).first()
        if session:
            session.is_active = False
            db.commit()

