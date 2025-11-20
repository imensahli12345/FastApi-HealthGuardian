from fastapi import APIRouter, HTTPException
from api.schemas import (
    UserHealthData,
    RiskPredictionResponse,
    NutritionRequest,
    NutritionResponse,
    ExerciseRequest,
    ExerciseResponse
)
from services.risk_predictor import predict_health_risks
from services.nutrition_service import generate_nutrition_plan
from services.exercise_service import generate_exercise_plan

router = APIRouter()

# 🔮 Risk Prediction Endpoint
@router.post("/predict-risks", response_model=RiskPredictionResponse)
async def predict_risks(data: UserHealthData):
    """
    Predict health risks based on user data
    
    - **age**: User age in years
    - **weight**: Weight in kg
    - **height**: Height in meters
    - **medical_history**: Existing conditions (optional)
    """
    try:
        prediction = predict_health_risks(data)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# 🍽️ Nutrition Plan Endpoint
@router.post("/nutrition/recommend", response_model=NutritionResponse)
async def recommend_nutrition(request: NutritionRequest):
    """
    Generate personalized nutrition plan using OpenFoodFacts API
    
    - **userId**: User ID from Spring Boot
    - **age, weight, height**: Physical metrics
    - **goal**: weight_loss, weight_gain, maintenance
    - **dietary_restrictions**: allergies, diabetes, etc.
    """
    try:
        nutrition_plan = await generate_nutrition_plan(request)
        return nutrition_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nutrition generation failed: {str(e)}")

# 💪 Exercise Plan Endpoint
@router.post("/exercise/recommend", response_model=ExerciseResponse)
async def recommend_exercise(request: ExerciseRequest):
    """
    Generate personalized exercise plan using wger.de API
    
    - **userId**: User ID
    - **fitness_level**: beginner, intermediate, advanced
    - **goal**: weight_loss, muscle_gain, endurance
    - **available_equipment**: home, gym, outdoor
    """
    try:
        exercise_plan = await generate_exercise_plan(request)
        return exercise_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exercise generation failed: {str(e)}")

# 🤖 Chatbot Endpoint (Placeholder for Person 4)
@router.post("/chatbot")
async def chatbot(question: dict):
    """
    Medical chatbot - Will be implemented by Person 4
    """
    return {
        "answer": "Chatbot functionality coming soon!",
        "question": question.get("question", "")
    }