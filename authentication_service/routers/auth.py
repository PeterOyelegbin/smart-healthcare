from fastapi import APIRouter, Depends, Request, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from database import schema, models
from database.db_config import get_db, redis_client
from utils.compliance import verify_company
from utils.auth import register_user, authenticate_user, get_current_user, blacklist_token, password_reset
from utils.security import refresh_access_token, decode_token, create_password_reset_token
from utils.mail import send_password_reset_email

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/register", response_model=schema.User, status_code=status.HTTP_201_CREATED)
async def register(user: schema.Signup, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    try:
        if db.query(models.User).filter(models.User.email == user.email).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        verification = verify_company(user)
        if not verification.get("success"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company verification failed, check your details and try again.")    
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
    return {"access_token": token["access_token"], "refresh_token": token["refresh_token"], "token_type": "bearer"}

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """
    Refresh access token using a valid refresh token
    """
    try:
        new_tokens = refresh_access_token(refresh_token)
        return {"access_token": new_tokens, "token_type": "bearer"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during token refresh: {str(e)}")

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(refresh_token: str, request: Request, current_user: schema.User = Depends(get_current_user)):
    """
    Logout current user (blacklists the current access token)
    """
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid authorization header format. Expected 'Bearer <token>'")
        payload = decode_token(refresh_token)
        jti = payload.get("jti")
        if jti and redis_client.get(f"refresh:{jti}"):
            access_token = auth_header.split(" ")[1]
            blacklisted = blacklist_token(access_token)
            if not blacklisted:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to process logout request")
            redis_client.delete(f"refresh:{jti}")
        return {"message": "Successfully logged out"}        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during logout: {str(e)}")
    
@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(data: schema.ResetPassword, bg_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Request password reset - sends email with reset URL containing reset token
    """
    try:
        existing_user = db.query(models.User).filter(models.User.email == data.email).first()
        if not existing_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this email does not exist")
        reset_token = create_password_reset_token({"sub": data.email})
        # Send password reset email in background
        bg_tasks.add_task(send_password_reset_email, existing_user.business_name, existing_user.email, reset_token)
        return {"message": "Password reset instructions sent to your email"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during password reset: {str(e)}")
    
@router.post("/confirm-password", status_code=status.HTTP_200_OK)
async def confirm_password(data: schema.ConfirmPassword, db: Session = Depends(get_db)):
    """
    Confirm password reset using token
    """
    try:
        payload = decode_token(data.token)
        user_email = payload.get("sub")
        user = db.query(models.User).filter(models.User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if data.new_password != data.confirm_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password and confirm password do not match")
        updated_user = password_reset(db, user, data.new_password)
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update password")
        return {"message": "Password reset successful"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during password reset: {str(e)}")
    