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
    "age": 30,
    "weight": 80,
    "goal": "Perte de poids",
    "daily_steps": 3000, # Sedentary
    "hours_of_sleep": 5  # Low sleep
}

question = "Pourquoi je suis fatigué ?"

print(f"🤖 Testing Chatbot with question: '{question}'...")
try:
    response = generate_chatbot_response(question, user_data)
    print("\n--- RESPONSE ---")
    print(response)
    print("----------------")
    
    if "fatigué" in response.lower() or "sommeil" in response.lower():
        print("✅ Test Passed: Response seems relevant.")
    else:
        print("⚠️ Test Warning: Response might not be relevant.")
        
except Exception as e:
    print(f"❌ Execution failed: {e}")
