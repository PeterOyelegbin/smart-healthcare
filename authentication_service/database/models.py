from .db_config import Base
from sqlalchemy import Column, UUID, String, Boolean
from uuid import uuid4

# create database model
class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    business_name = Column(String(256), nullable=False)
    registration_number = Column(String, nullable=False)
    email = Column(String(256), unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_consent = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
