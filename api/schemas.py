from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

# 🎯 Enums for controlled values
class Goal(str, Enum):
    weight_loss = "weight_loss"
    weight_gain = "weight_gain"
    maintenance = "maintenance"
    muscle_gain = "muscle_gain"

class FitnessLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class EquipmentType(str, Enum):
    home = "home"
    gym = "gym"
    outdoor = "outdoor"
    none = "none"


    
# 🍽️ Nutrition Request
class NutritionRequest(BaseModel):
    userId: int
    age: int
    weight: float
    height: float
    goal: Goal = Goal.maintenance
    dietary_restrictions: Optional[List[str]] = Field(default=[], description="Allergies, diabetes, etc.")
    cuisine_preference: Optional[str] = Field("tunisian", description="Preferred cuisine")
    daily_calorie_target: Optional[int] = Field(None, description="Target calories/day")
    
    class Config:
        schema_extra = {
            "example": {
                "userId": 123,
                "age": 30,
                "weight": 70,
                "height": 1.70,
                "goal": "weight_loss",
                "dietary_restrictions": ["diabète"],
                "cuisine_preference": "tunisian"
            }
        }

# 🍽️ Meal Item
class MealItem(BaseModel):
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    portion: str
    tunisian_alternative: Optional[str] = None

# 🍽️ Nutrition Response
class NutritionResponse(BaseModel):
    userId: int
    daily_calories: int
    daily_protein: float
    daily_carbs: float
    daily_fat: float
    breakfast: List[MealItem]
    lunch: List[MealItem]
    dinner: List[MealItem]
    snacks: List[MealItem]
    tips: List[str]

# 💪 Exercise Request
class ExerciseRequest(BaseModel):
    userId: int
    age: int
    weight: float
    height: float
    fitness_level: FitnessLevel = FitnessLevel.beginner
    goal: Goal = Goal.maintenance
    available_equipment: EquipmentType = EquipmentType.home
    medical_restrictions: Optional[List[str]] = Field(default=[], description="Health limitations")
    sessions_per_week: int = Field(3, ge=1, le=7, description="Training frequency")
    
    class Config:
        schema_extra = {
            "example": {
                "userId": 123,
                "age": 30,
                "weight": 70,
                "height": 1.70,
                "fitness_level": "beginner",
                "goal": "weight_loss",
                "available_equipment": "home",
                "medical_restrictions": ["hypertension"],
                "sessions_per_week": 3
            }
        }

# 💪 Exercise Item
class ExerciseItem(BaseModel):
    name: str
    type: str  # cardio, strength, flexibility
    duration_minutes: int
    calories_burned: int
    sets: Optional[int] = None
    reps: Optional[int] = None
    description: str
    tunisian_location: Optional[str] = None

# 💪 Exercise Response
class ExerciseResponse(BaseModel):
    userId: int
    weekly_plan: dict  # {"Monday": [exercises], "Wednesday": [...]}
    total_weekly_calories: int
    progression_notes: str
    tips: List[str]


# 1. INPUT DATA (What the Frontend sends)
class UserHealthData(BaseModel):
    userId: int
    age: int
    gender: int = Field(..., description="0=Male, 1=Female")
    height: float = Field(..., description="Height in meters (e.g. 1.75)")
    weight: float = Field(..., description="Weight in kg")
    
    # Lifestyle Data
    hours_of_sleep: float
    exercise_hours_per_week: float
    daily_steps: int
    water_liters: float = Field(..., alias="litres_eau_jour") # Alias handles mapping
    coffee_cups: int = Field(..., alias="cafe_jour")
    work_hours: float = Field(..., alias="heures_travail_jour")
    bedtime_hour: str = Field(..., description="Format HH:MM (e.g. '23:30')")
    
    # Medical Data
    bp_systolic: int
    bp_diastolic: int
    
    # Text Categories (We will convert these to numbers)
    job_type: str = Field(..., description="IT/Tech, Santé, Bureau, Commerce, Industrie, Enseignement")
    activity_status: str = Field(..., description="Working, Student, Inactive")

# 🚨 UPDATED: Includes specific risks and diet plans
class RiskPredictionResponse(BaseModel):
    userId: int
    bmi: float
    health_score: float
    
    # Probabilities
    risk_diabetes: float
    risk_hypertension: float
    risk_obesity: float
    risk_heart_disease: float
    
    # Advice
    recommendations: List[str]
    needs_doctor: bool
    diet_plan_type: str # "balanced", "low_sugar", "low_salt"