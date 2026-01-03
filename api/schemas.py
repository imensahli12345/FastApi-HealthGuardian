from pydantic import BaseModel, Field
from typing import Optional, List, Any
from enum import Enum

# 1. INPUT DATA (What the Frontend sends)
class UserHealthData(BaseModel):
    userId: int  # Integer ID
    age: int
    gender: int = Field(..., description="0=Male, 1=Female")
    height: float = Field(..., description="Height in meters (e.g. 1.75)")
    weight: float = Field(..., description="Weight in kg")
    
    # Lifestyle Data
    hours_of_sleep: float
    exercise_hours_per_week: float
    daily_steps: int
    
    # French names to match risk_predictor.py
    litres_eau_jour: float 
    cafe_jour: int 
    heures_travail_jour: float 
    
    bedtime_hour: str = Field(..., description="Format HH:MM (e.g. '23:30')")
    
    # Medical Data
    bp_systolic: int
    bp_diastolic: int
    
    # Text Categories
    job_type: str 
    activity_status: str
    
    # Optional
    goal: Optional[str] = "health"

# 2. RISK PREDICTION OUTPUT
class RiskPredictionResponse(BaseModel):
    userId: int  # Integer ID
    bmi: float
    health_score: float
    
    # Risk scores (0.0-1.0) - Hybrid of medical detection + ML prediction
    risk_diabetes: float
    risk_hypertension: float
    risk_obesity: float
    risk_heart_disease: float
    
    # Existing fields (backward compatible)
    recommendations: List[str]
    needs_doctor: bool
    diet_plan_type: str
    
    # NEW: Current condition detection (medical rule-based)
    current_conditions: dict = Field(
        default_factory=dict,
        description="Detected current medical conditions with classifications"
    )
    condition_severity: str = Field(
        default="normal",
        description="Overall severity: critical, warning, or normal"
    )
    severity_color: str = Field(
        default="#10B981",
        description="Hex color code for frontend display"
    )
    
    # NEW: Detection metadata for audit trail
    detection_source: dict = Field(
        default_factory=dict,
        description="Source of each risk value: 'medical_rule' or 'ml_model'"
    )

# 3. NUTRITION SCHEMAS
class MealItem(BaseModel):
    name: str
    calories: int
    protein: Optional[float] = 0
    carbs: Optional[float] = 0
    fat: Optional[float] = 0
    portion: Optional[str] = "1 portion"
    tunisian_alternative: Optional[str] = None

class NutritionRequest(BaseModel):
    userId: int  # Integer ID
    weight: float
    height: float
    age: int
    goal: str
    daily_calorie_target: Optional[int] = None  
    dietary_restrictions: List[str] = []

class NutritionResponse(BaseModel):
    userId: int  # Integer ID
    daily_calories: int
    daily_protein: float
    daily_carbs: float
    daily_fat: float
    breakfast: List[MealItem]
    lunch: List[MealItem]
    dinner: List[MealItem]
    snacks: List[MealItem]
    tips: List[str]

# 4. EXERCISE SCHEMAS
class ExerciseItem(BaseModel):
    name: str
    type: str
    duration_minutes: int
    calories_burned: int
    sets: Optional[int] = None
    reps: Optional[int] = None
    tunisian_location: Optional[str] = None
    description: Optional[str] = None

class ExerciseRequest(BaseModel):
    userId: int  # Integer ID
    fitness_level: str
    sessions_per_week: int
    goal: str
    available_equipment: str
    weight: Optional[float] = 70.0 
    medical_restrictions: List[str] = []

class ExerciseResponse(BaseModel):
    userId: int  # Integer ID
    weekly_plan: dict
    total_weekly_calories: int
    progression_notes: str
    tips: List[str]
