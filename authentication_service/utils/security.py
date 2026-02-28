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
    payload = jwt.decode(token, config('SECRET_KEY'), algorithms=[config('ALGORITHM')])
    return payload.get("sub")  # user email
