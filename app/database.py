from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv() #reads .env and loads the variables into the environment

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL) #creates connection to PostgreSQL database using the URL from .env
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #a factory that creates new Session objects when called, configured to not autocommit and not autoflush, and bound to the engine

Base = declarative_base() #all models inherit from this. SQLAlchemy uses this to create tables and map classes to database tables

# Dependency that can be used in FastAPI routes to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()