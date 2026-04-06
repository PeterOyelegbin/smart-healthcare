from fastapi import HTTPException, status
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from uuid import uuid4
from decouple import config
from database.db_config import redis_client

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=config('ACCESS_TOKEN_EXPIRE_MINUTES', cast=int))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, config('SECRET_KEY'), algorithm=config('ALGORITHM'))

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=config('REFRESH_TOKEN_EXPIRE_DAYS', cast=int))
    jti = str(uuid4())
    to_encode.update({"exp": expire, "type": "refresh", "jti": jti})
    redis_client.setex(
        f"refresh:{jti}",
        int(timedelta(days=config('REFRESH_TOKEN_EXPIRE_DAYS', cast=int)).total_seconds()),
        data.get("sub")
    )
    return jwt.encode(to_encode, config('SECRET_KEY'), algorithm=config('ALGORITHM'))

def create_token_pair(data: dict) -> dict:
    return {
        "access_token": create_access_token(data),
        "refresh_token": create_refresh_token(data)
    }

def decode_token(token: str):
    try:
        payload = jwt.decode(token, config('SECRET_KEY'), algorithms=[config('ALGORITHM')])
        return payload
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token!")
    
def refresh_access_token(refresh_token: str):
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token type!")
        jti = payload.get("jti")
        if not redis_client.get(f"refresh:{jti}"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked, login again!")
        return create_access_token({"sub": payload.get("sub")})
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired, login again!")
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")

def get_expires_at(token: str) -> int:
    payload = jwt.decode(token, config('SECRET_KEY'), algorithms=[config('ALGORITHM')], options={"verify_exp": False})
    exp_timestamp = payload.get("exp")
    if exp_timestamp:
        expires_at = datetime.fromtimestamp(exp_timestamp)
        expires_in_seconds = int((expires_at - datetime.utcnow()).total_seconds())
        return max(1, expires_in_seconds)
    else:
        # Default expiration if not in token (30 minutes)
        return 30 * 60
