# 📘 HealthGuardian AI - Detailed Technical Deep Dive

## 1. 🛠️ Technologies & Stack
This project is **NOT** built with Flask. It is built with **FastAPI**, which is a modern, faster, and more robust framework for building APIs with Python.

### Core Stack:
*   **Language**: Python 3.10+
*   **Web Framework**: **FastAPI** (High performance, automatic validation, auto-documentation).
*   **Server**: **Uvicorn** (ASGI server to run the application).
*   **Data Validation**: **Pydantic** (Ensures the data sent to the API is correct).
*   **Machine Learning**: **Scikit-Learn** (For the Risk Prediction Model), **Pandas** (Data manipulation), **Joblib** (Model loading).
*   **Generative AI**: **Groq API** (Running **Llama 3**) for the Chatbot and Health Summary.

---

## 2. 🏗️ Software Architecture
The project follows a **Layered Architecture** (Controller-Service-Model pattern) to keep code clean and organized.

1.  **Presentation Layer (API)**: `api/routes.py`
    *   **Role**: Receives HTTP requests, validates data (using `schemas.py`), and calls the appropriate service. It does NOT contain business logic.
2.  **Service Layer (Business Logic)**: `services/`
    *   **Role**: Contains the "brain" of the application.
    *   *Examples*: `risk_predictor.py` (ML logic), `nutrition_service.py` (Diet logic), `chatbot_service.py` (AI logic).
3.  **Data/Model Layer**: `models/`
    *   **Role**: Stores the pre-trained Machine Learning models (`.joblib` files).

---

## 3. 🔍 Code Breakdown by Endpoint

### A. The Master Endpoint: `/api/generate-full-plan`
**File**: `api/routes.py`

This endpoint is the "Orchestrator". It calls multiple services in sequence.

```python
@router.post("/generate-full-plan")
async def generate_full_health_plan(data: UserHealthData):
```
*   **Concept**: `async def` allows the server to handle other requests while waiting for slow operations (like AI calls). `data: UserHealthData` tells FastAPI to validate the input JSON against the schema.

#### Step 1: ML Prediction
```python
risk_prediction = predict_health_risks(data)
```
*   **Logic**: Calls `services.risk_predictor`.
*   **Inside `risk_predictor.py`**:
    1.  Converts user data (Age, BMI, Sleep) into a format the model understands (One-Hot Encoding).
    2.  `model.predict_proba(input_df)`: Asks the ML model for the probability of Diabetes, Hypertension, etc.

#### Step 2: Nutrition & Exercise Generation
```python
nutrition_plan = await generate_nutrition_plan(nutri_req, risk_dict)
exercise_plan = await generate_exercise_plan(sport_req, risk_dict)
```
*   **Logic**:
    *   **Nutrition**: Uses the user's BMR (Basal Metabolic Rate) to calculate calories, then selects Tunisian meals (Couscous, etc.) that fit the calorie goal.
    *   **Exercise**: Uses `wger.de` API + Local Tunisian spots (Corniche, Belvédère) to create a schedule.

#### Step 3: AI Summary (RAG)
```python
ai_message = generate_grok_summary(user_data, risks, ...)
```
*   **Logic**: Sends all the calculated data (Risks + Plans) to Llama 3 (via Groq) to generate a friendly summary.

---

### B. The Chatbot Endpoint: `/api/chatbot`
**File**: `api/routes.py` & `services/chatbot_service.py`

This endpoint enables the "Context-Aware" conversation.

```python
@router.post("/chatbot")
async def chatbot(request: dict):
```

#### Step 1: Calculate Risks on the Fly
```python
if user_data_dict:
    user_health_data = UserHealthData(**user_data_dict)
    risk_response = predict_health_risks(user_health_data)
```
*   **Concept**: The chatbot needs to know the user's health *right now*. We re-run the ML model on the incoming user data to get fresh risk probabilities.

#### Step 2: Generate Response (RAG)
```python
answer = generate_chatbot_response(question, user_data_dict, risks)
```
*   **Inside `chatbot_service.py`**:
    *   **Context Injection**: We create a hidden "System Prompt" that includes the user's data and risks.
    *   *Example Prompt Sent to AI*:
        > "You are HealthGuardian. The user has 85% Diabetes Risk. User asks: 'Can I eat cake?'"
    *   **Result**: The AI answers "No, because of your diabetes risk..." without the user explicitly mentioning it.

---

### C. The ML Service: `services/risk_predictor.py`

This file handles the "Intelligence" part of the anomaly detection.

```python
model = joblib.load("models/health_risk_model.joblib")
```
*   **Concept**: Loads the pre-trained brain (Random Forest or XGBoost) into memory when the server starts.

```python
input_df = pd.DataFrame(0, index=[0], columns=model_features)
input_df['Age'] = data.age
input_df['BMI'] = bmi
```
*   **Concept (Preprocessing)**: The model expects a very specific table of numbers. We create an empty table and fill in the user's details.

```python
probas = model.predict_proba(input_df)
```
*   **Concept (Inference)**: The actual "prediction" happens here. It returns an array of probabilities (e.g., `[0.1, 0.85]`) for "No Disease" vs "Disease".
