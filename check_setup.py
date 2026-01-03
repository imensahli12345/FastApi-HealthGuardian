import sys
import os
import importlib

print("🔍 Starting Project Verification...")

# 1. Check for .env file
if os.path.exists(".env"):
    print("✅ .env file found.")
else:
    print("❌ .env file MISSING! Please create one with GROQ_API_KEY.")

# 2. Check Dependencies
dependencies = ["fastapi", "uvicorn", "pydantic", "groq", "joblib", "pandas", "sklearn"]
missing = []
for dep in dependencies:
    try:
        importlib.import_module(dep)
        print(f"✅ Dependency found: {dep}")
    except ImportError:
        print(f"❌ Dependency MISSING: {dep}")
        missing.append(dep)

if missing:
    print(f"⚠️ Missing packages: {', '.join(missing)}")
    print("Run: pip install " + " ".join(missing))

# 3. Check Internal Modules (Syntax & Imports)
modules_to_check = [
    "app",
    "api.routes",
    "api.schemas",
    "services.risk_predictor",
    "services.nutrition_service",
    "services.exercise_service",
    "services.llm_grok",
    "services.chatbot_service"
]

print("\n🔍 Checking Internal Modules...")
sys.path.append(os.getcwd())

for module in modules_to_check:
    try:
        importlib.import_module(module)
        print(f"✅ Module loaded successfully: {module}")
    except SyntaxError as e:
        print(f"❌ SyntaxError in {module}: {e}")
    except ImportError as e:
        print(f"❌ ImportError in {module}: {e}")
    except Exception as e:
        print(f"❌ Error loading {module}: {e}")

print("\n🏁 Verification Complete.")
