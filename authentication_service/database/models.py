from .db_config import Base
from sqlalchemy import Column, UUID, String, Boolean
from uuid import uuid4

# create database model
class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organisation = Column(String(256))
    # cac_document = Column(File)
    email = Column(String(256), unique=True)
    password = Column(String(20))
    is_active = Column(Boolean, default=True)
    verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
