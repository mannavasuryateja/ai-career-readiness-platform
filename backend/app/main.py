from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import interview, resume, auth
from app.core.database import connect_db, close_db
from app.core.config import get_settings
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate settings at boot
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="AI Career Platform",
    description="Unified Platform for AI Interviews and Resume Analysis",
    version="1.0.0"
)

# Configure CORS using environment-driven allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_urls,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(interview.router)
app.include_router(resume.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database and check API keys on startup"""
    # Connect to database
    await connect_db()
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not gemini_api_key:
        logger.warning("⚠️  GEMINI_API_KEY not configured. Answer evaluation will use fallback scoring.")
    else:
        logger.info("✓ Gemini API key configured for answer evaluation.")
    
    if not openrouter_api_key:
        logger.warning("⚠️  OPENROUTER_API_KEY not configured. Question generation will use fallback phrasing.")
    else:
        logger.info("✓ OpenRouter API key configured for question generation.")
    
    logger.info(f"✓ CORS configured for origins: {settings.frontend_urls}")
    logger.info(f"✓ Daily limits: {settings.analysis_daily_limit} analyses, {settings.interview_daily_limit} interviews")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await close_db()


@app.get("/health")
async def health_check():
    """Sanitized public health check endpoint without leaking internal credentials"""
    return {
        "status": "ok",
        "message": "AI Career Platform API is running",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

