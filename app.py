from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api.routes import router

# Create FastAPI app
app = FastAPI(
    title="HealthGuardian AI",
    description="AI-powered nutrition and exercise recommendation system",
    version="1.0.0"
)

# Configure CORS (allow Spring Boot backend to call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Spring Boot default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["api"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "HealthGuardian AI",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/api/predict-risks",
            "/api/nutrition/recommend",
            "/api/exercise/recommend",
            "/api/chatbot"
        ]
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "HealthGuardian AI"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)