from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date
from database.models import Gender, MaritalStatus

class PatientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    email: EmailStr
    gender: Gender
    date_of_birth: date = Field(..., description="Date of birth in YYYY-MM-DD format")
    phone: str = Field(..., pattern=r'^\+?1?\d{9,15}$')
    address: str = Field(..., max_length=512)
    marital_status: MaritalStatus
    occupation: Optional[str] = None
    blood_type: Optional[str] = Field(None, pattern=r'^(A|B|AB|O)[+-]$')
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    
    @field_validator('date_of_birth')
    def validate_age(cls, v):
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 0:
            raise ValueError('Date of birth cannot be in the future')
        if age > 120:
            raise ValueError('Age cannot be greater than 120 years')
        return v
    
class PatientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=256)
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    address: Optional[str] = Field(None, max_length=512)
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    blood_type: Optional[str] = Field(None, pattern=r'^(A|B|AB|O)[+-]$')
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    marital_status: Optional[MaritalStatus] = None
    occupation: Optional[str] = None

class PatientResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    gender: Gender
    date_of_birth: date
    phone: str
    address: str
    marital_status: MaritalStatus
    occupation: Optional[str]
    blood_type: Optional[str]
    allergies: Optional[str]
    medical_conditions: Optional[str]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PatientListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    patients: List[PatientResponse]
