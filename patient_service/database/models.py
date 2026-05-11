from .db_config import Base
from enum import Enum as PyEnum
from datetime import datetime
from sqlalchemy import Column, UUID, Enum as SQLEnum, String, Text, Date, DateTime, Boolean
from uuid import uuid4

# create database model
class Gender(str, PyEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class MaritalStatus(str, PyEnum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"

class Patient(Base):
    __tablename__ = 'patients'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(256), nullable=False)
    email = Column(String(256), unique=True, index=True, nullable=False)
    gender = Column(SQLEnum(Gender), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(Text, nullable=False)
    marital_status = Column(SQLEnum(MaritalStatus), nullable=False)
    occupation = Column(String(256), nullable=True)
    blood_type = Column(String(3), nullable=True)
    allergies = Column(String(256), nullable=True)
    medical_conditions = Column(Text, nullable=True)
    emergency_contact_name = Column(String(256), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Patient(id={self.id}, name='{self.name}', email='{self.email}')>"
    