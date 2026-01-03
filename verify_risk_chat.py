import sys
import os

# Add the current directory to sys.path so we can import services
sys.path.append(os.getcwd())

try:
    from services.chatbot_service import generate_chatbot_response
    print("✅ Import successful: services.chatbot_service")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test Data
user_data = {
    "userId": "TestUser",
    "age": 45,
    "weight": 95,
    "goal": "Perte de poids",
    "daily_steps": 2000, 
    "hours_of_sleep": 6
}

# Fake High Risk Data
fake_risks = {
    "risk_diabetes": 0.85, # Very High
    "risk_hypertension": 0.20,
    "risk_obesity": 0.70,
    "risk_heart_disease": 0.10
}

question = "Est-ce que je peux manger des gâteaux ?"

print(f"🤖 Testing Chatbot with question: '{question}' and HIGH DIABETES RISK...")
try:
    response = generate_chatbot_response(question, user_data, fake_risks)
    print("\n--- RESPONSE ---")
    print(response)
    print("----------------")
    
    if "diabète" in response.lower() or "sucre" in response.lower():
        print("✅ Test Passed: Chatbot mentioned diabetes/sugar risks.")
    else:
        print("⚠️ Test Warning: Chatbot did NOT mention diabetes risks clearly.")
        
except Exception as e:
    print(f"❌ Execution failed: {e}")
