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

# 📊 Base User Health Data
class UserHealthData(BaseModel):
    userId: int = Field(..., description="User ID from Spring Boot")
    age: int = Field(..., ge=10, le=120, description="Age in years")
    weight: float = Field(..., gt=0, description="Weight in kg")
    height: float = Field(..., gt=0, description="Height in meters")
    medical_history: Optional[str] = Field(None, description="Existing conditions")
    blood_pressure: Optional[int] = Field(None, description="Systolic BP")
    
    class Config:
        schema_extra = {
            "example": {
                "userId": 123,
                "age": 35,
                "weight": 75.5,
                "height": 1.75,
                "medical_history": "Diabète type 2",
                "blood_pressure": 130
            }
        }

# 🔮 Risk Prediction Response
class RiskPredictionResponse(BaseModel):
    userId: int
    bmi: float
    health_score: float = Field(..., ge=0, le=100, description="Overall health score")
    risk_diabetes: float = Field(..., ge=0, le=1, description="Diabetes risk 0-1")
    risk_hypertension: float = Field(..., ge=0, le=1, description="Hypertension risk 0-1")
    risk_obesity: float = Field(..., ge=0, le=1, description="Obesity risk 0-1")
    recommendations: List[str]
    
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