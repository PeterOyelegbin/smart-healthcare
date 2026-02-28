from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

# create database engine
engine = create_engine(config('DATABASE_URL'), connect_args={"check_same_thread": False})
# engine = create_engine('sqlite:///./SMC.db', future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
# SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)

Base = declarative_base()

# create function to get session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
