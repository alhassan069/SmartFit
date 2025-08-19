from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import get_db
from models import WorkoutPlans, Exercise, WorkoutProgress, WorkoutPlanExercise, User
from typing import List, Optional
from datetime import date
from routes.user import get_current_user

router = APIRouter(prefix="/workouts")

# Pydantic models for request/response
class ExerciseBase(BaseModel):
    exercise_name: str
    category: Optional[str] = None
    equipment_needed: Optional[str] = None
    difficulty: Optional[str] = None
    instructions: Optional[str] = None
    target_muscle: Optional[str] = None

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseResponse(ExerciseBase):
    id: int
    
    class Config:
        from_attributes = True

class WorkoutPlanBase(BaseModel):
    plan_name: str
    difficulty_level: Optional[str] = None
    duration: Optional[str] = None

class WorkoutPlanCreate(WorkoutPlanBase):
    pass

class WorkoutPlanResponse(WorkoutPlanBase):
    id: int
    
    class Config:
        from_attributes = True

class WorkoutPlanExerciseBase(BaseModel):
    exercise_id: int
    sets: Optional[int] = None
    reps: Optional[int] = None
    duration: Optional[str] = None
    order: Optional[int] = None

class WorkoutPlanExerciseCreate(WorkoutPlanExerciseBase):
    pass

class WorkoutPlanExerciseResponse(WorkoutPlanExerciseBase):
    id: int
    workout_plan_id: int
    exercise: ExerciseResponse
    
    class Config:
        from_attributes = True

class WorkoutProgressBase(BaseModel):
    workout_id: int
    exercise_id: int
    date: date
    sets: Optional[int] = None
    reps: Optional[int] = None
    weights: Optional[int] = None
    duration: Optional[str] = None
    notes: Optional[str] = None

class WorkoutProgressCreate(WorkoutProgressBase):
    pass

