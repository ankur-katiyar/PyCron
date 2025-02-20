# models.py
import datetime
import json
import os
from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

#DATABASE_URL = "sqlite:///./scheduler.db"
DATABASE_URL = os.environ.get("DATABASE_URL","sqlite:///./scheduler.db")

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    schedule = Column(Text, nullable=False)  # JSON string for cron parameters
    command = Column(Text, nullable=False)
    dependencies = Column(Text, default='[]')  # JSON list of job IDs
    status = Column(String, default="scheduled")  # "scheduled", "running", "complete", "failed", "inactive"
    last_run = Column(DateTime, nullable=True)
    logs = Column(Text, default='[]')  # JSON list of logs

    def __repr__(self):
        return f"Job(id={self.id}, name={self.name}, schedule={self.schedule}, command={self.command}, dependencies={self.dependencies}, status={self.status}, last_run={self.last_run}, logs={self.logs})"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    def __repr__(self):
        return f"User(id={self.id}, username={self.username})"

def create_user(username: str, password: str):
    session = SessionLocal()
    hashed_password = pwd_context.hash(password)
    user = User(username=username, hashed_password=hashed_password)
    session.add(user)
    session.commit()
    session.close()
    return user

def get_user(username: str):
    session = SessionLocal()
    user = session.query(User).filter(User.username == username).first()
    session.close()
    return user

# Create all tables
Base.metadata.create_all(bind=engine)
