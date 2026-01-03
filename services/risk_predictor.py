import joblib
import pandas as pd
import numpy as np
import logging
from api.schemas import UserHealthData, RiskPredictionResponse
from services.medical_detector import get_detector

# Configure logging for audit trail
logger = logging.getLogger(__name__)

# Load the pre-trained model and features at startup
try:
    model = joblib.load("models/health_risk_model.joblib")  # ✅ Correct filename
    model_features = joblib.load("models/model_features.joblib")
    print("✅ AI Brain Loaded Successfully")
except Exception as e:
    print(f"❌ Failed to load AI model: {e}")
    model = None
    model_features = None

def predict_health_risks(data: UserHealthData) -> RiskPredictionResponse:
    """
    Predicts health risks using hybrid approach:
    1. Medical rule-based detection for current conditions
    2. ML model for future risk prediction
    3. Per-condition max() logic to combine both
    """
    if not model:
        raise RuntimeError("AI Model is not loaded. Check server logs.")
    
    # ===== STEP 1: Calculate Basic Metrics ===== 
    
    bmi = round(data.weight / (data.height ** 2), 2)
    
    # Convert bedtime to numeric (hour as float)
    try:
        hour, minute = data.bedtime_hour.split(":")
        bedtime_numeric = int(hour) + int(minute) / 60
    except:
        bedtime_numeric = 23.0  # Default
    
    # ===== STEP 2: Medical Rule-Based Detection =====
    detector = get_detector()
    
    # Detect current conditions using clinical thresholds
    obesity_risk, obesity_classification, obesity_severity = detector.detect_obesity_status(bmi)
    hypertension_risk, hypertension_classification, hypertension_severity = detector.detect_hypertension_status(
        data.bp_systolic, data.bp_diastolic
    )
    diabetes_risk, diabetes_classification, diabetes_severity = detector.detect_diabetes_risk(
        bmi, data.age, data.activity_status, data.hours_of_sleep
    )
    
    # Heart disease detection requires hypertension status
    has_hypertension = hypertension_risk is not None and hypertension_risk >= 0.85
    risk_factors_count = sum([
        bmi >= 30,
        has_hypertension,
        data.exercise_hours_per_week < 2,
        data.hours_of_sleep < 6,
        data.daily_steps < 5000
    ])
    
    heart_disease_risk, heart_classification, heart_severity = detector.detect_heart_disease_risk(
        has_hypertension, bmi, data.age, data.exercise_hours_per_week, risk_factors_count
    )
    
    logger.info(f"Medical detection completed for user {data.userId}")
    
    # ===== STEP 3: ML Model Prediction =====
    # Prepare input data
    input_data = {
        'age': data.age,
        'gender': data.gender,
        'height': data.height,
        'weight': data.weight,
        'bmi': bmi,
        'hours_of_sleep': data.hours_of_sleep,
        'exercise_hours_per_week': data.exercise_hours_per_week,
        'daily_steps': data.daily_steps,
        'litres_eau_jour': data.litres_eau_jour,
        'cafe_jour': data.cafe_jour,
        'heures_travail_jour': data.heures_travail_jour,
        'bedtime': bedtime_numeric,
        'bp_systolic': data.bp_systolic,
        'bp_diastolic': data.bp_diastolic,
        'job_type': data.job_type,
        'activity_status': data.activity_status
    }
    
    # Convert to DataFrame
    input_df = pd.DataFrame([input_data])
    
    # One-hot encode categorical features if needed
    if model_features:
        # Get categorical columns
        categorical_cols = ['job_type', 'activity_status']
        
        for col in categorical_cols:
            if col in input_df.columns:
                # One-hot encode and align with model features
                dummies = pd.get_dummies(input_df[col], prefix=col)
                input_df = pd.concat([input_df, dummies], axis=1)
                input_df = input_df.drop(columns=[col])
        
        # Align columns with model features
        missing_cols = set(model_features) - set(input_df.columns)
        for col in missing_cols:
            input_df[col] = 0
        
        input_df = input_df[model_features]
    
    # Make ML predictions (probabilities)
    probas = model.predict_proba(input_df)
    
    # Extract ML risk probabilities
    ml_risk_diabetes = float(probas[0][0][1]) if len(probas) > 0 else 0.0
    ml_risk_hypertension = float(probas[1][0][1]) if len(probas) > 1 else 0.0
    ml_risk_obesity = float(probas[2][0][1]) if len(probas) > 2 else 0.0
    ml_risk_heart_disease = float(probas[3][0][1]) if len(probas) > 3 else 0.0
    
    logger.info(f"ML prediction completed for user {data.userId}")
    
    # ===== STEP 4: Hybrid Merge (Per-Condition Max Logic) =====
    # For each condition, use max(medical_rule, ML_prediction)
    # If medical_rule is None, use ML prediction
    
    final_risk_diabetes = diabetes_risk if diabetes_risk is not None else ml_risk_diabetes
    final_risk_diabetes = max(final_risk_diabetes, ml_risk_diabetes)
    
    final_risk_hypertension = hypertension_risk if hypertension_risk is not None else ml_risk_hypertension
    final_risk_hypertension = max(final_risk_hypertension, ml_risk_hypertension)
    
    final_risk_obesity = obesity_risk if obesity_risk is not None else ml_risk_obesity
    final_risk_obesity = max(final_risk_obesity, ml_risk_obesity)
    
    final_risk_heart_disease = heart_disease_risk if heart_disease_risk is not None else ml_risk_heart_disease
    final_risk_heart_disease = max(final_risk_heart_disease, ml_risk_heart_disease)
    
    # ===== STEP 5: Build Current Conditions Report =====
    current_conditions = {}
    severities = []
    
    if obesity_classification and obesity_classification != "Normal Weight":
        current_conditions['obesity'] = f"{obesity_classification} (BMI {bmi})"
        severities.append(obesity_severity)
    
    if hypertension_classification and hypertension_classification != "Normal Blood Pressure":
        current_conditions['hypertension'] = f"{hypertension_classification} ({data.bp_systolic}/{data.bp_diastolic})"
        severities.append(hypertension_severity)
    
    if diabetes_classification:
        current_conditions['diabetes'] = diabetes_classification
        severities.append(diabetes_severity)
    
    if heart_classification:
        current_conditions['heart_disease'] = heart_classification
        severities.append(heart_severity)
    
    # Determine overall severity
    overall_severity = detector.get_overall_severity(severities) if severities else "normal"
    severity_color = detector.get_severity_color(overall_severity)
    
    # ===== STEP 6: Detection Source Tracking (Audit Trail) =====
    detection_source = {
        'diabetes': 'medical_rule' if diabetes_risk is not None else 'ml_model',
        'hypertension': 'medical_rule' if hypertension_risk is not None else 'ml_model',
        'obesity': 'medical_rule' if obesity_risk is not None else 'ml_model',
        'heart_disease': 'medical_rule' if heart_disease_risk is not None else 'ml_model'
    }
    
    logger.info(f"Hybrid merge completed. Detection sources: {detection_source}")
    
    # ===== STEP 7: Calculate Health Score =====
    avg_risk = (final_risk_diabetes + final_risk_hypertension + final_risk_obesity + final_risk_heart_disease) / 4
    health_score = round((1 - avg_risk) * 100, 1)
    
    # ===== STEP 8: Generate Recommendations =====
    recommendations = []
    needs_doctor = False
    diet_plan_type = "balanced"
    
    # Critical condition alerts (use "You have" language)
    if overall_severity == "critical":
        needs_doctor = True
        
        if final_risk_obesity >= 0.95:
            if bmi >= 40:
                recommendations.append("🚨 Vous avez une obésité sévère (Classe III). Consultation médicale urgente recommandée.")
            elif bmi >= 35:
                recommendations.append("⚠️ Vous avez une obésité modérée (Classe II). Consultez un médecin.")
            else:
                recommendations.append("⚖️ Vous êtes obèse. Programme de perte de poids recommandé.")
            diet_plan_type = "weight_loss"
        
        if final_risk_hypertension >= 0.95:
            if data.bp_systolic >= 180 or data.bp_diastolic >= 120:
                recommendations.append("🚨🚨 URGENCE: Crise hypertensive détectée! Consultez immédiatement un médecin ou appelez les urgences.")
            elif data.bp_systolic >= 140 or data.bp_diastolic >= 90:
                recommendations.append("❤️ Vous avez une hypertension de stade 2. Réduisez le sel et consultez un médecin.")
            else:
                recommendations.append("❤️ Vous avez une hypertension de stade 1. Surveillez votre tension.")
            diet_plan_type = "low_salt"
    
    # Warning level alerts
    if overall_severity == "warning":
        if final_risk_diabetes >= 0.70:
            recommendations.append("⚠️ Risque élevé de diabète. Consultez un médecin pour un dépistage.")
            needs_doctor = True
            diet_plan_type = "low_sugar"
        
        if 25 <= bmi < 30:
            recommendations.append("⚖️ Vous êtes en surpoids. Une activité physique régulière est recommandée.")
    
    # Lifestyle recommendations (for all)
    if data.daily_steps < 5000:
        recommendations.append("🚶 Augmentez votre activité: Essayez de marcher 30 min par jour.")
    
    if data.litres_eau_jour < 1.5:
        recommendations.append("💧 Hydratez-vous plus (minimum 1.5L/jour).")
    
    if data.hours_of_sleep < 6:
        recommendations.append("😴 Sommeil insuffisant. Visez 7-9h par nuit pour une meilleure santé.")
    
    if data.cafe_jour > 4:
        recommendations.append("☕ Réduisez votre consommation de café (>4 tasses/jour).")
    
    # If no issues found
    if not recommendations:
        recommendations.append("✅ Bonne santé! Continuez vos bonnes habitudes.")
    
    # ===== STEP 9: Audit Log =====
    logger.info(
        f"Risk assessment completed for user {data.userId}: "
        f"Severity={overall_severity}, Conditions={len(current_conditions)}, "
        f"Diabetes={final_risk_diabetes:.2f}, Hypertension={final_risk_hypertension:.2f}, "
        f"Obesity={final_risk_obesity:.2f}, Heart={final_risk_heart_disease:.2f}"
    )
    
    # ===== STEP 10: Return Response =====
    return RiskPredictionResponse(
        userId=int(data.userId),
        bmi=bmi,
        health_score=health_score,
        risk_diabetes=final_risk_diabetes,
        risk_hypertension=final_risk_hypertension,
        risk_obesity=final_risk_obesity,
        risk_heart_disease=final_risk_heart_disease,
        recommendations=recommendations,
        needs_doctor=needs_doctor,
        diet_plan_type=diet_plan_type,
        current_conditions=current_conditions,
        condition_severity=overall_severity,
        severity_color=severity_color,
        detection_source=detection_source
    )