class WorkoutProgressResponse(WorkoutProgressBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

# Exercise CRUD operations
@router.post("/exercises", response_model=ExerciseResponse)
def create_exercise(exercise: ExerciseCreate, db: Session = Depends(get_db)):
    db_exercise = Exercise(**exercise.model_dump())
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

@router.get("/exercises", response_model=List[ExerciseResponse])
def get_exercises(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    exercises = db.query(Exercise).offset(skip).limit(limit).all()
    return exercises

@router.get("/exercises/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise

@router.put("/exercises/{exercise_id}", response_model=ExerciseResponse)
def update_exercise(exercise_id: int, exercise: ExerciseCreate, db: Session = Depends(get_db)):
    db_exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    for key, value in exercise.model_dump().items():
        setattr(db_exercise, key, value)
    
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

@router.delete("/exercises/{exercise_id}")
def delete_exercise(exercise_id: int, db: Session = Depends(get_db)):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    db.delete(exercise)
    db.commit()
    return {"message": "Exercise deleted successfully"}

# Workout Plan CRUD operations
@router.post("/plans", response_model=WorkoutPlanResponse)
def create_workout_plan(plan: WorkoutPlanCreate, db: Session = Depends(get_db)):
    db_plan = WorkoutPlans(**plan.model_dump())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

@router.get("/plans", response_model=List[WorkoutPlanResponse])
def get_workout_plans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    plans = db.query(WorkoutPlans).offset(skip).limit(limit).all()
    return plans

@router.get("/plans/{plan_id}", response_model=WorkoutPlanResponse)
def get_workout_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(WorkoutPlans).filter(WorkoutPlans.id == plan_id).first()
    if plan is None:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    return plan

@router.put("/plans/{plan_id}", response_model=WorkoutPlanResponse)
def update_workout_plan(plan_id: int, plan: WorkoutPlanCreate, db: Session = Depends(get_db)):
    db_plan = db.query(WorkoutPlans).filter(WorkoutPlans.id == plan_id).first()
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    
    for key, value in plan.model_dump().items():
        setattr(db_plan, key, value)
    
    db.commit()
    db.refresh(db_plan)
    return db_plan

@router.delete("/plans/{plan_id}")
def delete_workout_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(WorkoutPlans).filter(WorkoutPlans.id == plan_id).first()
    if plan is None:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    
    db.delete(plan)
    db.commit()
    return {"message": "Workout plan deleted successfully"}

# Workout Plan Exercise CRUD operations
@router.post("/plans/{plan_id}/exercises", response_model=WorkoutPlanExerciseResponse)
def add_exercise_to_plan(plan_id: int, plan_exercise: WorkoutPlanExerciseCreate, db: Session = Depends(get_db)):
    # Check if plan exists
    plan = db.query(WorkoutPlans).filter(WorkoutPlans.id == plan_id).first()
    if plan is None:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    
    # Check if exercise exists
    exercise = db.query(Exercise).filter(Exercise.id == plan_exercise.exercise_id).first()
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    db_plan_exercise = WorkoutPlanExercise(
        workout_plan_id=plan_id,
        **plan_exercise.model_dump()
    )
    db.add(db_plan_exercise)
    db.commit()
    db.refresh(db_plan_exercise)
    return db_plan_exercise

@router.get("/plans/{plan_id}/exercises", response_model=List[WorkoutPlanExerciseResponse])
def get_plan_exercises(plan_id: int, db: Session = Depends(get_db)):
    plan_exercises = db.query(WorkoutPlanExercise).filter(
        WorkoutPlanExercise.workout_plan_id == plan_id
    ).order_by(WorkoutPlanExercise.order).all()
    return plan_exercises

@router.put("/plans/{plan_id}/exercises/{exercise_id}", response_model=WorkoutPlanExerciseResponse)
def update_plan_exercise(plan_id: int, exercise_id: int, plan_exercise: WorkoutPlanExerciseCreate, db: Session = Depends(get_db)):
    db_plan_exercise = db.query(WorkoutPlanExercise).filter(
        WorkoutPlanExercise.workout_plan_id == plan_id,
        WorkoutPlanExercise.id == exercise_id
    ).first()
    
    if db_plan_exercise is None:
        raise HTTPException(status_code=404, detail="Plan exercise not found")
    
    for key, value in plan_exercise.model_dump().items():
        setattr(db_plan_exercise, key, value)
    
    db.commit()
    db.refresh(db_plan_exercise)
    return db_plan_exercise

@router.delete("/plans/{plan_id}/exercises/{exercise_id}")
def remove_exercise_from_plan(plan_id: int, exercise_id: int, db: Session = Depends(get_db)):
    plan_exercise = db.query(WorkoutPlanExercise).filter(
        WorkoutPlanExercise.workout_plan_id == plan_id,
        WorkoutPlanExercise.id == exercise_id
    ).first()
    
    if plan_exercise is None:
        raise HTTPException(status_code=404, detail="Plan exercise not found")
    
    db.delete(plan_exercise)
    db.commit()
    return {"message": "Exercise removed from plan successfully"}

# Workout Progress CRUD operations
@router.post("/progress", response_model=WorkoutProgressResponse)
def log_workout_progress(progress: WorkoutProgressCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if workout plan exists
    workout = db.query(WorkoutPlans).filter(WorkoutPlans.id == progress.workout_id).first()
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    
    # Check if exercise exists
    exercise = db.query(Exercise).filter(Exercise.id == progress.exercise_id).first()
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    db_progress = WorkoutProgress(
        user_id=current_user.id,
        **progress.model_dump()
    )
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress

@router.get("/progress", response_model=List[WorkoutProgressResponse])
def get_workout_progress(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    progress = db.query(WorkoutProgress).filter(
        WorkoutProgress.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return progress

@router.get("/progress/{progress_id}", response_model=WorkoutProgressResponse)
def get_workout_progress_by_id(progress_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    progress = db.query(WorkoutProgress).filter(
        WorkoutProgress.id == progress_id,
        WorkoutProgress.user_id == current_user.id
    ).first()
    
    if progress is None:
        raise HTTPException(status_code=404, detail="Workout progress not found")
    return progress

@router.put("/progress/{progress_id}", response_model=WorkoutProgressResponse)
def update_workout_progress(progress_id: int, progress: WorkoutProgressCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_progress = db.query(WorkoutProgress).filter(
        WorkoutProgress.id == progress_id,
        WorkoutProgress.user_id == current_user.id
    ).first()
    
    if db_progress is None:
        raise HTTPException(status_code=404, detail="Workout progress not found")
    
    for key, value in progress.model_dump().items():
        setattr(db_progress, key, value)
    
    db.commit()
    db.refresh(db_progress)
    return db_progress

@router.delete("/progress/{progress_id}")
def delete_workout_progress(progress_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    progress = db.query(WorkoutProgress).filter(
        WorkoutProgress.id == progress_id,
        WorkoutProgress.user_id == current_user.id
    ).first()
    
    if progress is None:
        raise HTTPException(status_code=404, detail="Workout progress not found")
    
    db.delete(progress)
    db.commit()
    return {"message": "Workout progress deleted successfully"}

# Additional utility endpoints
@router.get("/exercises/category/{category}")
def get_exercises_by_category(category: str, db: Session = Depends(get_db)):
    exercises = db.query(Exercise).filter(Exercise.category == category).all()
    return exercises

@router.get("/exercises/difficulty/{difficulty}")
def get_exercises_by_difficulty(difficulty: str, db: Session = Depends(get_db)):
    exercises = db.query(Exercise).filter(Exercise.difficulty == difficulty).all()
    return exercises

@router.get("/plans/difficulty/{difficulty_level}")
def get_plans_by_difficulty(difficulty_level: str, db: Session = Depends(get_db)):
    plans = db.query(WorkoutPlans).filter(WorkoutPlans.difficulty_level == difficulty_level).all()
    return plans
