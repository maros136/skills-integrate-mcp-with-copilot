"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from contextlib import asynccontextmanager
import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    db.seed_data()
    yield

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities",
              lifespan=lifespan)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return db.get_activities()


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    activity = db.get_activity(activity_name)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate capacity
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")

    # Add student (raises ValueError if already signed up)
    try:
        db.add_participant(activity_name, email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if db.get_activity(activity_name) is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Remove student
    removed = db.remove_participant(activity_name, email)
    if not removed:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

    return {"message": f"Unregistered {email} from {activity_name}"}
