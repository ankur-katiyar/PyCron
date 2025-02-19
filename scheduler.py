# scheduler.py
import datetime
import json
import subprocess
from threading import Thread
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from models import Job, SessionLocal

logger = logging.getLogger(__name__)

class JobScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
    
    def start(self):
        self.scheduler.start()
        self.load_jobs()

    def load_jobs(self):
        # Load jobs from the database and schedule them
        session = SessionLocal()
        jobs = session.query(Job).all()
        for job in jobs:
            self.schedule_job(job)
        session.close()
    
    def schedule_job(self, job: Job):
        try:
            # Parse the schedule JSON string
            cron_params = json.loads(job.schedule)
            trigger = CronTrigger(**cron_params)
        except Exception as e:
            logger.error(f"Error parsing schedule for job '{job.name}': {e}")
            return

        try:
            # Add the job to APScheduler
            self.scheduler.add_job(
                func=self.run_job,
                trigger=trigger,
                args=[job.id],
                id=str(job.id),
                name=job.name,
                replace_existing=True
            )
        except Exception as e:
            logger.error(f"Error scheduling job '{job.name}': {e}")
    
    def run_job(self, job_id: int):
        session = SessionLocal()
        job = session.query(Job).filter(Job.id == job_id).first()
        if not job:
            session.close()
            return
        
        # Check dependencies: if any dependency is not 'completed', skip execution.
        deps = json.loads(job.dependencies)
        for dep_id in deps:
            dep_job = session.query(Job).filter(Job.id == dep_id).first()
            if dep_job and dep_job.status != "completed":
                print(f"Job '{job.name}' waiting for dependency job '{dep_job.name}' to complete.")
                session.close()
                return

        # Update job status to running
        job.status = "running"
        session.commit()
        try:
            # Execute the command.
            result = subprocess.run(job.command, shell=True, capture_output=True, text=True)
            log_entry = f"\n{datetime.datetime.now()}: STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            job.logs += log_entry
            job.status = "completed" if result.returncode == 0 else "failed"
        except Exception as e:
            job.logs += f"\n{datetime.datetime.now()}: Exception: {str(e)}"
            job.status = "failed"
        job.last_run = datetime.datetime.now()
        session.commit()
        session.close()
        
    def add_job(self, job_data: dict) -> Job:
        session = SessionLocal()
        job = Job(**job_data)
        print(job)
        session.add(job)
        session.commit()
        session.refresh(job)
        self.schedule_job(job)
        session.close()
        return job

    def run_job_adhoc(self, job_id: int) -> dict:
        # Trigger the job immediately on a separate thread
        thread = Thread(target=self.run_job, args=(job_id,))
        thread.start()
        return {"message": f"Job {job_id} triggered ad-hoc."}

    def remove_job(self, job_id: int):
        try:
            self.scheduler.remove_job(str(job_id))
        except Exception as e:
            print(f"Error removing job '{job_id}': {e}")

# Create a singleton scheduler instance for the API to use.
job_scheduler = JobScheduler()
