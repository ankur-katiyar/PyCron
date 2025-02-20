# Job Scheduler

## Overview

**Job Scheduler** is a robust web-based application developed using FastAPI and APScheduler. It allows users to create, manage, and execute scheduled jobs with dependencies. The application features a polished dashboard interface, user authentication, and comprehensive logging mechanisms.

## Features

- **Create Jobs:** Define jobs with unique names, schedules (using cron syntax), commands, and dependencies on other jobs.
- **Manage Dependencies:** Ensure that dependent jobs only run when their parent jobs have successfully completed.
- **Ad-Hoc Execution:** Manually trigger jobs outside of their scheduled time.
- **User Authentication:** Secure access with username and password login, along with a logoff option.
- **Comprehensive Logging:** View detailed logs for each job execution, including stdout, stderr, and execution time.
- **Reset Functionality:** Reset job statuses back to "scheduled" to rerun jobs as needed.
- **Responsive Dashboard:** Intuitive and responsive user interface for managing and monitoring jobs.
- **Refresh Functionality:** Easily refresh the job list to view the latest updates.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage](#usage)
  - [Logging In](#logging-in)
  - [Adding a New Job](#adding-a-new-job)
  - [Managing Jobs](#managing-jobs)
  - [Viewing Logs](#viewing-logs)
  - [Running Jobs Ad-Hoc](#running-jobs-adhoc)
  - [Resetting Job Status](#resetting-job-status)
  - [Refreshing Dashboard](#refreshing-dashboard)
  - [Logging Out](#logging-out)
- [Security](#security)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Kubernetes Deployment](#kubernetes-deployment)

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Python 3.7+**: Ensure Python is installed on your machine. You can download it from [here](https://www.python.org/downloads/).
- **Virtual Environment (Recommended)**: It is advisable to use a virtual environment to manage dependencies.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/job-scheduler.git
   cd job-scheduler
   ```

2. **Create and Activate a Virtual Environment**

   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Unix or MacOS
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

   *If a `requirements.txt` file does not exist, manually install the necessary packages:*

   ```bash
   pip install fastapi uvicorn sqlalchemy passlib[bcrypt] jinja2 apscheduler
   ```

## Configuration

1. **Secret Key**

   Replace the placeholder secret key in `api.py` with a strong, randomly generated secret key to secure session data.

   ```python
   app.add_middleware(SessionMiddleware, secret_key="your-strong-secret-key")  # Replace with a secure secret
   ```

   *You can generate a secret key using Python:*

   ```python
   import secrets
   secrets.token_hex(16)
   ```

2. **Database URL**

   The application uses SQLite by default. If you wish to use another database (e.g., PostgreSQL, MySQL), update the `DATABASE_URL` in `models.py`.

   ```python
   DATABASE_URL = "sqlite:///./scheduler.db"
   ```

   For example, for PostgreSQL:

   ```python
   DATABASE_URL = "postgresql://user:password@localhost:5432/job_scheduler_db"
   ```

## Running the Application

Start the FastAPI server using Uvicorn:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

This will start the server on `http://0.0.0.0:8000`.

- **Host:** `0.0.0.0` makes the server accessible externally.
- **Port:** `8000` is the default port; you can change it as needed.
- **Reload:** Enables auto-reloading on code changes (useful during development).

Access the application by navigating to `http://localhost:8000` in your web browser.

## Usage

### Logging In

1. **Access the Login Page**

   Navigate to `http://localhost:8000/login`.

2. **Default Admin Credentials**

   On the first run, a default admin user is created:

   - **Username:** `admin`
   - **Password:** `password`

   **Security Note:**  
   Immediately change the default password after first login to secure your application.

### Adding a New Job

1. **Navigate to the Dashboard**

   After logging in, you'll be redirected to the dashboard.

2. **Fill Out the "Add New Job" Form**

   - **Job Name:** Enter a unique name for the job.
   - **Schedule:** Provide cron-formatted JSON for scheduling (e.g., `{"minute": "*/5"}` for every 5 minutes).
   - **Command:** Specify the command to execute (e.g., `echo "Hello World"`).
   - **Dependencies:** (Optional) Enter comma-separated Job IDs that this job depends on.

3. **Submit the Form**

   Click the "Add Job" button. If successful, a toast notification will confirm the creation, and the job list will refresh automatically.

### Managing Jobs

- **Run Now:**  
  Click the "Run Now" button next to a job to execute it immediately.

- **Toggle Logs:**  
  Click the "Toggle Logs" button to view or hide the execution logs for a job.

- **Reset Job Status:**  
  Click the "Reset" button to set the job's status back to "scheduled," allowing it to be rerun.

- **Delete Job:**  
  Click the "Delete" button to remove a job. Confirm the action when prompted.

- **Edit Job:**  
  Click the "Edit" button to modify job details. *(Note: Edit functionality is a placeholder and needs implementation.)*

### Viewing Logs

1. **Toggle Logs**

   Click the "Toggle Logs" button next to a job to view its execution logs.

2. **Log Details**

   Logs include:

   - **Timestamp**
   - **STDOUT:** Standard output from the command.
   - **STDERR:** Standard error from the command.
   - **Execution Time:** Duration of the job execution in seconds.

3. **Delete Log Entry**

   Click the "Delete Log" button within a log entry to remove it.

4. **Purge Logs**

   Click the "Purge Logs" button to retain only the last 10 log entries for a job.

### Running Jobs Ad-Hoc

- **Run Now Button:**  
  Click the "Run Now" button next to a job to execute it immediately. This is useful for testing or manual triggering of jobs.

### Resetting Job Status

- **Reset Button:**  
  Click the "Reset" button next to a job to set its status back to "scheduled." This allows the job to be rerun as per its schedule or manually triggered.

### Refreshing Dashboard

- **Refresh Button:**  
  Click the "Refresh" button in the header to manually update the job list and ensure you're viewing the latest data.

### Logging Out

- **Logoff Button:**  
  Click the "Logoff" button in the header to end your session and return to the login page.

## Security

- **Password Management:**  
  The application uses hashed passwords stored securely in the database using `passlib`.

- **Session Management:**  
  User sessions are managed via secure cookies. Ensure that `secret_key` is strong and kept confidential.

- **Secure Deployment:**  
  - Consider using HTTPS to encrypt data in transit.
  - Regularly update dependencies to patch potential vulnerabilities.
  - Implement additional security measures as needed (e.g., rate limiting, user roles).

## Project Structure

```
job-scheduler/
├── api.py
├── models.py
├── scheduler.py
├── __init__.py
├── README.md
├── requirements.txt
├── templates/
│   ├── login.html
│   └── dashboard.html
└── static/
    └── (optional static files like CSS, JS)
```

- **api.py:**  
  Main FastAPI application handling routes, authentication, and integration with the scheduler.

- **models.py:**  
  Database models using SQLAlchemy, including the `Job` and `User` models.

- **scheduler.py:**  
  Scheduler management using APScheduler, handling job execution, dependencies, and logging.

- **templates/:**  
  HTML templates rendered using Jinja2 for the login page and dashboard.

- **static/:**  
  Directory for static files like CSS and JavaScript, if needed.

## Troubleshooting

- **AttributeError: `'apscheduler.job.Job' object has no attribute 'next_run_time'`**  
  - **Cause:** This error typically occurs due to conflicts between APScheduler's `Job` class and your application's `Job` model.
  - **Solution:**  
    - Ensure that APScheduler is correctly imported and that there are no naming conflicts.
    - Verify that the scheduler is started on application startup.
    - Check APScheduler's version compatibility with your code.
    - Utilize `getattr` to safely access attributes.

- **Database Errors (e.g., UNIQUE Constraint Failed)**  
  - **Cause:** Attempting to create a job with a name that already exists.
  - **Solution:** Ensure that all job names are unique. The application now checks for duplicate names and provides appropriate error messages.

- **Authentication Issues**  
  - **Cause:** Problems logging in or sessions not persisting.
  - **Solution:**  
    - Verify that `SessionMiddleware` is correctly configured with a strong secret key.
    - Ensure that cookies are enabled in your browser.
    - Check server logs for any authentication-related errors.

- **Dependency Handling Issues**  
  - **Cause:** Child jobs not triggering due to unmet dependencies.
  - **Solution:**  
    - Ensure that parent jobs complete successfully and update their statuses to "complete."
    - Verify that child jobs have their dependencies correctly set.
    - Check logs for any errors related to job execution or dependency management.

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**

2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "Add Your Feature"
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeatureName
   ```

5. **Open a Pull Request**

## License

This project is licensed under the [MIT License](LICENSE).

## Kubernetes Deployment

### Prerequisites for Kubernetes Deployment

- Kubernetes cluster (local or cloud-based)
- kubectl CLI tool installed and configured
- Docker installed (for building the container image)
- Access to a container registry (e.g., Docker Hub, Google Container Registry)

### Deployment Steps

1. **Build and Push the Docker Image**

   ```bash
   # Build the Docker image
   docker build -t job-scheduler:latest .

   # Tag the image for your registry
   docker tag job-scheduler:latest your-registry/job-scheduler:latest

   # Push to your registry
   docker push your-registry/job-scheduler:latest
   ```

2. **Deploy to Kubernetes**

   The application includes Kubernetes manifests in the `k8s/` directory:

   ```bash
   # Create namespace (optional)
   kubectl create namespace job-scheduler

   # Apply the deployment
   kubectl apply -f k8s/deployment.yaml
   ```

3. **Verify the Deployment**

   ```bash
   # Check if pods are running
   kubectl get pods -n job-scheduler

   # Check the service
   kubectl get svc job-scheduler-service -n job-scheduler

   # View logs
   kubectl logs -f deployment/job-scheduler -n job-scheduler
   ```

### Kubernetes Configuration Files

The deployment uses the following Kubernetes resources:

- **PersistentVolumeClaim:** For storing the SQLite database
- **Deployment:** Main application deployment
- **Service:** Exposes the application

Key features of the deployment:

- Single replica deployment (to prevent scheduling conflicts)
- Persistent storage for the SQLite database
- Resource limits and requests
- Health checks via liveness and readiness probes
- LoadBalancer service type (configurable)

### Monitoring and Maintenance

1. **Health Checks**

   The application exposes a `/health` endpoint that Kubernetes uses to monitor the pod's health:
   ```bash
   # Check the pod's health status
   kubectl describe pod -l app=job-scheduler -n job-scheduler
   ```

2. **Scaling Considerations**

   The application is designed to run as a single instance. Horizontal scaling is not recommended due to:
   - SQLite database limitations
   - Potential scheduling conflicts
   - Job execution coordination requirements

3. **Database Backups**

   To backup the SQLite database:
   ```bash
   # Copy the database file from the pod
   kubectl cp job-scheduler-pod:/app/data/scheduler.db backup.db
   ```

### Troubleshooting Kubernetes Deployment

1. **Pod Won't Start**
   - Check pod events:
     ```bash
     kubectl describe pod -l app=job-scheduler -n job-scheduler
     ```
   - View pod logs:
     ```bash
     kubectl logs -f deployment/job-scheduler -n job-scheduler
     ```

2. **Service Not Accessible**
   - Verify service configuration:
     ```bash
     kubectl describe service job-scheduler-service -n job-scheduler
     ```
   - Check endpoints:
     ```bash
     kubectl get endpoints job-scheduler-service -n job-scheduler
     ```

3. **Database Issues**
   - Check persistent volume:
     ```bash
     kubectl describe pvc scheduler-db-pvc -n job-scheduler
     ```
   - Verify volume mounts:
     ```bash
     kubectl describe pod -l app=job-scheduler -n job-scheduler
     ```

### Production Considerations

1. **Security**
   - Use Kubernetes Secrets for sensitive data
   - Implement network policies
   - Configure proper RBAC
   - Consider using a ServiceAccount

2. **High Availability**
   - Consider using a more robust database (e.g., PostgreSQL)
   - Implement proper backup strategies
   - Use node affinity rules for better placement

3. **Monitoring**
   - Set up Prometheus metrics
   - Configure proper logging
   - Implement alerting

4. **Updates and Rollbacks**
   ```bash
   # Rolling update
   kubectl set image deployment/job-scheduler job-scheduler=your-registry/job-scheduler:new-version

   # Rollback if needed
   kubectl rollout undo deployment/job-scheduler
   ```

### Environment Variables

The following environment variables can be configured in the deployment:

- `DATABASE_URL`: SQLite database location (default: `sqlite:///app/data/scheduler.db`)
- Add other environment variables as needed

Update these in the `deployment.yaml` file under the `env` section of the container spec.

---