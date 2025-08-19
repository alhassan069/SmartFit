from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import get_db
from models import NutritionalLogs, User
from typing import List, Optional
from datetime import date
from routes.user import get_current_user

router = APIRouter(prefix="/nutrition")

class NutritionalLogBase(BaseModel):
    date: date
    meal_type: Optional[str] = None
    food_name: str
    calories: Optional[int] = None
    fat: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    serving_size: Optional[str] = None

class NutritionalLogCreate(NutritionalLogBase):
    pass

class NutritionalLogUpdate(BaseModel):
    date: Optional[date] = None
    meal_type: Optional[str] = None
    food_name: Optional[str] = None
    calories: Optional[int] = None
    fat: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    serving_size: Optional[str] = None

class NutritionalLogResponse(NutritionalLogBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

@router.post("/logs", response_model=NutritionalLogResponse)
def create_nutrition_log(
    nutrition_log: NutritionalLogCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new nutrition log entry for the authenticated user"""
    db_nutrition_log = NutritionalLogs(
        user_id=current_user.id,
        **nutrition_log.model_dump()
    )
    db.add(db_nutrition_log)
    db.commit()
    db.refresh(db_nutrition_log)
    return db_nutrition_log

@router.get("/logs", response_model=List[NutritionalLogResponse])
def get_nutrition_logs(
    skip: int = 0, 
    limit: int = 100,
    date_filter: Optional[date] = None,
    meal_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(NutritionalLogs).filter(NutritionalLogs.user_id == current_user.id)
    
    if date_filter:
        query = query.filter(NutritionalLogs.date == date_filter)
    
    if meal_type:
        query = query.filter(NutritionalLogs.meal_type == meal_type)
    
    nutrition_logs = query.offset(skip).limit(limit).all()
    return nutrition_logs

@router.get("/logs/{log_id}", response_model=NutritionalLogResponse)
def get_nutrition_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    nutrition_log = db.query(NutritionalLogs).filter(
        NutritionalLogs.id == log_id,
        NutritionalLogs.user_id == current_user.id
    ).first()
    
    if nutrition_log is None:
        raise HTTPException(status_code=404, detail="Nutrition log not found")
    
    return nutrition_log

@router.get("/logs/date/{target_date}", response_model=List[NutritionalLogResponse])
def get_nutrition_logs_by_date(
    target_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    nutrition_logs = db.query(NutritionalLogs).filter(
        NutritionalLogs.user_id == current_user.id,
        NutritionalLogs.date == target_date
    ).all()
    
    return nutrition_logs

@router.get("/summary")
def get_nutrition_summary(
    start_date: date,
    end_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logs = db.query(NutritionalLogs).filter(
        NutritionalLogs.user_id == current_user.id,
        NutritionalLogs.date >= start_date,
        NutritionalLogs.date <= end_date
    ).all()
    
    total_calories = sum(log.calories or 0 for log in logs)
    total_fat = sum(log.fat or 0 for log in logs)
    total_protein = sum(log.protein or 0 for log in logs)
    total_carbs = sum(log.carbs or 0 for log in logs)
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_entries": len(logs),
        "total_calories": total_calories,
        "total_fat": round(total_fat, 2),
        "total_protein": round(total_protein, 2),
        "total_carbs": round(total_carbs, 2),
        "daily_average_calories": round(total_calories / max(1, (end_date - start_date).days + 1), 2)
    }

@router.put("/logs/{log_id}", response_model=NutritionalLogResponse)
def update_nutrition_log(
    log_id: int,
    nutrition_log_update: NutritionalLogUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    nutrition_log = db.query(NutritionalLogs).filter(
        NutritionalLogs.id == log_id,
        NutritionalLogs.user_id == current_user.id
    ).first()
    
    if nutrition_log is None:
        raise HTTPException(status_code=404, detail="Nutrition log not found")
    
    # Update only provided fields
    update_data = nutrition_log_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(nutrition_log, field, value)
    
    db.commit()
    db.refresh(nutrition_log)
    return nutrition_log


@router.delete("/logs/{log_id}")
def delete_nutrition_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    nutrition_log = db.query(NutritionalLogs).filter(
        NutritionalLogs.id == log_id,
        NutritionalLogs.user_id == current_user.id
    ).first()
    
    if nutrition_log is None:
        raise HTTPException(status_code=404, detail="Nutrition log not found")
    
    db.delete(nutrition_log)
    db.commit()
    
    return {"message": "Nutrition log deleted successfully"}

@router.delete("/logs/date/{target_date}")
def delete_nutrition_logs_by_date(
    target_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    nutrition_logs = db.query(NutritionalLogs).filter(
        NutritionalLogs.user_id == current_user.id,
        NutritionalLogs.date == target_date
    ).all()
    
    for log in nutrition_logs:
        db.delete(log)
    
    db.commit()
    
    return {"message": f"Deleted {len(nutrition_logs)} nutrition log(s) for {target_date}"}
