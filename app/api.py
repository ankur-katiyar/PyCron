# api.py
import json
from fastapi import FastAPI, HTTPException, Request, Depends, Form, status, Body
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta

import logging
from threading import Thread
import os

from scheduler import job_scheduler
from models import Job, SessionLocal, User, create_user, get_user
from passlib.context import CryptContext

# Configure FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow React app
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Add session middleware with environment variable
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("SECRET_KEY", "default-secret-key"))

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

class StatusUpdate(BaseModel):
    status: str

# Pydantic model for job creation
class JobModel(BaseModel):
    name: str
    schedule: str  # JSON string for cron parameters, e.g., '{"minute": "*/5"}'
    command: str
    dependencies: list[int] = []  # List of job IDs

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

def require_authentication(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

# Health Check Endpoint
@app.get("/health")
def health_check():
    return {"status": "success"}

# Route: Login Page
@app.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Route: Handle Login
@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    session = SessionLocal()
    user = session.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        session.close()
        logger.warning(f"Failed login attempt for username '{username}'.")
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials."})
    request.session["user"] = user.username
    logger.info(f"User '{username}' logged in successfully.")
    session.close()
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

# Route: Logout
@app.get("/logout")
def logout(request: Request):
    request.session.pop("user", None)
    logger.info("User logged out.")
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

# Route: Dashboard
@app.get("/dashboard")
def dashboard(request: Request, user: User = Depends(require_authentication)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

# Route: Create Job
@app.post("/jobs")
def create_job(job: JobModel, user: str = Depends(require_authentication)):
    session = SessionLocal()
    existing_job = session.query(Job).filter(Job.name == job.name).first()
    if existing_job:
        session.close()
        raise HTTPException(status_code=400, detail="Job name already exists.")
    
    new_job = Job(
        name=job.name,
        schedule=job.schedule,
        command=job.command,
        dependencies=json.dumps(job.dependencies),
        status="scheduled"
    )
    session.add(new_job)
    session.commit()
    session.refresh(new_job)
    session.close()
    
    # Schedule the job
    job_scheduler.schedule_job(new_job)
    
    logger.info(f"Job '{new_job.name}' created with ID {new_job.id}.")
    return {"message": f"Job '{new_job.name}' created successfully.", "job_id": new_job.id}

# Route: Get All Jobs
@app.get("/jobs")
def get_jobs(user: str = Depends(require_authentication)):
    session = SessionLocal()
    jobs = session.query(Job).all()
    job_list = []
    for job in jobs:
        try:
            logs = json.loads(job.logs) if job.logs else []
        except json.JSONDecodeError:
            logs = []
            logger.error(f"Invalid JSON in logs for job {job.id}")

        job_data = {
            "id": job.id,
            "name": job.name,
            "schedule": json.loads(job.schedule),
            "command": job.command,
            "dependencies": json.loads(job.dependencies),
            "status": job.status,
            "last_run": job.last_run.isoformat() if job.last_run else None,
            "logs": logs,
            "run_count": len(logs),
        }

        # Calculate average execution time
        execution_times = [log.get('execution_time') for log in logs 
                          if isinstance(log.get('execution_time'), (int, float))]
        job_data["average_execution_time"] = (
            sum(execution_times) / len(execution_times) if execution_times else 0
        )

        # Get next run time from scheduler
        next_run = job_scheduler.get_next_run_time(job.id)
        job_data["next_run"] = next_run

        job_list.append(job_data)
    
    session.close()
    return job_list

# Route: Delete Job
@app.delete("/jobs/{job_id}")
def delete_job(job_id: int, user: User = Depends(require_authentication)):
    session = SessionLocal()
    job = session.query(Job).filter(Job.id == job_id).first()
    if not job:
        session.close()
        raise HTTPException(status_code=404, detail="Job not found.")
    
    session.delete(job)
    session.commit()
    session.close()
    
    # Remove the job from scheduler
    job_scheduler.delete_job(job_id)
    
    logger.info(f"Job '{job.name}' (ID: {job.id}) deleted.")
    return {"message": f"Job '{job.name}' deleted successfully."}

# Route: Run Job Ad-Hoc
@app.post("/jobs/{job_id}/run")
def run_job_adhoc(job_id: int, user: str = Depends(require_authentication)):
    session = SessionLocal()
    job = session.query(Job).filter(Job.id == job_id).first()
    if not job:
        session.close()
        raise HTTPException(status_code=404, detail="Job not found.")
    
    try:
        # Trigger the job execution
        rc,message = job_scheduler.run_job(job.id)
        if rc != 0:
            return {"message": f"Job ID {job_id} execution failed: {message}."}
        #session.close()
        logger.info(f"Job '{job.name}' (ID: {job.id}) executed ad-hoc.")
        return {"message": f"Job '{job.name}' executed successfully."}
    except Exception as e:
        session.close()
        logger.error(f"Error running job ad-hoc: {e}")
        raise HTTPException(status_code=500, detail="Failed to run job.")
    finally:
        session.close()

# Route: Update Job Status
@app.put("/jobs/{job_id}/status")
def update_job_status(job_id: int, status_update: StatusUpdate, user: User = Depends(require_authentication)):
    allowed_statuses = {"scheduled", "complete", "inactive"}
    if status_update.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of {allowed_statuses}.")
    
    allowed_statuses = {"scheduled", "complete", "inactive"}
    if status_update.status not in allowed_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Status must be one of {allowed_statuses}."
        )
        
    session = SessionLocal()
    job = session.query(Job).filter(Job.id == job_id).first()
    if not job:
        session.close()
        raise HTTPException(status_code=404, detail="Job not found.")
    
    job.status = status_update.status
    session.commit()
    
    if status_update.status == "scheduled":
        # Reschedule the job
        job_scheduler.schedule_job(job)
    # If status is "complete", no action needed for scheduler
    
    session.close()
    logger.info(f"Job ID {job_id} status updated to '{status_update.status}'.")
    return {"message": f"Job ID {job_id} status updated to '{status_update.status}'."}

# Route: Delete Log Entry
@app.delete("/jobs/{job_id}/logs/{log_index}")
def delete_log_entry(job_id: int, log_index: int, user: User = Depends(require_authentication)):
    session = SessionLocal()
    job = session.query(Job).filter(Job.id == job_id).first()
    if not job:
        session.close()
        raise HTTPException(status_code=404, detail="Job not found.")
    
    logs = json.loads(job.logs) if job.logs else []
    if log_index < 0 or log_index >= len(logs):
        session.close()
        raise HTTPException(status_code=400, detail="Invalid log index.")
    
    deleted_log = logs.pop(log_index)
    job.logs = json.dumps(logs)
    session.commit()
    session.close()
    
    logger.info(f"Deleted log entry {log_index + 1} for job '{job.name}' (ID: {job.id}).")
    return {"message": f"Log entry {log_index + 1} for job '{job.name}' deleted successfully."}

# Route: Purge Logs (Keep only the last 10 entries)
@app.post("/jobs/{job_id}/purge_logs")
def purge_logs(job_id: int, user: User = Depends(require_authentication)):
    session = SessionLocal()
    job = session.query(Job).filter(Job.id == job_id).first()
    if not job:
        session.close()
        raise HTTPException(status_code=404, detail="Job not found.")
    
    logs = json.loads(job.logs) if job.logs else []
    if len(logs) <= 10:
        session.close()
        return {"message": "No logs to purge."}
    
    # Keep only the last 10 entries
    purged_logs = logs[-10:]
    job.logs = json.dumps(purged_logs)
    session.commit()
    #session.close()
    
    logger.info(f"Purged logs for job '{job.name}' (ID: {job.id}), keeping last 10 entries.")
    return {"message": f"Logs purged for job '{job.name}'. Kept the last 10 entries."}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Utility function to verify passwords
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Event handler to start the scheduler when the app starts
@app.on_event("startup")
def startup_event():
    logger.info("Starting the Job Scheduler...")
    job_scheduler.start()

# Event handler to shut down the scheduler when the app shuts down
@app.on_event("shutdown")
def shutdown_event():
    logger.info("Shutting down the Job Scheduler...")
    job_scheduler.stop()

@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    session = SessionLocal()
    try:
        job = session.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Convert dependencies from JSON string to list
        dependencies = json.loads(job.dependencies) if job.dependencies else []
        
        return {
            "id": job.id,
            "name": job.name,
            "schedule": job.schedule,
            "command": job.command,
            "dependencies": dependencies,
            "status": job.status,
            "last_run": job.last_run.isoformat() if job.last_run else None,
            "logs": json.loads(job.logs) if job.logs else [],
        }
    except Exception as e:
        logger.error(f"Error fetching job details for ID {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        session.close()

# Define a Pydantic model for the job update payload
class JobUpdateModel(BaseModel):
    name: str
    schedule: str  # Expecting a JSON string
    command: str
    dependencies: list[int]  # List of job IDs

# Route: Update Job
@app.put("/jobs/{job_id}")
def update_job(job_id: int, job: JobModel, user: str = Depends(require_authentication)):
    session = SessionLocal()
    existing_job = session.query(Job).filter(Job.id == job_id).first()
    if not existing_job:
        session.close()
        raise HTTPException(status_code=404, detail="Job not found.")
    
    existing_job.name = job.name
    existing_job.schedule = job.schedule
    existing_job.command = job.command
    existing_job.dependencies = json.dumps(job.dependencies)
    
    session.commit()
    session.refresh(existing_job)
    session.close()
    
    # Update the job in the scheduler
    job_scheduler.schedule_job(existing_job)
    
    logger.info(f"Job '{existing_job.name}' (ID: {existing_job.id}) updated.")
    return {"message": f"Job '{existing_job.name}' updated successfully."}

# Mock user database
fake_users_db = {
    "admin": {
        "username": "admin",
        "password": "password",  # In a real app, use hashed passwords
    }
}

# Secret key for JWT
SECRET_KEY = "your-secret-key"  # Replace with a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str

# New endpoint for React login
@app.post("/api/login", response_model=Token)
async def react_login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Create a JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {
            "sub": user["username"],
            "exp": datetime.utcnow() + access_token_expires,
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return {"access_token": access_token, "token_type": "bearer"}

@app.delete("/jobs/{job_id}/logs")
def purge_job_logs(job_id: int, user: str = Depends(require_authentication)):
    session = SessionLocal()
    job = session.query(Job).filter(Job.id == job_id).first()
    if not job:
        session.close()
        raise HTTPException(status_code=404, detail="Job not found.")
    
    job.logs = "[]"  # Clear the logs
    session.commit()
    session.close()
    
    logger.info(f"Logs for job '{job.name}' (ID: {job.id}) purged.")
    return {"message": f"Logs for job '{job.name}' purged successfully."}