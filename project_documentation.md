# HealthGuardian AI - Technical Documentation

## 1. Project Overview
**HealthGuardian AI** is a FastAPI-based application that provides personalized health, nutrition, and exercise recommendations. It combines **Machine Learning (ML)** for risk prediction with **Generative AI (LLM)** for personalized coaching.

### 🏗️ Architecture Flow
1.  **Frontend/User** sends data to **API Endpoints** (`api/routes.py`).
2.  **API Layer** orchestrates the request by calling various **Services** (`services/`).
3.  **Services** perform specific tasks:
    *   `risk_predictor.py`: Runs ML inference.
    *   `nutrition_service.py`: Generates diet plans.
    *   `exercise_service.py`: Generates workout schedules.
    *   `chatbot_service.py`: Handles AI conversations.
4.  **Services** may call **External APIs** or load **Local Models**.

---

## 2. Code Structure & Links

### 📂 `api/routes.py` (The Controller)
This is the entry point. It links everything together.
*   **Link to ML**: Calls `predict_health_risks(data)` to get disease probabilities.
*   **Link to Nutrition**: Calls `generate_nutrition_plan(req)` using the user's stats.
*   **Link to Exercise**: Calls `generate_exercise_plan(req)` using the user's stats.
*   **Link to LLM**: Calls `generate_grok_summary(...)` to summarize everything.
*   **Link to Chatbot**: Calls `generate_chatbot_response(...)` for Q&A.

### 📂 `services/` (The Logic)
*   **`risk_predictor.py`**: Loads the `.joblib` model and predicts health risks.
*   **`llm_grok.py`**: Connects to **Groq API** (Llama 3) to generate human-like summaries.
*   **`chatbot_service.py`**: Manages the chat context and injects risk data into the prompt.

---

## 3. External APIs & Data Sources

### 🍎 Nutrition (`nutrition_service.py`)
*   **Goal**: Provide culturally relevant meal plans.
*   **Implementation**:
    *   While the architecture supports external APIs (like OpenFoodFacts), the current implementation uses a **Curated Tunisian Dataset** (Hardcoded in `get_tunisian_meal_suggestions`).
    *   **Why?** To ensure recommendations are strictly Tunisian (Couscous, Chorba, etc.) and calorie-accurate, which generic APIs often fail to do for specific local dishes.

### 🏋️ Exercise (`exercise_service.py`)
*   **Goal**: Provide workout plans based on equipment.
*   **Implementation**:
    *   **External API**: Uses `wger.de` (via `utils.data_fetcher`) to fetch standard exercises (Squats, Pushups).
    *   **Local Data**: Enriches this with **Tunisian Locations** (e.g., "Jogging at Parc Belvédère", "Swimming at Gammarth") to make it personalized.

### 🧠 LLM (`llm_grok.py` & `chatbot_service.py`)
*   **Provider**: **Groq API** (running Llama 3).
*   **Usage**: Used for generating the "Coach Message" and answering Chatbot questions.

---

## 4. ML Model Integration (`risk_predictor.py`)

This is the "Brain" of the anomaly detection system.

### 1. Loading the Model
```python
model = joblib.load("models/health_risk_model.joblib")
features = joblib.load("models/model_features.joblib")
```
The system loads a pre-trained **Scikit-Learn** model when the server starts.

### 2. Preprocessing
The user's raw data (JSON) is converted into a format the model understands:
*   **Numeric Conversion**: `23:30` (Bedtime) -> `23.5`.
*   **One-Hot Encoding**: `Job: "Bureau"` -> `metier_Bureau = 1`, `metier_Manuel = 0`.
*   **DataFrame Creation**: A single-row Pandas DataFrame is created with all 0s, then filled with the user's values.

### 3. Prediction
```python
probas = model.predict_proba(input_df)
```
The model returns the **probability** (0% to 100%) for each disease (Diabetes, Hypertension, Obesity, Heart Disease).

### 4. Chatbot Integration (RAG)
These probabilities are passed to the **Chatbot Service**.
*   **Context Injection**: The system tells the LLM: *"User has 85% risk of Diabetes"*.
*   **Result**: If the user asks "Can I eat sugar?", the Chatbot uses this injected knowledge to say "No, be careful because of your diabetes risk."
