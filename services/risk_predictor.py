from api.schemas import UserHealthData, RiskPredictionResponse
from utils.data_fetcher import HealthCalculators
from typing import List

def predict_health_risks(data: UserHealthData) -> RiskPredictionResponse:
    """
    Predict health risks based on user data
    
    NOTE: This is a PLACEHOLDER using rule-based logic.
    In Week 2-3, you'll train an actual ML model (Random Forest/XGBoost)
    and load it here using joblib.
    
    For now, we use BMI and age-based risk assessment.
    """
    
    # Calculate BMI
    bmi = HealthCalculators.calculate_bmi(data.weight, data.height)
    bmi_category = HealthCalculators.get_bmi_category(bmi)
    
    # Rule-based risk assessment (temporary, will be replaced with ML model)
    risk_diabetes = calculate_diabetes_risk(data, bmi)
    risk_hypertension = calculate_hypertension_risk(data, bmi)
    risk_obesity = 0.0 if bmi < 30 else min((bmi - 30) / 10, 1.0)
    
    # Calculate overall health score (0-100)
    health_score = calculate_health_score(bmi, data.age, risk_diabetes, risk_hypertension)
    
    # Generate recommendations
    recommendations = generate_recommendations(
        bmi_category,
        risk_diabetes,
        risk_hypertension,
        data.medical_history
    )
    
    return RiskPredictionResponse(
        userId=data.userId,
        bmi=bmi,
        health_score=health_score,
        risk_diabetes=risk_diabetes,
        risk_hypertension=risk_hypertension,
        risk_obesity=risk_obesity,
        recommendations=recommendations
    )


def calculate_diabetes_risk(data: UserHealthData, bmi: float) -> float:
    """
    Calculate diabetes risk (0-1 scale)
    
    Risk factors:
    - BMI > 25 (overweight)
    - Age > 45
    - Family history (in medical_history)
    - High blood pressure
    """
    risk = 0.0
    
    # BMI factor (40% of risk)
    if bmi >= 30:  # Obese
        risk += 0.4
    elif bmi >= 25:  # Overweight
        risk += 0.2
    
    # Age factor (30% of risk)
    if data.age >= 60:
        risk += 0.3
    elif data.age >= 45:
        risk += 0.15
    
    # Blood pressure factor (20% of risk)
    if data.blood_pressure and data.blood_pressure >= 140:
        risk += 0.2
    elif data.blood_pressure and data.blood_pressure >= 130:
        risk += 0.1
    
    # Medical history factor (10% of risk)
    if data.medical_history:
        history_lower = data.medical_history.lower()
        if "diabète" in history_lower or "diabetes" in history_lower:
            risk = 0.9  # Already has diabetes
        elif "prédiabète" in history_lower:
            risk += 0.1
    
    return min(risk, 1.0)  # Cap at 1.0


def calculate_hypertension_risk(data: UserHealthData, bmi: float) -> float:
    """
    Calculate hypertension (high blood pressure) risk (0-1 scale)
    
    Risk factors:
    - High BMI
    - Age > 40
    - Already high blood pressure readings
    """
    risk = 0.0
    
    # BMI factor (30% of risk)
    if bmi >= 30:
        risk += 0.3
    elif bmi >= 25:
        risk += 0.15
    
    # Age factor (30% of risk)
    if data.age >= 60:
        risk += 0.3
    elif data.age >= 40:
        risk += 0.15
    
    # Blood pressure reading (40% of risk)
    if data.blood_pressure:
        if data.blood_pressure >= 180:  # Stage 2 hypertension
            risk = 1.0
        elif data.blood_pressure >= 140:  # Stage 1 hypertension
            risk += 0.4
        elif data.blood_pressure >= 130:  # Elevated
            risk += 0.2
    else:
        risk += 0.1  # Unknown BP is a minor risk
    
    # Medical history
    if data.medical_history:
        history_lower = data.medical_history.lower()
        if "hypertension" in history_lower:
            risk = 0.95  # Already has hypertension
    
    return min(risk, 1.0)


