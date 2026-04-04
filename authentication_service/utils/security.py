from fastapi import HTTPException, status
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from decouple import config

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=config('ACCESS_TOKEN_EXPIRE_MINUTES', cast=int))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config('SECRET_KEY'), algorithm=config('ALGORITHM'))

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, config('SECRET_KEY'), algorithms=[config('ALGORITHM')])
        return payload.get("sub")  # user email
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token!")

def get_expires_at(token: str) -> int:
    payload = jwt.decode(token, config('SECRET_KEY'), algorithms=[config('ALGORITHM')], options={"verify_exp": False})
    exp_timestamp = payload.get("exp")
    if exp_timestamp:
        expires_at = datetime.fromtimestamp(exp_timestamp)
        expires_in_seconds = max(1, int((expires_at - datetime.utcnow()).total_seconds()))
    else:
        # Default expiration if not in token (3 hours)
        expires_in_seconds = 3 * 60 * 60
    return expires_in_seconds
