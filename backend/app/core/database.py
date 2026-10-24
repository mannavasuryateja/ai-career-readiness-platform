from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB_NAME", "ai_career_platform")

# Global instances
client: Optional[AsyncIOMotorClient] = None
db = None


# ==================== CONNECT ====================

async def connect_db():
    """Connect to MongoDB"""
    global client, db

    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]

    # Create indexes for better query performance
    
    # Users collection
    users_collection = db["users"]
    await users_collection.create_index("email", unique=True)
    
    # Resumes collection
    resumes_collection = db["resumes"]
    await resumes_collection.create_index("user_id")
    await resumes_collection.create_index("uploaded_at")
    await resumes_collection.create_index([("user_id", 1), ("uploaded_at", -1)])
    
    # Job descriptions collection
    jd_collection = db["job_descriptions"]
    await jd_collection.create_index("user_id")
    await jd_collection.create_index("created_at")
    await jd_collection.create_index([("user_id", 1), ("created_at", -1)])
    
    # Analysis results collection
    analysis_collection = db["analysis_results"]
    await analysis_collection.create_index("user_id")
    await analysis_collection.create_index("resume_id")
    await analysis_collection.create_index("jd_id")
    await analysis_collection.create_index("analyzed_at")
    await analysis_collection.create_index([("user_id", 1), ("analyzed_at", -1)])
    await analysis_collection.create_index([("resume_id", 1), ("jd_id", 1)])
    
    # Interview sessions collection
    interview_collection = db["interview_sessions"]
    await interview_collection.create_index("session_id", unique=True)
    await interview_collection.create_index("user_id")
    await interview_collection.create_index("resume_id")
    await interview_collection.create_index("status")
    await interview_collection.create_index("created_at")
    await interview_collection.create_index([("user_id", 1), ("created_at", -1)])

    usage_collection = db["usage_quotas"]
    await usage_collection.create_index([("user_id", 1), ("date", 1)], unique=True)

    import logging
    logger = logging.getLogger(__name__)
    logger.info("Connected to MongoDB")
    logger.info("Database indexes created")


# ==================== CLOSE ====================

async def close_db():
    """Close MongoDB connection"""
    global client

    if client:
        client.close()
        import logging
        logger = logging.getLogger(__name__)
        logger.info("MongoDB connection closed")


# ==================== GET DB ====================

def get_db():
    """Get database instance safely"""
    if db is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return db