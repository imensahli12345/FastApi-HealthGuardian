"""
Medical Condition Detection Module

Uses clinical guidelines (WHO/AHA) to detect current medical conditions
based on measurable health metrics. This is separate from ML-based risk prediction.

Author: HealthGuardian AI
Last Updated: 2025-12-30
"""

import json
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Configure logging for audit trail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load medical thresholds from config
CONFIG_PATH = Path(__file__).parent.parent / "config" / "medical_thresholds.json"

try:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        MEDICAL_THRESHOLDS = json.load(f)
    logger.info("✅ Medical thresholds loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load medical thresholds: {e}")
    MEDICAL_THRESHOLDS = None


class MedicalConditionDetector:
    """Detects current medical conditions using clinical thresholds"""
    
    def __init__(self):
        if not MEDICAL_THRESHOLDS:
            raise RuntimeError("Medical thresholds configuration not loaded")
        self.thresholds = MEDICAL_THRESHOLDS
        
    def detect_obesity_status(self, bmi: float) -> Tuple[Optional[float], Optional[str], str]:
        """
        Detect obesity classification based on BMI
        
        Args:
            bmi: Body Mass Index value
            
        Returns:
            Tuple of (risk_value, classification, severity)
            - risk_value: 0.0-1.0 if condition detected, None if use ML
            - classification: Medical classification string
            - severity: 'critical', 'warning', or 'normal'
        """
        bmi_thresholds = self.thresholds['bmi_thresholds']
        
        # Check in order of severity (highest to lowest)
        for category in ['severe_obesity', 'moderate_obesity', 'obesity', 'overweight', 'underweight']:
            threshold = bmi_thresholds[category]
            
            # Edge case handling: Use < for max to avoid overlap (e.g., BMI=30.0 is obesity, not overweight)
            if threshold['min'] <= bmi < threshold['max']:
                risk = threshold['risk_value']
                classification = threshold['classification']
                severity = threshold['severity']
                
                logger.info(f"Obesity detection: BMI={bmi:.1f} → {classification} (Risk={risk})")
                return risk, classification, severity
        
        # Normal range
        logger.info(f"Obesity detection: BMI={bmi:.1f} → Normal (Using ML prediction)")
        return None, "Normal Weight", "normal"
    
    def detect_hypertension_status(
        self, 
        systolic: int, 
        diastolic: int
    ) -> Tuple[Optional[float], Optional[str], str]:
        """
        Detect hypertension classification based on blood pressure
        
        Args:
            systolic: Systolic BP (mmHg)
            diastolic: Diastolic BP (mmHg)
            
        Returns:
            Tuple of (risk_value, classification, severity)
        """
        bp_thresholds = self.thresholds['blood_pressure_thresholds']
        
        # Check in order of severity (highest to lowest)
        for category in ['hypertensive_crisis', 'stage_2_hypertension', 'stage_1_hypertension', 'elevated']:
            threshold = bp_thresholds[category]
            operator = threshold.get('operator', 'OR')
            
            # Determine if condition is met
            systolic_check = systolic >= threshold.get('systolic_min', 0) if 'systolic_min' in threshold else True
            diastolic_check = diastolic >= threshold.get('diastolic_min', 0) if 'diastolic_min' in threshold else True
            
            # Apply operator logic
            if operator == 'OR':
                condition_met = systolic_check or diastolic_check
            else:  # AND
                condition_met = systolic_check and diastolic_check
            
            if condition_met:
                risk = threshold['risk_value']
                classification = threshold['classification']
                severity = threshold['severity']
                
                logger.info(
                    f"Hypertension detection: BP={systolic}/{diastolic} → {classification} (Risk={risk})"
                )
                return risk, classification, severity
        
        # Normal range
        logger.info(f"Hypertension detection: BP={systolic}/{diastolic} → Normal (Using ML prediction)")
        return None, "Normal Blood Pressure", "normal"
    
    def detect_diabetes_risk(
        self,
        bmi: float,
        age: int,
        activity_status: str,
        hours_of_sleep: float
    ) -> Tuple[Optional[float], Optional[str], str]:
        """
        Detect diabetes risk based on composite indicators
        
        Args:
            bmi: Body Mass Index
            age: Patient age
            activity_status: Activity level (e.g., 'Sédentaire')
            hours_of_sleep: Daily sleep hours
            
        Returns:
            Tuple of (risk_value, classification, severity)
        """
        diabetes_factors = self.thresholds['diabetes_risk_factors']
        
        # Check high-risk combination
        high_risk = diabetes_factors['high_risk_combo']
        conditions = high_risk['conditions']
        
        if (bmi >= conditions['bmi_min'] and 
            'sédentaire' in activity_status.lower() and
            hours_of_sleep <= conditions['sleep_hours_max']):
            
            logger.info(
                f"Diabetes risk: BMI={bmi}, Activity={activity_status}, "
                f"Sleep={hours_of_sleep}h → High Risk"
            )
            return (
                high_risk['risk_value'],
                high_risk['classification'],
                high_risk['severity']
            )
        
        # Check moderate-risk combination
        moderate_risk = diabetes_factors['moderate_risk_combo']
        conditions = moderate_risk['conditions']
        
        if age >= conditions['age_min'] and bmi >= conditions['bmi_min']:
            logger.info(f"Diabetes risk: Age={age}, BMI={bmi} → Moderate Risk")
            return (
                moderate_risk['risk_value'],
                moderate_risk['classification'],
                moderate_risk['severity']
            )
        
        # No rule-based detection, use ML
        logger.info("Diabetes risk: No high-risk indicators → Using ML prediction")
        return None, None, "normal"
    
    def detect_heart_disease_risk(
        self,
        has_hypertension: bool,
        bmi: float,
        age: int,
        exercise_hours_per_week: float,
        risk_factors_count: int
    ) -> Tuple[Optional[float], Optional[str], str]:
        """
        Detect cardiovascular disease risk based on composite indicators
        
        Args:
            has_hypertension: Whether patient has hypertension
            bmi: Body Mass Index
            age: Patient age
            exercise_hours_per_week: Weekly exercise hours
            risk_factors_count: Number of other risk factors
            
        Returns:
            Tuple of (risk_value, classification, severity)
        """
        heart_factors = self.thresholds['heart_disease_risk_factors']
        
        # Check high-risk combination
        high_risk = heart_factors['high_risk_combo']
        conditions = high_risk['conditions']
        
        if (has_hypertension and 
            bmi >= conditions['bmi_min'] and
            exercise_hours_per_week <= conditions['exercise_hours_max']):
            
            logger.info(
                f"Heart disease risk: Hypertension={has_hypertension}, BMI={bmi}, "
                f"Exercise={exercise_hours_per_week}h/week → High Risk"
            )
            return (
                high_risk['risk_value'],
                high_risk['classification'],
                high_risk['severity']
            )
        
        # Check moderate-risk combination
        moderate_risk = heart_factors['moderate_risk_combo']
        conditions = moderate_risk['conditions']
        
        if age >= conditions['age_min'] and risk_factors_count >= conditions['multiple_risk_factors']:
            logger.info(
                f"Heart disease risk: Age={age}, Risk factors={risk_factors_count} → Moderate Risk"
            )
            return (
                moderate_risk['risk_value'],
                moderate_risk['classification'],
                moderate_risk['severity']
            )
        
        # No rule-based detection, use ML
        logger.info("Heart disease risk: No high-risk indicators → Using ML prediction")
        return None, None, "normal"
    
    def get_overall_severity(self, severities: list) -> str:
        """
        Determine overall severity from multiple conditions
        
        Args:
            severities: List of severity levels
            
        Returns:
            Overall severity: 'critical', 'warning', or 'normal'
        """
        if 'critical' in severities:
            return 'critical'
        elif 'warning' in severities:
            return 'warning'
        else:
            return 'normal'
    
    def get_severity_color(self, severity: str) -> str:
        """
        Get hex color code for severity level
        
        Args:
            severity: Severity level
            
        Returns:
            Hex color code
        """
        return self.thresholds['severity_colors'].get(severity, '#6B7280')


# Singleton instance
_detector_instance = None

def get_detector() -> MedicalConditionDetector:
    """Get singleton instance of medical detector"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = MedicalConditionDetector()
    return _detector_instance
