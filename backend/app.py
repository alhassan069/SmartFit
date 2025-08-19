from fastapi import FastAPI
from db import engine, Base
from routes.user import router as user_router
from routes.workouts import router as workouts_router
from models import User, WorkoutPlans, Exercise, WorkoutPlanExercise, WorkoutProgress, NutritionalLogs



app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

app.include_router(user_router)
app.include_router(workouts_router)


def create_database():

    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")

@app.on_event("startup")
async def startup_event():
    create_database()