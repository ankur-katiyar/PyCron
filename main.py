# main.py
import uvicorn
from app import app  # use the shared app instance

# Import routes to ensure they are registered.
import api
import ui

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
