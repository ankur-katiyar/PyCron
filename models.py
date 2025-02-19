# models.py
import datetime
import json
from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./scheduler.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    schedule = Column(String, nullable=False)
    command = Column(Text, nullable=False)
    dependencies = Column(Text, default="[]")
    status = Column(String, default="scheduled")
    last_run = Column(DateTime, nullable=True)
    logs = Column(Text, default="")

def __repr__(self):
    print(f"Job(id={self.id}, name={self.name}, schedule={self.schedule}, command={self.command}, dependencies={self.dependencies}, status={self.status}, last_run={self.last_run}, logs={self.logs})")
    
def init_db():
    Base.metadata.create_all(bind=engine)

# Initialize the database at module load
init_db()
