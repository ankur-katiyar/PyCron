# ui.py
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app import app  # Shared FastAPI instance
from models import SessionLocal, Job

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    session = SessionLocal()
    jobs = session.query(Job).all()
    session.close()
    return templates.TemplateResponse("dashboard.html", {"request": request, "jobs": jobs})
