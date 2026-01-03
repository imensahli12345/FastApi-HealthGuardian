import asyncio
from fastapi import APIRouter, HTTPException
from api.schemas import (
    UserHealthData, 
    RiskPredictionResponse,
    NutritionRequest,
    NutritionResponse,
    ExerciseRequest,
    ExerciseResponse
)

# 📦 IMPORTS
from services.risk_predictor import predict_health_risks
from services.nutrition_service import generate_nutrition_plan
from services.exercise_service import generate_exercise_plan
from services.llm_grok import generate_grok_summary 
from services.chatbot_service import generate_chatbot_response 

router = APIRouter()

# ==========================================
# 🚀 1. THE MASTER ENDPOINT (Main Feature)
# ==========================================
@router.post("/generate-full-plan")
async def generate_full_health_plan(data: UserHealthData):
    print("🚀 Starting Full Plan Generation...")

    # 1️⃣ Step 1: ML Model
    try:
        risk_prediction = predict_health_risks(data)
        print("✅ Risk Prediction done.")
    except Exception as e:
        print(f"❌ ML Error: {e}")
        raise HTTPException(status_code=500, detail=f"Model Error: {e}")

    risk_dict = {
        "diabetes": risk_prediction.risk_diabetes,
        "hypertension": risk_prediction.risk_hypertension,
        "obesity": risk_prediction.risk_obesity,
        "heart": risk_prediction.risk_heart_disease
    }

    # 2️⃣ Step 2: Prepare Requests
    try:
        nutri_req = NutritionRequest(
            userId=str(data.userId),
            weight=float(data.weight),
            height=float(data.height),
            age=int(data.age),
            goal="weight_loss" if risk_prediction.risk_obesity > 0.5 else "maintenance",
            dietary_restrictions=[],
            daily_calorie_target=None 
        )
        
        sport_req = ExerciseRequest(
            userId=str(data.userId),
            fitness_level="beginner" if data.daily_steps < 4000 else "intermediate",
            sessions_per_week=3,
            goal="weight_loss",
            available_equipment="home",
            weight=float(data.weight),
            medical_restrictions=[]
        )
        print("✅ Request Objects Created.")
    except Exception as e:
        print(f"❌ Error creating request objects: {e}")
        raise HTTPException(status_code=500, detail=f"Schema Error: {e}")

    # 3️⃣ Step 3: Run Generators
    try:
        nutrition_plan = await generate_nutrition_plan(nutri_req, risk_dict)
        print("✅ Nutrition Plan Generated.")
        
        exercise_plan = await generate_exercise_plan(sport_req, risk_dict)
        print("✅ Exercise Plan Generated.")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ API Generation Error: {e}")
        raise HTTPException(status_code=500, detail=f"Plan Generation Error: {str(e)}")

    # 4️⃣ Step 4: Grok
    try:
        ai_message = generate_grok_summary(
            user_data=data,
            risks=risk_prediction,
            nutrition_plan=nutrition_plan,
            exercise_plan=exercise_plan
        )
        print("✅ Grok Message Generated.")
    except Exception as e:
        print(f"⚠️ Grok Error: {e}")
        ai_message = "Plan généré avec succès (Message AI indisponible)."

    return {
        "status": "success",
        "ai_coach_message": ai_message,
        "health_analysis": risk_prediction,
        "nutrition_schedule": nutrition_plan,
        "workout_schedule": exercise_plan
    }

# ==========================================
# 🛠️ 2. INDIVIDUAL ENDPOINTS (For Testing)
# ==========================================

@router.post("/predict-risks", response_model=RiskPredictionResponse)
def predict_risks_endpoint(data: UserHealthData):
    try:
        return predict_health_risks(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/nutrition/recommend", response_model=NutritionResponse)
async def recommend_nutrition(request: NutritionRequest):
    try:
        return await generate_nutrition_plan(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exercise/recommend", response_model=ExerciseResponse)
async def recommend_exercise(request: ExerciseRequest):
    try:
        return await generate_exercise_plan(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chatbot")
async def chatbot(request: dict):
    """
    Endpoint for the AI Chatbot.
    Expected JSON: { "question": "...", "user_data": {...} }
    """
    question = request.get("question", "")
    user_data_dict = request.get("user_data", None)
    
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    # 1. Calculate Risks if user data is present
    risks = None
    if user_data_dict:
        try:
            # Convert dict to Pydantic model
            user_health_data = UserHealthData(**user_data_dict)
            
            # Predict Risks
            risk_response = predict_health_risks(user_health_data)
            
            # Convert to simple dict for chatbot
            risks = {
                "risk_diabetes": risk_response.risk_diabetes,
                "risk_hypertension": risk_response.risk_hypertension,
                "risk_obesity": risk_response.risk_obesity,
                "risk_heart_disease": risk_response.risk_heart_disease
            }
            
            # 🛡️ HARD SAFETY GUARD: Prevent risk override when vitals are normal
            # If BP is normal (<130/80), cap hypertension risk to prevent false diagnosis
            bp_sys = user_data_dict.get("bp_systolic", 0)
            bp_dia = user_data_dict.get("bp_diastolic", 0)
            
            if bp_sys < 130 and bp_dia < 80:
                # BP is normal - cap hypertension risk to prevent AI from treating it as current condition
                risks["risk_hypertension"] = min(risks["risk_hypertension"], 0.49)
                print(f"🛡️ Safety Guard: BP normal ({bp_sys}/{bp_dia}), capped hypertension risk to {int(risks['risk_hypertension']*100)}%")
            
            print("✅ Chatbot: Risks calculated successfully.")
        except Exception as e:
            print(f"⚠️ Chatbot Risk Calculation Error: {e}")
            # We continue without risks if calculation fails
            risks = None

    # 2. Generate Response
    answer = generate_chatbot_response(question, user_data_dict, risks)
    
    return {
        "answer": answer,
        "question": question,
        "risks_used": risks  # Helpful for debugging
    }