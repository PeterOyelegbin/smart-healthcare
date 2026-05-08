from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from redis import Redis
from decouple import config

# create database engine
engine = create_engine(config('DATABASE_URL'))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# create redis client
redis_client = Redis(host=config('REDIS_HOST'), port=config('REDIS_PORT'), password=config('REDIS_PASSWORD'), db=0, decode_responses=True)

Base = declarative_base()

# create function to get session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
