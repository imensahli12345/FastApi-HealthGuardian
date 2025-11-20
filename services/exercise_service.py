from api.schemas import ExerciseRequest, ExerciseResponse, ExerciseItem
from utils.data_fetcher import ExerciseAPI, HealthCalculators
from typing import List, Dict
import random

async def generate_exercise_plan(request: ExerciseRequest) -> ExerciseResponse:
    """
    Generate a personalized exercise plan using wger.de API + custom Tunisian exercises
    
    Steps:
    1. Fetch exercises from wger.de API
    2. Add Tunisia-specific exercises
    3. Create weekly schedule
    4. Calculate calorie burn
    """
    
    # 1️⃣ Get exercises based on available equipment
    if request.available_equipment == "home" or request.available_equipment == "none":
        exercises = await ExerciseAPI.get_bodyweight_exercises()
        tunisian_exercises = get_tunisian_home_exercises()
    elif request.available_equipment == "gym":
        exercises = await ExerciseAPI.get_exercises()
        tunisian_exercises = get_tunisian_gym_exercises()
    else:  # outdoor
        exercises = await ExerciseAPI.get_cardio_exercises()
        tunisian_exercises = get_tunisian_outdoor_exercises()
    
    # Combine API exercises with Tunisia-specific ones
    all_exercises = exercises + tunisian_exercises
    
    # 2️⃣ Filter exercises based on fitness level and medical restrictions
    filtered_exercises = filter_exercises(
        all_exercises,
        fitness_level=request.fitness_level,
        medical_restrictions=request.medical_restrictions
    )
    
    # 3️⃣ Create weekly schedule
    weekly_plan = create_weekly_schedule(
        exercises=filtered_exercises,
        sessions_per_week=request.sessions_per_week,
        goal=request.goal,
        fitness_level=request.fitness_level
    )
    
    # 4️⃣ Calculate total weekly calories burned
    total_calories = calculate_weekly_calories(weekly_plan, request.weight)
    
    # 5️⃣ Generate tips
    tips = generate_exercise_tips(request)
    
    # 6️⃣ Create progression notes
    progression = get_progression_notes(request.fitness_level, request.sessions_per_week)
    
    return ExerciseResponse(
        userId=request.userId,
        weekly_plan=weekly_plan,
        total_weekly_calories=total_calories,
        progression_notes=progression,
        tips=tips
    )


def get_tunisian_home_exercises() -> List[Dict]:
    """Get exercises perfect for home workout in Tunisia"""
    return [
        {
            "id": "tn_home_1",
            "name": "Pompes classiques",
            "description": "3 séries de 10-15 répétitions",
            "category": "Strength",
            "equipment": ["Aucun"],
            "muscles": ["Pectoraux", "Triceps", "Épaules"],
            "difficulty": "beginner",
            "tunisian_location": "À la maison"
        },
        {
            "id": "tn_home_2",
            "name": "Squats au poids du corps",
            "description": "3 séries de 15-20 répétitions",
            "category": "Strength",
            "equipment": ["Aucun"],
            "muscles": ["Quadriceps", "Fessiers", "Ischio-jambiers"],
            "difficulty": "beginner",
            "tunisian_location": "À la maison"
        },
        {
            "id": "tn_home_3",
            "name": "Planche abdominale",
            "description": "3 séries de 30-60 secondes",
            "category": "Core",
            "equipment": ["Tapis"],
            "muscles": ["Abdominaux", "Lombaires"],
            "difficulty": "beginner",
            "tunisian_location": "À la maison"
        },
        {
            "id": "tn_home_4",
            "name": "Burpees",
            "description": "4 séries de 10 répétitions",
            "category": "HIIT",
            "equipment": ["Aucun"],
            "muscles": ["Corps entier"],
            "difficulty": "advanced",
            "tunisian_location": "À la maison"
        }
    ]


