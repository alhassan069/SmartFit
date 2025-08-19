from fastapi import FastAPI, Depends, HTTPException, Response, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import declarative_base, Session
from db import SessionLocal, engine, Base
import uuid
import time

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

session_cache = {}
SESSION_EXPIRY = 3600

def get_session_id():
    return str(uuid.uuid4())

def add_session_to_cache(session_id: str, user_id: int):
    session_cache[session_id] = {
        "user_id": user_id,
        "expires_at": time.time() + SESSION_EXPIRY
    }

def get_user_from_cache(session_id: str):
    if session_id in session_cache:
        if session_cache[session_id]["expires_at"] > time.time():
            return session_cache[session_id]["user_id"]
        else:
            del session_cache[session_id]
    return None

def get_current_user(request: Request, db: Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    user_id = get_user_from_cache(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return user

def remove_session_from_cache(session_id: str):
    if session_id in session_cache:
        del session_cache[session_id]


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}



class Register(BaseModel):
    name: str
    email: str
    password: str
    age: int | None = None
    weight: int | None = None
    height: int | None = None
    fitness_goals: str | None = None
    medical_conditions: str | None = None
    activity_level: str | None = None

@app.post("/auth/register")
def register(user: Register, db : Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status":200,"message":"User registered successfully"}


@app.get("/auth/user/{user_id}")
def get_user(user_id:int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return HTTPException(status_code=404, detail="User not found")
    return user


class Login(BaseModel):
    email: str
    password: EmailStr
@app.post("/auth/login")
def login(user: Login, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user is None:
        return HTTPException(status_code=404, detail="User not found")
    
    if db_user.password != user.password:
        return HTTPException(status_code=500, detail="Incorrect Password")
    
    session_id = get_session_id()
    add_session_to_cache(session_id, db_user.id)

    response.set_cookie(key="session_id", value=session_id, httponly=True, secure=True, max_age=SESSION_EXPIRY)
    return {"status":200,"message":"Login Successful"}


