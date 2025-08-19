from fastapi import FastAPI
from sqlalchemy.orm import declarative_base, Session
from db import SessionLocal, engine, Base

from models import User, WorkoutPlans, WorkoutPlanExercise, Exercise, WorkoutProgress, NutritionalLogs

Base.metadata.create_all(bind=engine)
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}