import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"), 
    base_url="https://api.groq.com/openai/v1"
)

def classify_question_type(question: str) -> str:
    """
    Classifies question as 'simple' or 'complex' to determine response length.
    
    Simple: Yes/no questions, single clarifications, quick advice
    Complex: Symptom analysis, multiple factors, health concerns
    """
    question_lower = question.lower()
    
    # Simple question indicators
    simple_indicators = [
        "puis-je", "est-ce que", "combien", "quand", "quelle heure",
        "c'est bon", "c'est mauvais", "c'est bien", "ok de", "normal de",
        "dois-je", "faut-il", "oui ou non"
    ]
    
    # Complex question indicators
    complex_indicators = [
        "pourquoi", "comment", "expliqu", "analyse", "symptôme", "symptom",
        "fatigue", "mal", "douleur", "inquiet", "préoccup", "problème",
        "santé", "risque", "maladie", "que faire"
    ]
    
    # Check for simple patterns
    if any(indicator in question_lower for indicator in simple_indicators):
        # But if it also has complex indicators, it's complex
        if any(indicator in question_lower for indicator in complex_indicators):
            return "complex"
        return "simple"
    
    # Check for complex patterns
    if any(indicator in question_lower for indicator in complex_indicators):
        return "complex"
    
    # Default: if short (<50 chars), probably simple; otherwise complex
    return "simple" if len(question) < 50 else "complex"


