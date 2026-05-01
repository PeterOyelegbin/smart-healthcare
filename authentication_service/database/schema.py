from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Optional, Literal, Annotated
from uuid import UUID

BusinessType = Literal["BUSINESS_NAME", "COMPANY", "INCORPORATED_TRUSTEES", "LIMITED_PARTNERSHIP", "LIMITED_LIABILITY_PARTNERSHIP"]

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
    business_type: list[BusinessType] = ["BUSINESS_NAME"]
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
    