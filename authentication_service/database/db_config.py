from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from redis import Redis
from decouple import config

# create database engine
engine = create_engine(config('DATABASE_URL'), connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# create redis client
redis_client = Redis(host=config('REDIS_HOST'), port=config('REDIS_PORT'), db=config('REDIS_DB'), decode_responses=True)

Base = declarative_base()

# create function to get session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
