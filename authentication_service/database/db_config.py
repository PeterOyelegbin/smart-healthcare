from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# create database engine
engine = create_engine('sqlite:///./SMC.db', future=True)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)

# create function to get session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