def generate_chatbot_response(user_question: str, user_data: dict = None, risks: dict = None):
    """
    Generates medically safe responses using BOTH current measurements AND AI predictions.
    Adapts response length based on question complexity.
    """
    
    # 1. Classify question type
    question_type = classify_question_type(user_question)
    
    # 2. Build comprehensive context
    context_str = build_context(user_data, risks)
    
    # 3. Base medical safety rules (common to both types)
    base_instructions = f"""
Tu es HealthGuardian Assistant, un assistant de prévention santé basé sur l'IA.

{context_str}

═══ RÈGLES MÉDICALES ESSENTIELLES ═══
🚫 Ne JAMAIS diagnostiquer de maladies
🚫 Ne JAMAIS dire "tu as [maladie]"
✅ Utiliser "peut contribuer", "suggère", "associé à"
✅ Toujours terminer par: "Cette analyse est informative, pas un avis médical."

═══ INTERPRÉTATION DES DONNÉES ═══
- Mesures actuelles = État PRÉSENT (peut causer symptômes maintenant)
- Risques IA = Trajectoire FUTURE (prédiction, pas diagnostic)
- Les prédictions IA INCLUENT déjà les mesures actuelles
- Risque élevé + mesures normales = OPPORTUNITÉ DE PRÉVENTION

"""
    
    # 4. Question-specific instructions
    if question_type == "simple":
        specific_instructions = """
═══ MODE: QUESTION SIMPLE ═══

Cette question nécessite une réponse COURTE et DIRECTE.

FORMAT OBLIGATOIRE (2-4 phrases max):
1. Réponse directe (oui/non + nuance si besoin)
2. Raison principale (1 phrase, cite données pertinentes)
3. Conseil pratique court si applicable

LONGUEUR: Maximum 4 phrases. Sois concis!

EXEMPLES:

Q: "Puis-je manger 2 morceaux de gâteau?"
A: "Oui, occasionnellement c'est bien. Avec ton poids stable et tes bonnes 
habitudes (8h sommeil, 2L eau), 2 morceaux de temps en temps sont OK. Évite 
juste d'en faire une habitude quotidienne, surtout vu ton risque hypertension. 
Cette analyse est informative, pas un avis médical."

Q: "Le café le soir, c'est mauvais?"
A: "Oui, évite après 16h. Tu prends déjà 4 cafés/jour, et le café peut perturber 
ton sommeil même si tu dors actuellement 8h. Garde tes cafés pour le matin. 
Cette analyse est informative, pas un avis médical."
"""
        max_tokens = 250
        
    else:  # complex
        specific_instructions = """
═══ MODE: QUESTION COMPLEXE ═══

Cette question nécessite une analyse DÉTAILLÉE avec le cadre complet.

FORMAT OBLIGATOIRE:

**📊 État Actuel** (basé sur tes mesures):
[Mesures EXACTES et leur interprétation]

**🔍 Facteurs Expliquant Tes Symptômes Actuels**:
[Liste numérotée avec chiffres exacts, du plus au moins probable]

**🎯 Analyse de Risque IA** (trajectoire future):
[Si risque >40%: expliquer ce que le modèle a détecté]
[Faire le LIEN entre facteurs actuels et risque futur]

**✅ Plan d'Action** (spécifique et mesurable):
1. [Action avec chiffre cible]
2. [Deuxième action]
3. [Quand consulter médecin]

**💡 Perspective**:
[Phrase encourageante sur la prévention]

⚠️ Cette analyse est informative, pas un avis médical.

═══ SCÉNARIOS D'INTERPRÉTATION ═══

SCÉNARIO A: Mesures normales + Risque IA élevé (>60%)
→ C'est une FENÊTRE DE PRÉVENTION - Valorise cette opportunité!
→ "Tes mesures actuelles sont bonnes. Cependant, ton profil de risque IA 
montre [X]% de risque. Ces mêmes facteurs qui [impact actuel] sont aussi ceux 
qui mènent à [condition] à long terme. C'est ton moment idéal pour prévenir."

SCÉNARIO B: Mesures anormales + Risque IA élevé (>60%)
→ Prédiction CONFIRMÉE - Recommande consultation
→ "🚨 Tes mesures [préciser] indiquent [état actuel]. Ton évaluation IA 
confirme ce pattern. Tu dois consulter un médecin."

SCÉNARIO C: Mesures normales + Risque IA faible (<30%)
→ SANTÉ OPTIMALE - Encourage maintien
→ "Excellente nouvelle! Tes mesures sont saines ET ton profil de risque est 
faible. Continue comme ça!"

SCÉNARIO D: Mesures anormales + Risque IA faible (<30%)
→ Problème TEMPORAIRE probable - Recommande monitoring
→ "Ta mesure [X] est élevée, mais ton profil de risque global est faible. 
Cela suggère un problème temporaire. Re-vérifie dans [délai]."

═══ FACTEURS DE MODE DE VIE ═══

SOMMEIL:
- Impact immédiat: Fatigue, maux de tête
- Impact long terme: Diabète, hypertension
- Connexion: "Ton sommeil de 5h cause ta fatigue MAINTENANT, et c'est aussi 
pourquoi le modèle prédit [X]% risque diabète à long terme."

HYDRATATION:
- Impact immédiat: Maux de tête, fatigue
- Minimum: 1.5L | Recommandé: 2-3L
- Ajustement: +500ml par café au-delà de 2

ACTIVITÉ:
- Recommandé: 8000-10000 pas/jour
- Toujours citer le nombre EXACT de pas

CAFÉ:
- Sain: 1-3 tasses/jour
- >4 tasses: Problèmes sommeil, anxiété
"""
        max_tokens = 800
    
    # 5. Combine instructions
    system_prompt = base_instructions + specific_instructions
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question}
            ],
            temperature=0.2,  # Lower for medical consistency
            max_tokens=max_tokens,  # Adaptive based on question type
            top_p=0.9,
            frequency_penalty=0.3
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"❌ Chatbot Error: {e}")
        return "Désolé, une erreur technique s'est produite. Réessaie dans un instant."


