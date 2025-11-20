from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="HealthGuardian AI",
    description="AI-powered nutrition and exercise recommendation system",
    version="1.0.0"
)

# Configure CORS (allow Spring Boot backend to call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Spring Boot default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class HealthProfile(BaseModel):
    age: int
    weight: float
    height: float
    activity_level: str
    health_goals: List[str]
    dietary_restrictions: Optional[List[str]] = None

class NutritionRecommendation(BaseModel):
    meal_type: str
    foods: List[str]
    calories: float
    protein: float
    carbs: float
    fats: float

# Root endpoint
@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "HealthGuardian AI",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/api/nutrition/recommend",
            "/api/exercise/recommend"
        ]
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "HealthGuardian AI"}

# Nutrition recommendation endpoint
@app.post("/api/nutrition/recommend")
async def recommend_nutrition(profile: HealthProfile):
    # Placeholder - we'll implement this with real data later
    return {
        "status": "success",
        "message": "Nutrition recommendations generated",
        "profile": profile.dict(),
        "recommendations": [
            {
                "meal_type": "breakfast",
                "foods": ["Whole grain bread", "Olive oil", "Tomatoes"],
                "calories": 350,
                "protein": 12,
                "carbs": 45,
                "fats": 15
            }
        ]
    }

# Exercise recommendation endpoint
@app.post("/api/exercise/recommend")
async def recommend_exercise(profile: HealthProfile):
    # Placeholder - we'll implement this with real data later
    return {
        "status": "success",
        "message": "Exercise recommendations generated",
        "profile": profile.dict(),
        "recommendations": [
            {
                "exercise": "Walking",
                "duration_minutes": 30,
                "intensity": "moderate",
                "calories_burned": 150
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)