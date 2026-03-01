from sqlalchemy.orm import Session
from database.models import User
from database.db_config import get_db
from fastapi import Depends, security, HTTPException, status
from .security import hash_password, verify_password, create_access_token, decode_access_token

oauth2_scheme = security.HTTPBearer()

def register_user(db: Session, user_data):
    hashed_pw = hash_password(user_data.password)
    user = User(organisation=user_data.organisation, email=user_data.email, password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password!")
    if not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password!")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive, contact support!")
    token = create_access_token({"sub": user.email})
    return token

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        user_email = decode_access_token(token.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        return user
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials!")
    
def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user or not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user

def password_update(db: Session, user: User, old_password: str, new_password: str):
    if not verify_password(old_password, user.password):
        return None
    hashed_pw = hash_password(new_password)
    user.password = hashed_pw
    db.commit()
    db.refresh(user)
    return user
