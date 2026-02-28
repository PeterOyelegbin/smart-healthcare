from fastapi import FastAPI, Depends, Path, HTTPException, Response
from sqlalchemy.orm import Session
from database import models, schema
from database.db_config import get_db
from uuid import UUID
from utils.auth import register_user, authenticate_user, password_update, get_current_user


# initialize the application and modify default api details
app = FastAPI(
    title="Smart Healthcare Authentication Service - FastAPI",
    description="Authentication service for managing user authentication and authorization",
    version="0.0.1",
    # openapi_url="/docs",
    contact={
        "name": "Peter Oyelegbin",
        "email": "peteroyelegbin@gmail.com",
    },
    license_info={
        "name": "MIT",
    },
)


# user registration endpoint
@app.post("/api/v1/auth/register", response_model=schema.User)
async def register(user: schema.Signup, db: Session = Depends(get_db)):
    return register_user(db, user)


# user login endpoint
@app.post("/api/v1/auth/login", response_model=schema.Token)
async def login(user: schema.Login, db: Session = Depends(get_db)):
    try:
        token = authenticate_user(db, user.email, user.password)
        if not token:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

# get all users endpoint
@app.get("/api/v1/users", response_model=list[schema.User])
async def getUsers(auth_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        if not auth_user or not auth_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        users = db.query(models.User).all()
        if users == []:
            return Response(status_code=200, content='{"message": "No users found"}', media_type="application/json")   
        return users
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

# get user by id endpoint
@app.get("/api/v1/users/{user_id}", response_model=schema.User)
async def getUser(auth_user: models.User = Depends(get_current_user), user_id: UUID = Path(..., description="user ID you want to retrieve"), db: Session = Depends(get_db)):
    try:
        if not auth_user or not auth_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        user = db.get(models.User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.get("/api/v1/users/me/profile", response_model=schema.User)
async def getProfile(auth_user: models.User = Depends(get_current_user)):
    try:
        if not auth_user:
            raise HTTPException(status_code=401, detail="Invalid token!")
        return auth_user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


# update current logged-in user password endpoint
@app.patch("/api/v1/users/me/password-update")
async def updatePassword(user_data: schema.UpdatePassword, auth_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        if not auth_user:
            raise HTTPException(status_code=401, detail="Invalid token!")
        if user_data.new_password != user_data.confirm_password:
            raise HTTPException(status_code=400, detail="New passwords do not match")
        updated_passwd = password_update(db, auth_user, user_data.old_password, user_data.new_password)
        if not updated_passwd:
            raise HTTPException(status_code=400, detail="Invalid old password")
        db.commit()
        db.refresh(auth_user)
        return Response(status_code=200, content='{"message": "Password updated successfully"}', media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

# activate user by id endpoint
@app.patch("/api/v1/users/{user_id}/activate")
async def activateUser(auth_user: models.User = Depends(get_current_user), user_id: UUID = Path(..., description="user ID you want to activate"), db: Session = Depends(get_db)):
    try:
        if not auth_user or not auth_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        user = db.get(models.User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.is_active:
            return Response(status_code=200, content='{"message": "User is already active"}', media_type="application/json")
        user.is_active = True
        db.commit()
        db.refresh(user)
        return Response(status_code=200, content='{"message": "User activated successfully"}', media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

# deactivate user by id endpoint
@app.patch("/api/v1/users/{user_id}/deactivate")
async def deactivateUser(auth_user: models.User = Depends(get_current_user), user_id: UUID = Path(..., description="user ID you want to deactivate"), db: Session = Depends(get_db)):
    try:
        if not auth_user or not auth_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        user = db.get(models.User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not user.is_active:
            return Response(status_code=200, content='{"message": "User is already deactivated"}', media_type="application/json")
        user.is_active = False
        db.commit()
        db.refresh(user)
        return Response(status_code=200, content='{"message": "User deactivated successfully"}', media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

# delete user by id endpoint
@app.delete("/api/v1/users/{user_id}")
async def deleteUser(auth_user: models.User = Depends(get_current_user), user_id: UUID = Path(..., description="user ID you want to delete"), db: Session = Depends(get_db)):
    try:
        if not auth_user or not auth_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        user = db.get(models.User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(user)
        db.commit()
        return Response(status_code=200, content='{"message": "User deleted successfully"}', media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    