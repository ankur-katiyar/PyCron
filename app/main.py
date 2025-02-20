# main.py
import uvicorn
import os
from app import app  # use the shared app instance
from models import SessionLocal, User, Base
from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Import routes to ensure they are registered.
import api
import ui

# Create a password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_default_admin_user():
    session = SessionLocal()
    # Check if the admin user already exists
    admin_user = session.query(User).filter(User.username == "admin").first()
    if not admin_user:
        # Create a new admin user
        hashed_password = pwd_context.hash("password")  # Hash the password
        new_user = User(username="admin", hashed_password=hashed_password)
        session.add(new_user)
        session.commit()
        print("Default admin user created.")
    else:
        print("Default admin user already exists.")
    session.close()

if __name__ == "__main__":
    # Create the database tables if they don't exist
    DATABASE_URL = os.environ.get("DATABASE_URL","sqlite:///./scheduler.db")

    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    # Create the default admin user
    create_default_admin_user()
    
    # Start the application
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
