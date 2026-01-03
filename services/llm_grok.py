import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def generate_grok_summary(user_data, risks, nutrition_plan, exercise_plan):
    """
    Generates a SHORT, punchy AI coach message (3-4 sentences max).
    """
    
    # 1. Prepare concise context
    context_message = f"""
    PROFIL: {user_data.userId}, {user_data.age} ans, {user_data.weight}kg
    
    HABITUDES:
    - Sommeil: {user_data.hours_of_sleep}h/nuit
    - Eau: {user_data.litres_eau_jour}L/jour
    - Café: {user_data.cafe_jour} tasses
    - Activité: {user_data.daily_steps} pas/jour
    - Tension: {user_data.bp_systolic}/{user_data.bp_diastolic} mmHg
    
    RISQUES IA:
    - Diabète: {int(risks.risk_diabetes * 100)}%
    - Hypertension: {int(risks.risk_hypertension * 100)}%
    - Obésité: {int(risks.risk_obesity * 100)}%
    - Cœur: {int(risks.risk_heart_disease * 100)}%
    
    SCORE SANTÉ: {risks.health_score}/100
    """

    system_prompt = """
Tu es HealthGuardian AI, coach santé bienveillant.

📋 TÂCHE: Génère un message COURT et MOTIVANT (3-4 phrases MAXIMUM).

FORMAT OBLIGATOIRE:
"Bonjour [Prénom]! 🎯 [1-2 priorités clés avec chiffres]. [1 encouragement]. 💪"

RÈGLES STRICTES:
1. MAXIMUM 50 mots total
2. Cite 2-3 priorités MAX (les plus critiques)
3. Utilise des chiffres concrets (pas de vagues "augmenter")
4. Termine par une phrase motivante
5. Ajoute 1-2 emojis pertinents

EXEMPLES PARFAITS:

Exemple 1 (hydratation critique):
"Bonjour Ahmed! 🎯 Priorités: bois 2.5L d'eau (tu es à 1L), réduis le café à 2 tasses avant 14h. Ton score santé de 72/100 peut facilement monter à 85+ avec ces ajustements! 💪"

Exemple 2 (hypertension élevée):
"Bonjour Marie! ⚠️ Attention: ta tension (145/92) et ton risque hypertension (89%) nécessitent un suivi médical. Priorité: réduire le sel, augmenter à 6000 pas/jour. Tu peux inverser cette tendance! 💪"

Exemple 3 (tout va bien):
"Bonjour Sofiane! 🌟 Excellentes habitudes! Tes 8h de sommeil et 2L d'eau te donnent un score de 85/100. Continue comme ça, tu es sur la bonne voie! 💪"

NE JAMAIS:
- Faire plus de 4 phrases
- Lister plus de 3 priorités
- Utiliser des paragraphes longs
- Répéter ce qui est dans les recommandations structurées
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context_message}
            ],
            temperature=0.3,  # Lower for consistency
            max_tokens=150    # Force short response
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"❌ AI Error: {e}")
        return "Le service AI est momentanément indisponible."