def calculate_health_score(
    bmi: float,
    age: int,
    risk_diabetes: float,
    risk_hypertension: float
) -> float:
    """
    Calculate overall health score (0-100)
    
    100 = Excellent health
    80-99 = Good health
    60-79 = Fair health
    40-59 = Poor health
    0-39 = High risk
    """
    score = 100.0
    
    # Deduct points for BMI
    if bmi < 18.5:  # Underweight
        score -= 20
    elif bmi >= 30:  # Obese
        score -= 30
    elif bmi >= 25:  # Overweight
        score -= 15
    
    # Deduct points for age (minor factor)
    if age >= 60:
        score -= 10
    elif age >= 50:
        score -= 5
    
    # Deduct points for disease risks
    score -= risk_diabetes * 25  # Up to -25 points
    score -= risk_hypertension * 25  # Up to -25 points
    
    return max(round(score, 1), 0.0)  # Never below 0


def generate_recommendations(
    bmi_category: str,
    risk_diabetes: float,
    risk_hypertension: float,
    medical_history: str
) -> List[str]:
    """Generate personalized health recommendations"""
    
    recommendations = []
    
    # BMI-based recommendations
    if bmi_category == "Obese":
        recommendations.append("⚠️ Votre IMC indique une obésité. Consultez un médecin pour un plan de perte de poids adapté.")
        recommendations.append("🏃 Commencez par 30 minutes de marche rapide par jour (Corniche La Marsa)")
        recommendations.append("🍽️ Réduisez les portions et privilégiez les légumes")
    elif bmi_category == "Overweight":
        recommendations.append("📊 Votre IMC indique un surpoids léger. Un ajustement alimentaire peut aider.")
        recommendations.append("🚶 Augmentez votre activité physique quotidienne")
    elif bmi_category == "Underweight":
        recommendations.append("⚠️ Votre IMC est bas. Consultez un nutritionniste pour augmenter sainement votre poids.")
        recommendations.append("🍗 Augmentez votre apport en protéines et calories")
    else:  # Normal
        recommendations.append("✅ Votre IMC est dans la norme. Maintenez vos bonnes habitudes!")
    
    # Diabetes risk recommendations
    if risk_diabetes >= 0.7:
        recommendations.append("🚨 RISQUE ÉLEVÉ de diabète - Consultez immédiatement un médecin")
        recommendations.append("🍬 Éliminez les boissons sucrées et pâtisseries")
        recommendations.append("📊 Faites un dépistage de glycémie")
    elif risk_diabetes >= 0.4:
        recommendations.append("⚠️ Risque modéré de diabète - Surveillance recommandée")
        recommendations.append("🥗 Réduisez les glucides raffinés (pain blanc, pâtes)")
        recommendations.append("🏃 Pratiquez 150 min d'activité physique/semaine")
    
    # Hypertension risk recommendations
    if risk_hypertension >= 0.7:
        recommendations.append("🚨 RISQUE ÉLEVÉ d'hypertension - Consultez un cardiologue")
        recommendations.append("🧂 Réduisez drastiquement votre consommation de sel")
        recommendations.append("💊 Un traitement médical peut être nécessaire")
    elif risk_hypertension >= 0.4:
        recommendations.append("⚠️ Risque modéré d'hypertension - Surveillez votre tension")
        recommendations.append("🧂 Limitez le sel et les aliments transformés")
        recommendations.append("🧘 Pratiquez des exercices de relaxation (yoga, méditation)")
    
    # Medical history specific recommendations
    if medical_history:
        history_lower = medical_history.lower()
        if "diabète" in history_lower or "diabetes" in history_lower:
            recommendations.append("💉 Suivez rigoureusement votre traitement pour le diabète")
            recommendations.append("📊 Contrôlez votre glycémie quotidiennement")
        if "hypertension" in history_lower:
            recommendations.append("💊 Prenez vos médicaments anti-hypertension régulièrement")
            recommendations.append("📈 Mesurez votre tension artérielle chaque semaine")
    
    # General recommendations (always include)
    recommendations.append("💧 Buvez au moins 2 litres d'eau par jour")
    recommendations.append("😴 Dormez 7-8 heures par nuit")
    recommendations.append("🏥 Faites un bilan de santé annuel")
    
    return recommendations[:8]  # Return max 8 recommendations