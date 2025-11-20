from api.schemas import NutritionRequest, NutritionResponse, MealItem
from utils.data_fetcher import NutritionAPI, HealthCalculators
from typing import List
import random

async def generate_nutrition_plan(request: NutritionRequest) -> NutritionResponse:
    """
    Generate a personalized nutrition plan using OpenFoodFacts API
    
    Steps:
    1. Calculate daily calorie needs
    2. Fetch Tunisian foods from OpenFoodFacts
    3. Create balanced meal plan
    4. Return structured response
    """
    
    # 1️⃣ Calculate daily calorie target
    height_cm = request.height * 100
    bmr = HealthCalculators.calculate_bmr(
        weight_kg=request.weight,
        height_cm=height_cm,
        age=request.age
    )
    tdee = HealthCalculators.calculate_tdee(bmr, activity_level="moderate")
    
    # Adjust calories based on goal
    if request.goal == "weight_loss":
        daily_calories = int(tdee - 500)  # 500 cal deficit
    elif request.goal == "weight_gain":
        daily_calories = int(tdee + 500)  # 500 cal surplus
    else:
        daily_calories = int(tdee)
    
    # Use custom target if provided
    if request.daily_calorie_target:
        daily_calories = request.daily_calorie_target
    
    # 2️⃣ Calculate macro distribution (40% carbs, 30% protein, 30% fat)
    daily_protein = round((daily_calories * 0.30) / 4, 1)  # 4 cal/g
    daily_carbs = round((daily_calories * 0.40) / 4, 1)
    daily_fat = round((daily_calories * 0.30) / 9, 1)  # 9 cal/g
    
    # 3️⃣ Fetch food data from OpenFoodFacts
    tunisian_foods = await get_tunisian_meal_suggestions(request.dietary_restrictions)
    
    # 4️⃣ Create meal plan (distribute calories: 30% breakfast, 40% lunch, 25% dinner, 5% snacks)
    breakfast_items = create_meal(
        target_calories=daily_calories * 0.30,
        foods=tunisian_foods["breakfast"],
        meal_name="breakfast"
    )
    
    lunch_items = create_meal(
        target_calories=daily_calories * 0.40,
        foods=tunisian_foods["lunch"],
        meal_name="lunch"
    )
    
    dinner_items = create_meal(
        target_calories=daily_calories * 0.25,
        foods=tunisian_foods["dinner"],
        meal_name="dinner"
    )
    
    snack_items = create_meal(
        target_calories=daily_calories * 0.05,
        foods=tunisian_foods["snacks"],
        meal_name="snacks"
    )
    
    # 5️⃣ Generate tips
    tips = generate_nutrition_tips(request)
    
    return NutritionResponse(
        userId=request.userId,
        daily_calories=daily_calories,
        daily_protein=daily_protein,
        daily_carbs=daily_carbs,
        daily_fat=daily_fat,
        breakfast=breakfast_items,
        lunch=lunch_items,
        dinner=dinner_items,
        snacks=snack_items,
        tips=tips
    )


