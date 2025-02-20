# models.py
import datetime
import json
from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

DATABASE_URL = "sqlite:///./scheduler.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)

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

def init_db():
    Base.metadata.create_all(bind=engine)
    # Create a default admin user if none exists
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    if not session.query(User).first():
        admin = User(username="admin")
        admin.set_password("password")  # Change this to a secure password
        session.add(admin)
        session.commit()
        print("Created default admin user with username 'admin' and password 'password'")
    session.close()

# Initialize the database at module load
init_db()

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
