"""MongoDB storage service for resumes, job descriptions, and analysis results."""

from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.core.database import get_db
from app.models.schemas import (
    StoredResume,
    StoredJobDescription,
    StoredAnalysisResult,
    StoredInterviewSession,
)
from datetime import datetime


class StorageService:
    """Service for storing and retrieving data from MongoDB."""

    # ==================== RESUME OPERATIONS ====================

    @staticmethod
    async def store_resume(
        filename: str,
        original_filename: str,
        extracted_text: str,
        extracted_data: Dict[str, Any],
        skills: List[str] = None,
        categories: Dict[str, List[str]] = None,
        user_id: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> str:
        """Store a resume in MongoDB. Returns resume_id."""
        db = get_db()
        resume_doc = {
            "user_id": user_id,
            "filename": filename,
            "original_filename": original_filename,
            "file_path": file_path,
            "extracted_text": extracted_text,
            "extracted_data": extracted_data,
            "skills": skills or [],
            "categories": categories or {},
            "uploaded_at": datetime.utcnow(),
        }
        result = await db.resumes.insert_one(resume_doc)
        return str(result.inserted_id)

    @staticmethod
    async def get_resume(resume_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a resume by ID."""
        db = get_db()
        resume = await db.resumes.find_one({"_id": ObjectId(resume_id)})
        return resume

    @staticmethod
    async def list_resumes(user_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """List all resumes (optionally filtered by user_id)."""
        db = get_db()
        query = {"user_id": user_id} if user_id else {}
        resumes = await db.resumes.find(query).sort("uploaded_at", -1).limit(limit).to_list(limit)
        return resumes

    @staticmethod
    async def delete_resume(resume_id: str) -> bool:
        """Delete a resume by ID."""
        db = get_db()
        result = await db.resumes.delete_one({"_id": ObjectId(resume_id)})
        return result.deleted_count > 0

    @staticmethod
    async def update_resume(resume_id: str, update_data: Dict[str, Any]) -> bool:
        """Update resume data."""
        db = get_db()
        result = await db.resumes.update_one(
            {"_id": ObjectId(resume_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0

    # ==================== JOB DESCRIPTION OPERATIONS ====================

    @staticmethod
    async def store_jd(
        title: str,
        company: str,
        description_text: str,
        skills: List[str] = None,
        categories: Dict[str, List[str]] = None,
        user_id: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> str:
        """Store a job description in MongoDB. Returns jd_id."""
        db = get_db()
        jd_doc = {
            "user_id": user_id,
            "title": title,
            "company": company,
            "description_text": description_text,
            "file_path": file_path,
            "skills": skills or [],
            "categories": categories or {},
            "created_at": datetime.utcnow(),
        }
        result = await db.job_descriptions.insert_one(jd_doc)
        return str(result.inserted_id)

    @staticmethod
    async def get_jd(jd_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a job description by ID."""
        db = get_db()
        jd = await db.job_descriptions.find_one({"_id": ObjectId(jd_id)})
        return jd

    @staticmethod
    async def list_jds(user_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """List all job descriptions (optionally filtered by user_id)."""
        db = get_db()
        query = {"user_id": user_id} if user_id else {}
        jds = await db.job_descriptions.find(query).sort("created_at", -1).limit(limit).to_list(limit)
        return jds

    @staticmethod
    async def delete_jd(jd_id: str) -> bool:
        """Delete a job description by ID."""
        db = get_db()
        result = await db.job_descriptions.delete_one({"_id": ObjectId(jd_id)})
        return result.deleted_count > 0

    # ==================== ANALYSIS RESULT OPERATIONS ====================

    @staticmethod
    async def store_analysis_result(
        resume_filename: str,
        jd_title: str,
        resume_skills: List[str],
        jd_skills: List[str],
        matched_skills: List[str],
        missing_skills: List[str],
        critical_missing: List[str],
        moderate_missing: List[str],
        optional_missing: List[str],
        score_breakdown: Dict[str, float],
        final_readiness_score: float,
        learning_plan: List[Dict[str, Any]],
        explanation: str,
        score_simulation: List[Dict[str, Any]],
        user_id: Optional[str] = None,
        resume_id: Optional[str] = None,
        jd_id: Optional[str] = None,
    ) -> str:
        """Store analysis result in MongoDB. Returns analysis_id."""
        db = get_db()
        
        # Convert string IDs to ObjectId if provided
        resume_oid = ObjectId(resume_id) if resume_id else None
        jd_oid = ObjectId(jd_id) if jd_id else None
        
        analysis_doc = {
            "user_id": user_id,
            "resume_id": resume_oid,
            "jd_id": jd_oid,
            "resume_filename": resume_filename,
            "jd_title": jd_title,
            "resume_skills": resume_skills,
            "jd_skills": jd_skills,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "critical_missing": critical_missing,
            "moderate_missing": moderate_missing,
            "optional_missing": optional_missing,
            "score_breakdown": score_breakdown,
            "final_readiness_score": final_readiness_score,
            "learning_plan": learning_plan,
            "explanation": explanation,
            "score_simulation": score_simulation,
            "analyzed_at": datetime.utcnow(),
        }
        result = await db.analysis_results.insert_one(analysis_doc)
        return str(result.inserted_id)

    @staticmethod
    async def get_analysis_result(analysis_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an analysis result by ID."""
        db = get_db()
        analysis = await db.analysis_results.find_one({"_id": ObjectId(analysis_id)})
        return analysis

    @staticmethod
    async def list_analysis_results(
        user_id: Optional[str] = None,
        resume_id: Optional[str] = None,
        jd_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """List analysis results with optional filters."""
        db = get_db()
        query = {}
        
        if user_id:
            query["user_id"] = user_id
        if resume_id:
            query["resume_id"] = ObjectId(resume_id)
        if jd_id:
            query["jd_id"] = ObjectId(jd_id)
        
        results = await db.analysis_results.find(query).sort("analyzed_at", -1).limit(limit).to_list(limit)
        return results

    @staticmethod
    async def delete_analysis_result(analysis_id: str) -> bool:
        """Delete an analysis result by ID."""
        db = get_db()
        result = await db.analysis_results.delete_one({"_id": ObjectId(analysis_id)})
        return result.deleted_count > 0

    # ==================== INTERVIEW SESSION OPERATIONS ====================

    @staticmethod
    async def store_interview_session(
        session_id: str,
        interview_type: str,
        user_id: Optional[str] = None,
        role: Optional[str] = None,
        resume_id: Optional[str] = None,
        mode: str = "text",
        resume_filename: Optional[str] = None,
        resume_summary: str = "NA",
        extracted_text: str = "",
        current_question: str = "",
        current_stage: str = "intro",
        max_questions: int = 6,
        session_doc_extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a new interview session in MongoDB with full initial state. Returns mongo_id."""
        db = get_db()
        
        resume_oid = ObjectId(resume_id) if resume_id else None
        
        session_doc = {
            "user_id": user_id,
            "session_id": session_id,
            "interview_type": interview_type,
            "role": role,
            "resume_id": resume_oid,
            "mode": mode,
            "resume_filename": resume_filename,
            "resume_summary": resume_summary or "NA",
            "extracted_text": extracted_text or "",
            "current_question": current_question or "",
            "current_stage": current_stage or "intro",
            "questions_asked": 0,
            "max_questions": max_questions,
            "transcript": [],
            "topics_covered": [],
            "last_answer": "",
            "last_question_type": "",
            "status": "in_progress",
            "is_finished": False,
            "final_report": None,
            "created_at": datetime.utcnow(),
            "completed_at": None,
        }
        if session_doc_extra:
            session_doc.update({k: v for k, v in session_doc_extra.items() if k not in ("_id",)})

        result = await db.interview_sessions.insert_one(session_doc)
        return str(result.inserted_id)

    @staticmethod
    async def get_interview_session(session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an interview session by session_id."""
        db = get_db()
        session = await db.interview_sessions.find_one({"session_id": session_id})
        return session

    @staticmethod
    async def update_interview_session(session_id: str, update_data: Dict[str, Any]) -> bool:
        """Update interview session data."""
        db = get_db()
        result = await db.interview_sessions.update_one(
            {"session_id": session_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    @staticmethod
    async def list_interview_sessions(
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """List interview sessions with optional filters."""
        db = get_db()
        query = {}
        
        if user_id:
            query["user_id"] = user_id
        if status:
            query["status"] = status
        
        sessions = await db.interview_sessions.find(query).sort("created_at", -1).limit(limit).to_list(limit)
        return sessions

    @staticmethod
    async def delete_interview_session(session_id: str) -> bool:
        """Delete an interview session by session_id."""
        db = get_db()
        result = await db.interview_sessions.delete_one({"session_id": session_id})
        return result.deleted_count > 0

    @staticmethod
    async def mark_interview_completed(session_id: str, final_report: Optional[Dict[str, Any]] = None) -> bool:
        """Mark an interview session as completed."""
        db = get_db()
        update_data = {
            "status": "completed",
            "is_finished": True,
            "completed_at": datetime.utcnow(),
        }
        if final_report:
            update_data["final_report"] = final_report
        
        result = await db.interview_sessions.update_one(
            {"session_id": session_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
