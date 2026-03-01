from fastapi import APIRouter, Depends, Path, HTTPException, status
from sqlalchemy.orm import Session
from database import models, schema
from database.db_config import get_db
from uuid import UUID
from utils.auth import require_admin
from utils.responses import MessageResponse

router = APIRouter(prefix="/api/v1/users", tags=["Admin"])

@router.get("/", response_model=list[schema.User])
async def get_all_users(admin: models.User = Depends(require_admin), db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Get all users (Admin only)
    """
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=schema.User)
async def get_user_by_id(admin: models.User = Depends(require_admin), user_id: UUID = Path(..., description="User ID to retrieve"), db: Session = Depends(get_db)):
    """
    Get user by ID (Admin only)
    """
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.patch("/{user_id}/toggle-status", response_model=MessageResponse)
async def toggle_user_status(activate: bool, admin: models.User = Depends(require_admin),
    user_id: UUID = Path(..., description="User ID"), db: Session = Depends(get_db)):
    """
    Activate or deactivate a user (Admin only)
    """
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.is_active == activate:
        status_text = "active" if activate else "deactivated"
        return MessageResponse(message=f"User is already {status_text}")
    user.is_active = activate
    db.commit()
    status_text = "activated" if activate else "deactivated"
    return MessageResponse(message=f"User {status_text} successfully")

@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(admin: models.User = Depends(require_admin), user_id: UUID = Path(..., description="User ID to delete"), db: Session = Depends(get_db)):
    """
    Delete a user (Admin only)
    """
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return MessageResponse(message="User deleted successfully")
