from fastapi import APIRouter, Response, Request, Depends
from sqlalchemy.orm import Session
from backend.auth import delete_session
from backend.database import get_db

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    session_token = request.cookies.get("session_token")
    if session_token:
        delete_session(session_token, db)
    
    response.delete_cookie("session_token")
    
    return {"message": "Logged out successfully"}