async def get_tunisian_meal_suggestions(dietary_restrictions: List[str]) -> dict:
    """
    Get Tunisian food suggestions organized by meal type
    Uses OpenFoodFacts API + hardcoded Tunisian staples
    """
    
    # 🇹🇳 Tunisian breakfast staples
    breakfast_foods = [
        MealItem(
            name="Café au lait + Pain complet",
            calories=250,
            protein=8,
            carbs=40,
            fat=6,
            portion="1 tasse + 2 tranches",
            tunisian_alternative="Pain maison"
        ),
        MealItem(
            name="Œufs brouillés + Harissa",
            calories=200,
            protein=14,
            carbs=3,
            fat=15,
            portion="2 œufs",
            tunisian_alternative="Œufs frais du marché"
        ),
        MealItem(
            name="Yaourt nature + Miel",
            calories=150,
            protein=8,
            carbs=20,
            fat=4,
            portion="1 bol",
            tunisian_alternative="Yaourt fermier"
        )
    ]
    
    # 🇹🇳 Tunisian lunch options
    lunch_foods = [
        MealItem(
            name="Couscous aux légumes",
            calories=450,
            protein=15,
            carbs=70,
            fat=12,
            portion="1 assiette moyenne",
            tunisian_alternative="Couscous maison"
        ),
        MealItem(
            name="Salade Méchouia",
            calories=180,
            protein=4,
            carbs=12,
            fat=14,
            portion="1 assiette",
            tunisian_alternative="Poivrons grillés maison"
        ),
        MealItem(
            name="Poisson grillé (Daurade)",
            calories=250,
            protein=35,
            carbs=0,
            fat=12,
            portion="150g",
            tunisian_alternative="Poisson frais du marché"
        ),
        MealItem(
            name="Riz aux petits pois",
            calories=280,
            protein=8,
            carbs=50,
            fat=6,
            portion="1 tasse",
            tunisian_alternative="Riz tunisien"
        )
    ]
    
    # 🇹🇳 Tunisian dinner options
    dinner_foods = [
        MealItem(
            name="Chorba (Soupe tunisienne)",
            calories=220,
            protein=12,
            carbs=30,
            fat=6,
            portion="1 bol",
            tunisian_alternative="Chorba frik"
        ),
        MealItem(
            name="Tajine tunisien",
            calories=300,
            protein=18,
            carbs=25,
            fat=14,
            portion="1 part",
            tunisian_alternative="Tajine maison"
        ),
        MealItem(
            name="Salade verte + Thon",
            calories=200,
            protein=20,
            carbs=8,
            fat=10,
            portion="1 grande assiette",
            tunisian_alternative="Thon tunisien en conserve"
        )
    ]
    
    # 🇹🇳 Tunisian snacks
    snack_foods = [
        MealItem(
            name="Fruits frais (Orange, Dattes)",
            calories=80,
            protein=1,
            carbs=20,
            fat=0,
            portion="1 portion",
            tunisian_alternative="Fruits de saison"
        ),
        MealItem(
            name="Amandes grillées",
            calories=100,
            protein=4,
            carbs=4,
            fat=9,
            portion="20g",
            tunisian_alternative="Amandes locales"
        )
    ]
    
    # Filter based on dietary restrictions
    if "diabète" in [r.lower() for r in dietary_restrictions]:
        # Remove high-sugar items
        breakfast_foods = [f for f in breakfast_foods if "miel" not in f.name.lower()]
        snack_foods = [f for f in snack_foods if "dattes" not in f.name.lower()]
    
    return {
        "breakfast": breakfast_foods,
        "lunch": lunch_foods,
        "dinner": dinner_foods,
        "snacks": snack_foods
    }


def create_meal(target_calories: float, foods: List[MealItem], meal_name: str) -> List[MealItem]:
    """
    Create a meal that approximately hits the target calories
    """
    selected_items = []
    current_calories = 0
    
    # Randomly select 2-3 items that fit the calorie budget
    available_foods = foods.copy()
    random.shuffle(available_foods)
    
    for food in available_foods[:3]:
        if current_calories + food.calories <= target_calories * 1.2:  # Allow 20% margin
            selected_items.append(food)
            current_calories += food.calories
            
            if current_calories >= target_calories * 0.8:  # Stop at 80% of target
                break
    
    return selected_items if selected_items else [available_foods[0]]


def generate_nutrition_tips(request: NutritionRequest) -> List[str]:
    """Generate personalized nutrition tips"""
    tips = [
        "💧 Buvez au moins 2 litres d'eau par jour",
        "🥗 Privilégiez les légumes tunisiens de saison (courgette, tomate, poivron)",
        "🐟 Consommez du poisson au moins 2 fois par semaine (disponible frais en Tunisie)"
    ]
    
    if request.goal == "weight_loss":
        tips.extend([
            "🚶 Marchez 30 minutes après chaque repas",
            "🍽️ Réduisez les portions de pain et de pâtes",
            "❌ Évitez les boissons sucrées (gazeuses, jus industriels)"
        ])
    elif "diabète" in [r.lower() for r in request.dietary_restrictions]:
        tips.extend([
            "📊 Contrôlez votre glycémie régulièrement",
            "🌾 Préférez les céréales complètes (pain complet, couscous complet)",
            "🍬 Limitez les pâtisseries tunisiennes sucrées (makroudh, baklawa)"
        ])
    
    return tips[:6]  # Return max 6 tips