def get_tunisian_outdoor_exercises() -> List[Dict]:
    """Get outdoor exercises perfect for Tunisia's climate and locations"""
    return [
        {
            "id": "tn_outdoor_1",
            "name": "Marche rapide (Corniche La Marsa)",
            "description": "30-45 minutes de marche rapide",
            "category": "Cardio",
            "equipment": ["Baskets"],
            "muscles": ["Jambes", "Cardio"],
            "difficulty": "beginner",
            "tunisian_location": "Corniche La Marsa, Sidi Bou Saïd"
        },
        {
            "id": "tn_outdoor_2",
            "name": "Jogging (Parc Belvédère)",
            "description": "20-30 minutes de course",
            "category": "Cardio",
            "equipment": ["Baskets"],
            "muscles": ["Jambes", "Cardio"],
            "difficulty": "intermediate",
            "tunisian_location": "Parc Belvédère, Parc Ennahli"
        },
        {
            "id": "tn_outdoor_3",
            "name": "Natation (Gammarth)",
            "description": "30-45 minutes de nage libre",
            "category": "Cardio",
            "equipment": ["Maillot"],
            "muscles": ["Corps entier"],
            "difficulty": "intermediate",
            "tunisian_location": "Plages Gammarth, Piscines municipales"
        },
        {
            "id": "tn_outdoor_4",
            "name": "Vélo (Route côtière Carthage)",
            "description": "45-60 minutes de vélo",
            "category": "Cardio",
            "equipment": ["Vélo"],
            "muscles": ["Jambes", "Cardio"],
            "difficulty": "intermediate",
            "tunisian_location": "Route Carthage-Sidi Bou Saïd"
        }
    ]


def get_tunisian_gym_exercises() -> List[Dict]:
    """Get gym exercises (for gyms like Oxygen, Fitness Zone in Tunisia)"""
    return [
        {
            "id": "tn_gym_1",
            "name": "Développé couché",
            "description": "4 séries de 8-12 répétitions",
            "category": "Strength",
            "equipment": ["Barre", "Banc"],
            "muscles": ["Pectoraux"],
            "difficulty": "intermediate",
            "tunisian_location": "Salles de gym (Oxygen, Fitness Zone)"
        },
        {
            "id": "tn_gym_2",
            "name": "Squat avec barre",
            "description": "4 séries de 10-12 répétitions",
            "category": "Strength",
            "equipment": ["Barre"],
            "muscles": ["Quadriceps", "Fessiers"],
            "difficulty": "intermediate",
            "tunisian_location": "Salles de gym"
        },
        {
            "id": "tn_gym_3",
            "name": "Rameur",
            "description": "20 minutes intensité modérée",
            "category": "Cardio",
            "equipment": ["Rameur"],
            "muscles": ["Corps entier", "Cardio"],
            "difficulty": "beginner",
            "tunisian_location": "Salles de gym"
        }
    ]


def filter_exercises(
    exercises: List[Dict],
    fitness_level: str,
    medical_restrictions: List[str]
) -> List[Dict]:
    """Filter exercises based on fitness level and medical restrictions"""
    
    filtered = []
    
    for ex in exercises:
        # Filter by difficulty
        ex_difficulty = ex.get("difficulty", "intermediate")
        
        if fitness_level == "beginner" and ex_difficulty == "advanced":
            continue
        elif fitness_level == "intermediate" and ex_difficulty == "advanced":
            continue  # Intermediate can do beginner and intermediate
        
        # Filter by medical restrictions
        skip = False
        for restriction in medical_restrictions:
            if "hypertension" in restriction.lower() and ex.get("category") == "HIIT":
                skip = True
                break
            if "articulation" in restriction.lower() and "course" in ex.get("name", "").lower():
                skip = True
                break
        
        if not skip:
            filtered.append(ex)
    
    return filtered


