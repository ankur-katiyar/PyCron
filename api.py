# api.py
import json
from fastapi import HTTPException, Request
from pydantic import BaseModel
import logging

from app import app  # import the shared app instance
from scheduler import job_scheduler
from models import Job, SessionLocal

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

# Pydantic model for job creation
class JobModel(BaseModel):
    name: str
    schedule: str  # JSON string for cron parameters, e.g., '{"minute": "*/5"}'
    command: str
    dependencies: list[int] = []  # List of job IDs

@app.on_event("startup")
def startup_event():
    job_scheduler.start()

@app.post("/jobs")
def create_job(job: JobModel):
    logger.debug('Received job creation request')
    job_data = job.dict()
    
    # Log the incoming data
    logger.debug(f"Incoming job data: {job_data}")
    
    # Validate and parse the schedule JSON string
    try:
        schedule_data = json.loads(job_data['schedule'])
        logger.debug(f"Parsed schedule data: {schedule_data}")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid schedule format: {e}")
        raise HTTPException(status_code=422, detail="Invalid schedule format")
    
    # Store dependencies as a JSON string
    job_data["dependencies"] = json.dumps(job_data.get("dependencies", []))
    
    try:
        new_job = job_scheduler.add_job(job_data)
        return {"message": "Job created", "job_id": new_job.id}
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/jobs")
def get_jobs():
    session = SessionLocal()
    jobs = session.query(Job).all()
    result = []
    for job in jobs:
        result.append({
            "id": job.id,
            "name": job.name,
            "schedule": job.schedule,
            "command": job.command,
            "dependencies": json.loads(job.dependencies),
            "status": job.status,
            "last_run": job.last_run.isoformat() if job.last_run else None,
            "logs": job.logs,
        })
    session.close()
    return result

@app.post("/jobs/{job_id}/run")
def run_job_now(job_id: int):
    return job_scheduler.run_job_adhoc(job_id)

@app.delete("/jobs/{job_id}")
def delete_job(job_id: int):
    session = SessionLocal()
    job = session.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        session.close()
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Remove job from scheduler
    job_scheduler.remove_job(job_id)
    
    session.delete(job)
    session.commit()
    session.close()
    return {"message": f"Job {job_id} deleted successfully"}

from pydantic import BaseModel
from fastapi import HTTPException
from models import SessionLocal, Job

class JobUpdate(BaseModel):
    name: str
    schedule: str
    command: str
    dependencies: list[str] = []  # Convert to strings before sending

@app.put("/jobs/{job_id}")
def update_job(job_id: int, job_update: JobUpdate):
    session = SessionLocal()
    job = session.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        session.close()
        raise HTTPException(status_code=404, detail="Job not found")

    updated_dependencies = json.dumps(job_update.dependencies)
    
    job.name = job_update.name
    job.schedule = job_update.schedule
    job.command = job_update.command
    job.dependencies = updated_dependencies

    session.commit()
    session.close()
    return {"message": f"Job {job_id} updated successfully"}

@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    session = SessionLocal()
    job = session.query(Job).filter(Job.id == job_id).first()
    if not job:
        session.close()
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = {
        "id": job.id,
        "name": job.name,
        "schedule": job.schedule,
        "command": job.command,
        "dependencies": json.loads(job.dependencies),
        "status": job.status,
        "last_run": job.last_run.isoformat() if job.last_run else None,
        "logs": job.logs,
    }
    session.close()
    return job_data