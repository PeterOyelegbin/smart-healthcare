from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import models, schema
from database.db_config import get_db
from utils.auth import get_current_user, password_update
from utils.responses import MessageResponse

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

@router.get("/me/profile", response_model=schema.User)
async def get_profile(current_user: models.User = Depends(get_current_user)):
    """
    Get current logged-in user's profile
    """
    return current_user

@router.patch("/me/password-update", response_model=MessageResponse)
async def update_password(user_data: schema.UpdatePassword, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Update current user's password
    """
    if user_data.new_password != user_data.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New passwords do not match")
    updated = password_update(db, current_user, user_data.old_password, user_data.new_password)
    if not updated:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password")
    return MessageResponse(message="Password updated successfully")
