# main.py
import uvicorn
from app import app  # use the shared app instance
from models import SessionLocal, User, Base
from passlib.context import CryptContext

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
    #Base.metadata.create_all(bind=engine)
    
    # Create the default admin user
    create_default_admin_user()
    
    # Start the application
    #uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
