from fastapi import APIRouter, HTTPException
from api.schemas import (
    UserHealthData, 
    RiskPredictionResponse,
    NutritionRequest,
    NutritionResponse,
    ExerciseRequest,
    ExerciseResponse
)
# Import your services
from services.risk_predictor import predict_health_risks
from services.nutrition_service import generate_nutrition_plan
from services.exercise_service import generate_exercise_plan

router = APIRouter()

# ==========================================
# 🤖 1. AI RISK PREDICTION (Your Trained Model)
# ==========================================
@router.post("/predict-risks", response_model=RiskPredictionResponse)
def predict_risks_endpoint(data: UserHealthData):  # <--- No 'async' here
    try:
        result = predict_health_risks(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 🥗 2. NUTRITION GENERATOR
# ==========================================
@router.post("/nutrition/recommend", response_model=NutritionResponse)
async def recommend_nutrition(request: NutritionRequest):
    """
    Generates a Tunisian-adapted nutrition plan
    """
    try:
        # call the service function
        plan = await generate_nutrition_plan(request)
        return plan
    except Exception as e:
        print(f"❌ Error in nutrition generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 🏋️ 3. EXERCISE GENERATOR
# ==========================================
@router.post("/exercise/recommend", response_model=ExerciseResponse)
async def recommend_exercise(request: ExerciseRequest):
    """
    Generates a workout plan based on equipment and location
    """
    try:
        # call the service function
        plan = await generate_exercise_plan(request)
        return plan
    except Exception as e:
        print(f"❌ Error in exercise generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
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