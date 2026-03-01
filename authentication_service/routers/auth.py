from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import schema
from database.db_config import get_db
from utils.auth import register_user, authenticate_user

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/register", response_model=schema.User, status_code=status.HTTP_201_CREATED)
async def register(user: schema.Signup, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    try:
        return register_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.post("/login", response_model=schema.Token)
async def login(user: schema.Login, db: Session = Depends(get_db)):
    """
    Login and get access token
    """
    token = authenticate_user(db, user.email, user.password)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    return {"access_token": token, "token_type": "bearer"}
