# api.py
import json
from fastapi import FastAPI, HTTPException, Request, Depends, Form, status
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates

import logging
from threading import Thread
import os

from scheduler import job_scheduler
from models import Job, SessionLocal, User, create_user, get_user
from passlib.context import CryptContext

# Configure FastAPI app
app = FastAPI()

# Add session middleware with environment variable
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("SECRET_KEY", "default-secret-key"))

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

# Pydantic model for job creation
class JobModel(BaseModel):
    name: str
    schedule: str  # JSON string for cron parameters, e.g., '{"minute": "*/5"}'
    command: str
    dependencies: list[int] = []  # List of job IDs

# Dependency for authentication
def require_authentication(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

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
def create_job(job: JobModel, user: User = Depends(require_authentication)):
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
def get_jobs(user: User = Depends(require_authentication)):
    session = SessionLocal()
    jobs = session.query(Job).all()
    job_list = []
    for job in jobs:
        job_data = {
            "id": job.id,
            "name": job.name,
            "schedule": json.loads(job.schedule),
            "command": job.command,
            "dependencies": json.loads(job.dependencies),
            "status": job.status,
            "last_run": job.last_run.isoformat() if job.last_run else None,
            "logs": json.loads(job.logs) if job.logs else []
        }
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
def run_job_adhoc(job_id: int, user: User = Depends(require_authentication)):
    session = SessionLocal()
    job = session.query(Job).filter(Job.id == job_id).first()
    if not job:
        session.close()
        raise HTTPException(status_code=404, detail="Job not found.")
    
    # Check dependencies
    dependencies = json.loads(job.dependencies) if job.dependencies else []
    if dependencies:
        parent_jobs = session.query(Job).filter(Job.id.in_(dependencies)).all()
        incomplete_deps = [parent.name for parent in parent_jobs if parent.status != "complete"]
        if incomplete_deps:
            session.close()
            raise HTTPException(status_code=400, detail=f"Dependencies not complete: {', '.join(incomplete_deps)}.")
    
    # Run the job in a separate thread to avoid blocking
    thread = Thread(target=job_scheduler.run_job, args=(job_id,))
    thread.start()
    session.close()
    logger.info(f"Job '{job.name}' (ID: {job.id}) triggered ad-hoc.")
    return {"message": f"Job '{job.name}' triggered successfully."}

# Route: Update Job Status
@app.put("/jobs/{job_id}/status")
def update_job_status(job_id: int, status: str, user: User = Depends(require_authentication)):
    allowed_statuses = {"scheduled", "complete", "inactive"}
    if status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of {allowed_statuses}.")
    
    session = SessionLocal()
    job = session.query(Job).filter(Job.id == job_id).first()
    if not job:
        session.close()
        raise HTTPException(status_code=404, detail="Job not found.")
    
    job.status = status
    session.commit()
    
    if status == "inactive":
        # Remove job from scheduler
        job_scheduler.delete_job(job_id)
    elif status == "scheduled":
        # Reschedule the job
        job_scheduler.schedule_job(job)
    # If status is "complete", no action needed for scheduler
    
    session.close()
    logger.info(f"Job ID {job_id} status updated to '{status}'.")
    return {"message": f"Job ID {job_id} status updated to '{status}'."}

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