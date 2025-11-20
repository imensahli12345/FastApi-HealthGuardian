import requests
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🍽️ OpenFoodFacts API - FREE & UNLIMITED
class NutritionAPI:
    BASE_URL = "https://world.openfoodfacts.org/cgi/search.pl"
    
    @staticmethod
    async def search_food(query: str, country: str = "Tunisia") -> List[Dict]:
        """
        Search for food items in OpenFoodFacts database
        
        Args:
            query: Food name (e.g., "couscous", "harissa")
            country: Country filter (default Tunisia)
        
        Returns:
            List of food items with nutritional data
        """
        try:
            params = {
                "search_terms": query,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": 20,
                "fields": "product_name,brands,nutriments,serving_size,countries_tags"
            }
            
            response = requests.get(NutritionAPI.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            products = data.get("products", [])
            
            # Filter and format results
            formatted = []
            for product in products[:10]:  # Take top 10
                nutriments = product.get("nutriments", {})
                formatted.append({
                    "name": product.get("product_name", "Unknown"),
                    "brand": product.get("brands", "Generic"),
                    "calories": nutriments.get("energy-kcal_100g", 0),
                    "protein": nutriments.get("proteins_100g", 0),
                    "carbs": nutriments.get("carbohydrates_100g", 0),
                    "fat": nutriments.get("fat_100g", 0),
                    "fiber": nutriments.get("fiber_100g", 0),
                    "serving_size": product.get("serving_size", "100g")
                })
            
            logger.info(f"Found {len(formatted)} food items for '{query}'")
            return formatted
            
        except Exception as e:
            logger.error(f"OpenFoodFacts API error: {str(e)}")
            return []
    
    @staticmethod
    async def get_tunisian_foods() -> List[Dict]:
        """Get common Tunisian foods"""
        tunisian_dishes = [
            "couscous", "tajine", "brik", "harissa", "mechouia",
            "lablabi", "makroudh", "chorba", "kafteji", "ojja"
        ]
        
        all_foods = []
        for dish in tunisian_dishes[:5]:  # Limit to avoid rate limiting
            foods = await NutritionAPI.search_food(dish)
            all_foods.extend(foods)
        
        return all_foods


# 💪 wger.de Exercise API - FREE & UNLIMITED
class ExerciseAPI:
    BASE_URL = "https://wger.de/api/v2"
    
    @staticmethod
    async def get_exercises(
        language: str = "en",
        category: Optional[int] = None,
        equipment: Optional[int] = None
    ) -> List[Dict]:
        """
        Get exercises from wger.de database
        
        Args:
            language: Language code (2 for English, 4 for French)
            category: Exercise category (8=Arms, 10=Legs, 11=Abs, 12=Back, 13=Shoulders, 14=Chest)
            equipment: Equipment ID (1=Barbell, 3=Dumbbell, 7=Bodyweight, 10=Kettlebell)
        
        Returns:
            List of exercises with details
        """
        try:
            params = {
                "language": 2,  # English
                "limit": 100
            }
            
            if category:
                params["category"] = category
            if equipment:
                params["equipment"] = equipment
            
            response = requests.get(
                f"{ExerciseAPI.BASE_URL}/exercise/",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            exercises = data.get("results", [])
            
            # Format results
            formatted = []
            for ex in exercises:
                formatted.append({
                    "id": ex.get("id"),
                    "name": ex.get("name", "Unknown Exercise"),
                    "description": ex.get("description", ""),
                    "category": ex.get("category", {}).get("name", "General"),
                    "equipment": [eq.get("name") for eq in ex.get("equipment", [])],
                    "muscles": [m.get("name") for m in ex.get("muscles", [])],
                    "difficulty": "intermediate"  # Default value
                })
            
            logger.info(f"Found {len(formatted)} exercises")
            return formatted
            
        except Exception as e:
            logger.error(f"wger.de API error: {str(e)}")
            return []
    
    @staticmethod
    async def get_bodyweight_exercises() -> List[Dict]:
        """Get exercises that don't require equipment (perfect for Tunisia)"""
        return await ExerciseAPI.get_exercises(equipment=7)  # 7 = Bodyweight
    
    @staticmethod
    async def get_cardio_exercises() -> List[Dict]:
        """Get cardio exercises"""
        # wger doesn't have a direct cardio category, so we'll create custom ones
        return [
            {
                "id": "cardio_1",
                "name": "Marche rapide (La Marsa Corniche)",
                "description": "30-45 minutes de marche rapide le long de la corniche",
                "category": "Cardio",
                "equipment": ["Aucun"],
                "muscles": ["Jambes", "Cardio"],
                "difficulty": "beginner",
                "tunisian_location": "Corniche La Marsa, Sidi Bou Saïd"
            },
            {
                "id": "cardio_2",
                "name": "Course à pied (Parc Belvédère)",
                "description": "20-30 minutes de jogging",
                "category": "Cardio",
                "equipment": ["Aucun"],
                "muscles": ["Jambes", "Cardio"],
                "difficulty": "intermediate",
                "tunisian_location": "Parc Belvédère, Tunis"
            },
            {
                "id": "cardio_3",
                "name": "Natation (Plages Gammarth)",
                "description": "30-45 minutes de nage libre",
                "category": "Cardio",
                "equipment": ["Maillot de bain"],
                "muscles": ["Corps entier"],
                "difficulty": "intermediate",
                "tunisian_location": "Plages Gammarth, piscines municipales"
            }
        ]


# 🧮 Health Calculators
class HealthCalculators:
    @staticmethod
    def calculate_bmi(weight_kg: float, height_m: float) -> float:
        """Calculate Body Mass Index"""
        return round(weight_kg / (height_m ** 2), 2)
    
    @staticmethod
    def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str = "male") -> float:
        """
        Calculate Basal Metabolic Rate (Mifflin-St Jeor Equation)
        
        Returns: Daily calories needed at rest
        """
        if gender.lower() == "male":
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        
        return round(bmr, 2)
    
    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str = "moderate") -> float:
        """
        Calculate Total Daily Energy Expenditure
        
        activity_level: sedentary, light, moderate, active, very_active
        """
        multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }
        
        return round(bmr * multipliers.get(activity_level, 1.55), 2)
    
    @staticmethod
    def get_bmi_category(bmi: float) -> str:
        """Get BMI category"""
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 25:
            return "Normal"
        elif 25 <= bmi < 30:
            return "Overweight"
        else:
            return "Obese"