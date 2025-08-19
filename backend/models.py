from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from db import Base
from typing import List

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    weight = Column(Integer)
    height = Column(Integer)
    fitness_goals = Column(Text)
    medical_conditions = Column(Text)
    activity_level = Column(String)
    created_at = Column(DateTime, default=func.now())

    workout_progress = relationship("WorkoutProgress", back_populates="user", cascade="all, delete-orphan")
    nutritional_logs = relationship("NutritionalLogs", back_populates="user", cascade="all, delete-orphan")
    



class WorkoutPlans(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_name = Column(String, nullable=False)
    difficulty_level = Column(String)
    duration = Column(String)
    exercises = relationship("WorkoutPlanExercise", back_populates="workout_plan")
    progress = relationship("WorkoutProgress", back_populates="workout_plan")

class Exercise(Base):
    __tablename__ = "exercise"

    id = Column(Integer, primary_key=True, index=True)
    exercise_name = Column(String, nullable=False)
    category = Column(String)
    equipment_needed = Column(String)
    difficulty = Column(String)
    instructions = Column(Text)
    target_muscle = Column(String)

    workout_plans = relationship("WorkoutPlanExercise", back_populates="exercise")


class WorkoutPlanExercise(Base):
    __tablename__ = "workout_plan_exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    workout_plan_id = Column(Integer, ForeignKey('workout_plans.id'), nullable=False)
    exercise_id = Column(Integer, ForeignKey('exercise.id'), nullable=False)
    sets = Column(Integer, nullable=True)
    reps = Column(Integer, nullable=True)
    duration = Column(String(50), nullable=True)
    order = Column(Integer, nullable=True)  # For exercise sequence
    
    # Relationships
    workout_plan = relationship("WorkoutPlans", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="workout_plans")



class WorkoutProgress(Base):
    __tablename__ = "workout_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    workout_id = Column(Integer, ForeignKey('workout_plans.id'), nullable=False)
    exercise_id = Column(Integer, ForeignKey('exercise.id'), nullable=False)
    date = Column(Date, nullable=False)
    sets = Column(Integer)
    reps = Column(Integer)
    weights = Column(Integer)
    duration = Column(String)
    notes = Column(Text)

    user = relationship("User", back_populates="workout_progress")
    workout_plan = relationship("WorkoutPlans", back_populates="progress")
    exercise = relationship("Exercise")


class NutritionalLogs(Base):
    __tablename__ = "nutrition"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(Date, nullable=False)
    meal_type = Column(String)
    food_name = Column(String)
    calories = Column(Integer)
    fat = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    serving_size = Column(String)

    user = relationship("User", back_populates="nutritional_logs")
    




