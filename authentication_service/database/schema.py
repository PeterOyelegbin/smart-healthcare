from pydantic import BaseModel, EmailStr, FileUrl, StringConstraints
from typing import Optional, Annotated
from uuid import UUID

class User(BaseModel):
    id: Optional[UUID]
    business_name: Optional[str]
    registration_number: Optional[str]
    email: Optional[str]
    is_consent: Optional[bool]
    is_active: Optional[bool]
    verified: Optional[bool]
    is_admin: Optional[bool]

    class Config:
        from_attributes = True

class Signup(BaseModel):
    business_name: str
    registration_number: str
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=6, max_length=50)]
    is_consent: bool

class Login(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    
class UpdatePassword(BaseModel):
    old_password: str
    new_password: Annotated[str, StringConstraints(min_length=6, max_length=50)]
    confirm_password: str
    
class ResetPassword(BaseModel):
    email: EmailStr

class ConfirmPassword(BaseModel):
    token: str
    new_password: Annotated[str, StringConstraints(min_length=6, max_length=50)]
    confirm_password: str
    