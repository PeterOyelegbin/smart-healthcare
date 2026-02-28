from pydantic import BaseModel, EmailStr, FileUrl
from typing import Optional
from uuid import UUID

class User(BaseModel):
    id: Optional[UUID]
    organisation: Optional[str]
    # cac_document: Optional[FileUrl]
    email: Optional[str]
    is_active: Optional[bool]
    verified: Optional[bool]
    is_admin: Optional[bool]

    class Config:
        from_attributes = True

class Signup(BaseModel):
    organisation: str
    email: EmailStr
    password: str

class Login(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
class UpdatePassword(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str
    