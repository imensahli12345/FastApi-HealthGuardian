import joblib
import pandas as pd
import numpy as np
import os
from api.schemas import UserHealthData, RiskPredictionResponse

# 1. Load Model & Features
current_dir = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(current_dir, "..", "models", "health_risk_model.joblib")
FEATURES_PATH = os.path.join(current_dir, "..", "models", "model_features.joblib")

try:
    model = joblib.load(MODEL_PATH)
    model_features = joblib.load(FEATURES_PATH)
    print("✅ AI Brain Loaded Successfully")
except Exception as e:
    print(f"❌ Error loading AI model: {e}")
    model = None
    model_features = []

def predict_health_risks(data: UserHealthData) -> RiskPredictionResponse:
    if not model:
        raise RuntimeError("AI Model is not loaded. Check server logs.")

    # 2. Calculate BMI
    bmi = round(data.weight / (data.height ** 2), 2)

    # 3. Convert Bedtime (HH:MM) to numeric (e.g. 23:30 -> 23.5)
    try:
        h, m = map(int, data.bedtime_hour.split(':'))
        bedtime_num = h + (m / 60)
    except:
        bedtime_num = 23.0 # Default if error

    # 4. Prepare Input DataFrame (Initialize with 0s)
    # We create a single row dataframe with columns matching the training data

    #create empty data frame with columns matching the training data , empty data frame with columns matching the training data
    #What it does: Creates a single-row dataframe filled with zeros, with columns matching those from training:

#All columns are initialized to 0
#Will be filled with actual user data next
#Ensures the model receives data in the exact format it expects
    input_df = pd.DataFrame(0, index=[0], columns=model_features)

    # 5. Fill Numeric Data
    # Map Schema fields to Model Columns
    input_df['Age'] = data.age
    input_df['Gender'] = data.gender
    input_df['BMI'] = bmi
    input_df['Hours_of_Sleep'] = data.hours_of_sleep
    input_df['Exercise_Hours_per_Week'] = data.exercise_hours_per_week
    input_df['Daily_Steps'] = data.daily_steps
    input_df['litres_eau_jour'] = data.water_liters
    input_df['cafe_jour'] = data.coffee_cups
    input_df['heures_travail_jour'] = data.work_hours
    input_df['BP_Systolic'] = data.bp_systolic
    input_df['BP_Diastolic'] = data.bp_diastolic
    input_df['heure_coucher_num'] = bedtime_num

    # 6. Fill Categorical Data (One-Hot Encoding)
    # Example: If job is 'Bureau', we set column 'metier_Bureau' to 1
    #One-Hot Encoding Rule: Only the user's actual category gets a 1, everything else is 0
#   Mutually Exclusive: A person can only have ONE job type at a time (they can't be both IT/Tech AND Bureau)
#   The Model Understands: When the model sees [0, 0, 1, 0, 0, 0, ...], it knows "this person is Bureau"
    job_col = f"metier_{data.job_type}"
    if job_col in input_df.columns:
        input_df[job_col] = 1
        
    status_col = f"statut_activite_{data.activity_status}"
    if status_col in input_df.columns:
        input_df[status_col] = 1

    # 7. Predict!
    # probas is a list of arrays (one per disease)
    #geting the probabilty from the model for each disease
    probas = model.predict_proba(input_df)
    
    # Extract probabilities (Class 1 = 'Yes')
    risk_diabetes = float(probas[0][0][1])
    risk_hypertension = float(probas[1][0][1])
    risk_obesity = float(probas[2][0][1])
    risk_heart = float(probas[3][0][1])

    # 8. Generate Logic-Based Advice

    #generating helath advice we should do that with LLM and api externe instead of hardcoded logic
    recommendations = []
    needs_doctor = False
    diet_plan = "balanced"

    # Alert Logic
    if risk_diabetes > 0.6:
        recommendations.append("🚨 Risque Diabète élevé : Consultez un médecin rapidement.")
        needs_doctor = True
        diet_plan = "low_sugar"
    
    if risk_hypertension > 0.6:
        recommendations.append("❤️ Attention à votre tension : Réduisez le sel.")
        diet_plan = "low_salt" if diet_plan != "low_sugar" else "complex"

    if risk_obesity > 0.5:
        recommendations.append("⚖️ Objectif poids : Un déficit calorique est recommandé.")
        
    # Hygiene Logic
    if data.daily_steps < 4000:
        recommendations.append("🚶 Vous êtes sédentaire. Essayez de marcher 30min par jour.")
    
    if data.water_liters < 1.5:
        recommendations.append("💧 Hydratez-vous plus (minimum 1.5L/jour).")

    # Default message if healthy
    if not recommendations:
        recommendations.append("✅ Excellent ! Continuez vos bonnes habitudes.")

    # Calculate Score (100 - average risk)
    avg_risk = (risk_diabetes + risk_hypertension + risk_obesity + risk_heart) / 4
    health_score = round(100 - (avg_risk * 100), 1)

    return RiskPredictionResponse(
        userId=data.userId,
        bmi=bmi,
        health_score=health_score,
        risk_diabetes=round(risk_diabetes, 2),
        risk_hypertension=round(risk_hypertension, 2),
        risk_obesity=round(risk_obesity, 2),
        risk_heart_disease=round(risk_heart, 2),
        recommendations=recommendations,
        needs_doctor=needs_doctor,
        diet_plan_type=diet_plan
    )