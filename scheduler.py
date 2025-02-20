# scheduler.py
import datetime
import json
import subprocess
from threading import Thread
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.base import JobLookupError
from apscheduler.job import Job as APSJob

from models import Job, SessionLocal

# Configure logger
logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

class JobScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
    
    def start(self):
        try:
            self.scheduler.start()
            self.load_jobs()
            logger.info("Scheduler started.")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
    
    def load_jobs(self):
        # Load jobs from the database and schedule them
        try:
            session = SessionLocal()
            jobs = session.query(Job).filter(Job.status != "inactive").all()
            logger.info(f"Loaded {len(jobs)} jobs from the database.")
            for job in jobs:
                self.schedule_job(job)
            session.close()
        except Exception as e:
            logger.error(f"Error loading jobs: {e}")
    
    def schedule_job(self, job: Job):
        # Parse the schedule JSON
        try:
            schedule_params = json.loads(job.schedule)
            trigger = CronTrigger(**schedule_params)
        except json.JSONDecodeError:
            logger.error(f"Invalid schedule format for job '{job.name}'. Skipping scheduling.")
            return
        except TypeError as e:
            logger.error(f"Error parsing schedule for job '{job.name}': {e}")
            return
        
        # Add the job to APScheduler
        try:
            self.scheduler.add_job(
                func=self.run_job,
                trigger=trigger,
                args=[job.id],
                id=str(job.id),
                replace_existing=True,
                name=job.name
            )
            logger.info(f"Scheduled job '{job.name}' with ID {job.id}.")
        except Exception as e:
            logger.error(f"Failed to schedule job '{job.name}' (ID: {job.id}): {e}")
    
    def run_job(self, job_id: int):
        session = SessionLocal()
        try:
            job = session.query(Job).filter(Job.id == job_id).first()
            if not job:
                logger.error(f"Job with ID {job_id} not found.")
                return
            
            # Check if job is inactive
            if job.status == "inactive":
                logger.info(f"Job '{job.name}' is inactive. Skipping execution.")
                return
            
            # Check dependencies
            dependencies = json.loads(job.dependencies) if job.dependencies else []
            if dependencies:
                parent_jobs = session.query(Job).filter(Job.id.in_(dependencies)).all()
                incomplete_deps = [parent.name for parent in parent_jobs if parent.status != "complete"]
                if incomplete_deps:
                    logger.info(f"Job '{job.name}' is waiting for dependencies to complete: {', '.join(incomplete_deps)}.")
                    return
            
            # Execute the command
            start_time = datetime.datetime.utcnow()
            logger.info(f"Executing job '{job.name}' (ID: {job.id})...")
            result = subprocess.run(job.command, shell=True, capture_output=True, text=True)
            end_time = datetime.datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            # Update job logs
            log_entry = {
                "timestamp": end_time.isoformat(),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": execution_time
            }
            if isinstance(execution_time, (int, float)):
                logs = json.loads(job.logs) if job.logs else []
                logs.append(log_entry)
                job.logs = json.dumps(logs)
            else:
                logger.error(f"Invalid execution_time for job '{job.name}' (ID: {job.id}): {execution_time}")
            
            # Update job status based on execution result
            if result.returncode == 0:
                job.status = "complete"
                logger.info(f"Job '{job.name}' completed successfully.")
            else:
                job.status = "failed"
                logger.error(f"Job '{job.name}' failed with return code {result.returncode}.")
            
            job.last_run = end_time
            session.commit()
            logger.info(f"Job '{job.name}' (ID: {job.id}) status updated to '{job.status}'.")
        except Exception as e:
            logger.error(f"Error executing job '{job.name}': {e}")
            if job:
                job.status = "failed"
                session.commit()
        finally:
            session.close()
    
    def get_next_run_time(self, job_id: int):
        try:
            aps_job = self.scheduler.get_job(str(job_id))
            if aps_job:
                next_run_time = getattr(aps_job, 'next_run_time', None)
                logger.debug(f"APS Job: {aps_job.name}, next_run_time: {next_run_time}")
                session = SessionLocal()
                db_job = session.query(Job).filter(Job.id == job_id).first()
                if db_job and db_job.status == "inactive":
                    session.close()
                    return None
                session.close()
                return next_run_time.isoformat() if next_run_time else None
            else:
                logger.debug(f"No APS job found for job_id: {job_id}")
                return None
        except JobLookupError:
            logger.error(f"Job ID {job_id} not found in scheduler.")
            return None
    
    def stop(self):
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped.")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def delete_job(self, job_id: int):
        try:
            self.scheduler.remove_job(str(job_id))
            logger.info(f"Removed job with ID {job_id} from scheduler.")
        except JobLookupError:
            logger.error(f"Job ID {job_id} not found in scheduler.")
        except Exception as e:
            logger.error(f"Error removing job ID {job_id}: {e}")
    
    def get_job_status(self, job_id: int):
        session = SessionLocal()
        try:
            job = session.query(Job).filter(Job.id == job_id).first()
            if job:
                return job.status
            return "unknown"
        finally:
            session.close()

# Create a singleton scheduler instance for the API to use.
job_scheduler = JobScheduler()