def create_weekly_schedule(
    exercises: List[Dict],
    sessions_per_week: int,
    goal: str,
    fitness_level: str
) -> Dict[str, List[ExerciseItem]]:
    """Create a weekly workout schedule"""
    
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    
    # Determine which days to train (evenly spaced)
    training_days = []
    if sessions_per_week == 3:
        training_days = [days[0], days[2], days[4]]  # Mon, Wed, Fri
    elif sessions_per_week == 4:
        training_days = [days[0], days[2], days[4], days[6]]  # Mon, Wed, Fri, Sun
    elif sessions_per_week == 5:
        training_days = [days[0], days[1], days[3], days[4], days[6]]
    else:
        training_days = days[:sessions_per_week]
    
    weekly_plan = {}
    
    for day in training_days:
        # Select 4-6 exercises for the day
        day_exercises = random.sample(exercises, min(5, len(exercises)))
        
        exercise_items = []
        for ex in day_exercises:
            # Estimate duration and calories based on exercise type
            if ex.get("category") == "Cardio":
                duration = 30
                calories = int(duration * 10)  # ~10 cal/min for cardio
            elif ex.get("category") == "Strength":
                duration = 15
                calories = int(duration * 6)  # ~6 cal/min for strength
            else:
                duration = 20
                calories = int(duration * 8)
            
            exercise_items.append(ExerciseItem(
                name=ex.get("name", "Unknown"),
                type=ex.get("category", "General"),
                duration_minutes=duration,
                calories_burned=calories,
                sets=3 if ex.get("category") != "Cardio" else None,
                reps=12 if ex.get("category") == "Strength" else None,
                description=ex.get("description", ""),
                tunisian_location=ex.get("tunisian_location")
            ))
        
        weekly_plan[day] = exercise_items
    
    return weekly_plan


def calculate_weekly_calories(weekly_plan: Dict, weight_kg: float) -> int:
    """Calculate total calories burned per week"""
    total = 0
    for day, exercises in weekly_plan.items():
        for ex in exercises:
            total += ex.calories_burned
    return total


def generate_exercise_tips(request: ExerciseRequest) -> List[str]:
    """Generate personalized exercise tips"""
    tips = [
        "💧 Hydratez-vous bien avant, pendant et après l'exercice",
        "🌅 Évitez de vous entraîner aux heures les plus chaudes en Tunisie (12h-16h)",
        "👟 Portez des chaussures adaptées pour éviter les blessures"
    ]
    
    if request.fitness_level == "beginner":
        tips.extend([
            "🐢 Commencez doucement et augmentez progressivement l'intensité",
            "📅 Gardez au moins 1 jour de repos entre les séances",
            "🎯 Concentrez-vous sur la bonne technique avant d'augmenter la charge"
        ])
    
    if request.goal == "weight_loss":
        tips.extend([
            "🔥 Combinez cardio et musculation pour de meilleurs résultats",
            "⏱️ Privilégiez les entraînements de 45-60 minutes",
            "🚶 Marchez dès que possible (escaliers, transports en commun)"
        ])
    
    if request.available_equipment == "outdoor":
        tips.extend([
            "🏖️ Profitez des espaces publics tunisiens (plages, parcs, corniche)",
            "☀️ Utilisez de la crème solaire pour les activités en extérieur",
            "👥 Entraînez-vous en groupe pour plus de motivation"
        ])
    
    return tips[:6]


def get_progression_notes(fitness_level: str, sessions_per_week: int) -> str:
    """Generate progression notes"""
    
    if fitness_level == "beginner":
        return f"""
🎯 Plan de progression (Débutant - {sessions_per_week} séances/semaine):

Semaines 1-2: Habituation
- Concentrez-vous sur l'apprentissage des mouvements
- Intensité légère à modérée
- Écoutez votre corps

Semaines 3-4: Augmentation progressive
- Augmentez légèrement la durée des exercices (+5 min)
- Maintenez l'intensité modérée

Semaines 5-8: Consolidation
- Ajoutez des variantes aux exercices de base
- Vous pouvez ajouter 1 séance supplémentaire/semaine

Après 8 semaines: Passage niveau intermédiaire possible
"""
    
    elif fitness_level == "intermediate":
        return f"""
🎯 Plan de progression (Intermédiaire - {sessions_per_week} séances/semaine):

Semaines 1-4: Intensification
- Augmentez les charges/intensité de 10-15%
- Travaillez la technique avancée

Semaines 5-8: Spécialisation
- Focalisez sur vos objectifs spécifiques
- Introduisez des techniques avancées (supersets, HIIT)

Après 8 semaines: Possibilité de passer au niveau avancé
"""
    
    else:  # advanced
        return f"""
🎯 Plan de progression (Avancé - {sessions_per_week} séances/semaine):

Programme optimisé pour performances maximales:
- Périodisation de l'entraînement
- Techniques avancées (drop sets, pyramides)
- Récupération active importante
- Suivi nutritionnel précis recommandé
"""