from pydantic import BaseModel, EmailStr, StringConstraints, field_validator
from typing import Optional, Literal, Annotated
from datetime import datetime
from uuid import UUID

BusinessType = Literal["BUSINESS_NAME", "COMPANY", "INCORPORATED_TRUSTEES", "LIMITED_PARTNERSHIP", "LIMITED_LIABILITY_PARTNERSHIP"]

class User(BaseModel):
    id: UUID
    business_name: str
    registration_number: str
    email: str
    is_consent: bool
    is_active: bool
    verified: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class Signup(BaseModel):
    business_name: str
    registration_number: str
    business_type: list[BusinessType] = ["BUSINESS_NAME"]
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=6)]
    is_consent: bool

    @field_validator("password")
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

class Login(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    
class UpdatePassword(BaseModel):
    old_password: str
    new_password: Annotated[str, StringConstraints(min_length=6)]
    confirm_password: str

    @field_validator("new_password")
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
    
class ResetPassword(BaseModel):
    email: EmailStr

class ConfirmPassword(BaseModel):
    token: str
    new_password: Annotated[str, StringConstraints(min_length=6)]
    confirm_password: str

    @field_validator("new_password")
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
    