def build_context(user_data: dict = None, risks: dict = None) -> str:
    """Builds context string with pattern interpretation"""
    
    context_str = "═══ DONNÉES UTILISATEUR ═══\n"
    
    if user_data:
        context_str += f"""
Profil:
- ID: {user_data.get('userId', 'Utilisateur')}
- Âge: {user_data.get('age', 'N/A')} ans
- Poids: {user_data.get('weight', 'N/A')} kg
- Objectif: {user_data.get('goal', 'Santé générale')}

Mesures Vitales:
- Tension artérielle: {user_data.get('bp_systolic', 'N/A')}/{user_data.get('bp_diastolic', 'N/A')} mmHg

Habitudes Quotidiennes:
- Sommeil: {user_data.get('hours_of_sleep', 'N/A')}h/nuit (Coucher: {user_data.get('bedtime_hour', 'N/A')})
- Activité: {user_data.get('daily_steps', 'N/A')} pas/jour
- Exercice: {user_data.get('exercise_hours_per_week', 'N/A')}h/semaine
- Hydratation: {user_data.get('litres_eau_jour', 'N/A')}L/jour
- Café: {user_data.get('cafe_jour', 'N/A')} tasses/jour
- Travail: {user_data.get('heures_travail_jour', 'N/A')}h/jour (Type: {user_data.get('job_type', 'N/A')})
"""
    else:
        context_str += "(Aucune donnée utilisateur disponible)\n"

    if risks:
        context_str += f"""
═══ PRÉDICTIONS IA (Risques Futurs Calculés) ═══
- Diabète (risque estimé): {int(risks.get('risk_diabetes', 0) * 100)}%
- Hypertension (risque estimé): {int(risks.get('risk_hypertension', 0) * 100)}%
- Obésité (risque estimé): {int(risks.get('risk_obesity', 0) * 100)}%
- Maladie Cardiaque (risque estimé): {int(risks.get('risk_heart_disease', 0) * 100)}%
"""
        
        # Add pattern interpretation
        if user_data:
            pattern = interpret_pattern(user_data, risks)
            context_str += f"""
═══ INTERPRÉTATION DU PATTERN ═══
{pattern}
"""
    
    return context_str


def interpret_pattern(user_data: dict, risks: dict) -> str:
    """Interprets the relationship between current measurements and AI predictions"""
    
    bp_sys = user_data.get('bp_systolic', 120)
    bp_dia = user_data.get('bp_diastolic', 80)
    
    max_risk_name = max(risks.items(), key=lambda x: x[1])[0] if risks else None
    max_risk_value = max(risks.values()) if risks else 0
    
    bp_normal = bp_sys < 130 and bp_dia < 80
    bp_high = bp_sys >= 140 or bp_dia >= 90
    
    risk_names = {
        'risk_diabetes': 'diabète',
        'risk_hypertension': 'hypertension',
        'risk_obesity': 'obésité',
        'risk_heart_disease': 'maladie cardiaque'
    }
    
    if bp_normal and max_risk_value > 0.6:
        return f"""
TYPE: Fenêtre de Prévention (OPPORTUNITÉ)
- Tension actuelle: NORMALE ({bp_sys}/{bp_dia})
- Risque IA le plus élevé: {risk_names.get(max_risk_name, max_risk_name)} à {int(max_risk_value*100)}%

INTERPRÉTATION: L'utilisateur est en bonne santé MAINTENANT, mais le modèle détecte 
des patterns de mode de vie qui mènent typiquement à des problèmes. C'est le moment 
IDÉAL pour la prévention. Valorise cette opportunité dans ta réponse!
"""
    
    elif bp_high and risks.get('risk_hypertension', 0) > 0.6:
        return f"""
TYPE: Prédiction Confirmée (VALIDATION)
- Tension actuelle: ÉLEVÉE ({bp_sys}/{bp_dia})
- Risque hypertension IA: {int(risks.get('risk_hypertension', 0)*100)}%

INTERPRÉTATION: Le risque prédit s'est matérialisé. Cela valide la précision du 
modèle et suggère que les autres prédictions sont également fiables. Recommande une 
consultation médicale urgente.
"""
    
    elif bp_high and max_risk_value < 0.3:
        return f"""
TYPE: Spike Temporaire Probable
- Tension actuelle: ÉLEVÉE ({bp_sys}/{bp_dia})
- Risque IA global: FAIBLE ({int(max_risk_value*100)}%)

INTERPRÉTATION: Mesure élevée mais pattern global sain suggère un problème situationnel 
(stress, douleur, erreur de mesure) plutôt que chronique. Recommande re-vérification 
et monitoring avant de s'alarmer.
"""
    
    elif bp_normal and max_risk_value < 0.3:
        return f"""
TYPE: Santé Optimale
- Tension actuelle: NORMALE ({bp_sys}/{bp_dia})
- Risque IA global: FAIBLE ({int(max_risk_value*100)}%)

INTERPRÉTATION: Excellent état de santé présent et futur. Les habitudes actuelles 
sont protectrices. Encourage le maintien de ces bonnes pratiques.
"""
    
    else:
        return f"""
TYPE: Évaluation Standard
- Tension actuelle: {bp_sys}/{bp_dia} mmHg
- Risque IA le plus élevé: {int(max_risk_value*100)}%

INTERPRÉTATION: Analyse les données selon les guidelines standard.
"""
