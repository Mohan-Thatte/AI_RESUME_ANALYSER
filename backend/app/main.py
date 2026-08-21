from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="ResumeMatch AI API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def home():
    return {
        "message": "ResumeMatch AI backend is running"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }