from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, status
from typing import Optional

from app.models.schemas import (
    StartRoleRequest,
    AnswerRequest,
    EndInterviewRequest,
    SessionResponse,
    InterviewReport,
)
from app.core.deps import get_current_user
from app.core.quota import consume_daily_quota, KIND_INTERVIEW
from app.core.uploads import read_allowed_upload, extract_text_from_bytes
from app.services.interview.interview_manager import get_interview_manager
from app.services.interview.resume_parser import ResumeParser
from app.services.storage_service import StorageService

router = APIRouter(prefix="/interview", tags=["interview"])

resume_parser = ResumeParser()
interview_manager = get_interview_manager(resume_parser=resume_parser)


async def _get_or_hydrate_session(session_id: str, user_id: str) -> dict:
    """Retrieve session from in-memory cache or hydrate from MongoDB."""
    session = interview_manager.get_session(session_id)
    if not session:
        db_session = await StorageService.get_interview_session(session_id)
        if not db_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found",
            )
        session = interview_manager.load_session(db_session)

    # Ownership check
    session_user_id = str(session.get("user_id", ""))
    if session_user_id and session_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this session",
        )

    return session


@router.post("/start/role", response_model=SessionResponse)
async def start_role_interview(
    request: StartRoleRequest,
    current_user: dict = Depends(get_current_user),
):
    """Start a role-based interview session with quota enforcement and Mongo persistence."""
    user_id = str(current_user["_id"])
    await consume_daily_quota(user_id, KIND_INTERVIEW)

    try:
        session = interview_manager.start_role_interview(
            role=request.role,
            mode=request.mode,
            max_questions=request.max_questions,
        )
        session["user_id"] = user_id

        # Store interview session in MongoDB with full initial state
        mongo_id = await StorageService.store_interview_session(
            session_id=session["session_id"],
            interview_type="role",
            user_id=user_id,
            role=request.role,
            mode=request.mode,
            current_question=session.get("current_question", ""),
            current_stage=session.get("current_stage", "intro"),
            max_questions=request.max_questions,
            session_doc_extra=session,
        )
        session["mongo_id"] = mongo_id
        return SessionResponse(session=session)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error starting role interview: {str(e)}",
        )


@router.post("/start/resume", response_model=SessionResponse)
async def start_resume_interview(
    resume_file: UploadFile = File(...),
    resume_summary: str = Form(""),
    mode: str = Form("text"),
    max_questions: int = Form(6),
    current_user: dict = Depends(get_current_user),
):
    """Start a resume-based interview session parsed in-memory with MongoDB persistence."""
    user_id = str(current_user["_id"])
    await consume_daily_quota(user_id, KIND_INTERVIEW)

    try:
        # Read file in memory (no disk writes)
        file_bytes, filename, ext = await read_allowed_upload(resume_file)
        extracted_text = extract_text_from_bytes(file_bytes, ext)

        summary = (
            resume_summary.strip()
            if resume_summary and resume_summary.strip()
            else ResumeParser.generate_summary(extracted_text)
        )

        session = interview_manager.start_resume_interview_from_text(
            extracted_text=extracted_text,
            filename=filename,
            resume_summary=summary,
            mode=mode,
            max_questions=max_questions,
        )
        session["user_id"] = user_id

        # Store interview session in MongoDB with full initial state
        mongo_id = await StorageService.store_interview_session(
            session_id=session["session_id"],
            interview_type="resume",
            user_id=user_id,
            resume_filename=filename,
            resume_summary=summary,
            extracted_text=extracted_text,
            current_question=session.get("current_question", ""),
            current_stage=session.get("current_stage", "intro"),
            mode=mode,
            max_questions=max_questions,
            session_doc_extra=session,
        )
        session["mongo_id"] = mongo_id
        return SessionResponse(session=session)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error starting resume interview: {str(e)}",
        )


@router.post("/answer", response_model=SessionResponse)
async def submit_answer(
    request: AnswerRequest,
    current_user: dict = Depends(get_current_user),
):
    """Submit an answer to the current interview question."""
    user_id = str(current_user["_id"])
    await _get_or_hydrate_session(request.session_id, user_id)

    try:
        session = interview_manager.submit_answer(
            session_id=request.session_id,
            answer=request.answer,
        )

        # Update session in MongoDB
        update_payload = {
            "questions_asked": session.get("questions_asked", 0),
            "transcript": session.get("transcript", []),
            "topics_covered": session.get("topics_covered", []),
            "last_answer": session.get("last_answer", ""),
            "last_question_type": session.get("last_question_type", ""),
            "current_question": session.get("current_question", ""),
            "current_stage": session.get("current_stage", ""),
            "is_finished": session.get("is_finished", False),
            "status": session.get("status", "in_progress"),
        }
        if session.get("final_report"):
            update_payload["final_report"] = session["final_report"]

        await StorageService.update_interview_session(
            session_id=request.session_id,
            update_data=update_payload,
        )

        return SessionResponse(session=session)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/end", response_model=SessionResponse)
async def end_interview(
    request: EndInterviewRequest,
    current_user: dict = Depends(get_current_user),
):
    """End an active interview session and generate final report."""
    user_id = str(current_user["_id"])
    session = await _get_or_hydrate_session(request.session_id, user_id)

    if not session.get("is_finished"):
        session["current_question"] = "Interview ended. Thank you for your time!"
        session["current_stage"] = "wrap_up"
        session["status"] = "completed"
        session["is_finished"] = True

        if not session.get("final_report"):
            session["final_report"] = interview_manager._build_final_report(session)

        interview_manager.session_store.update_session(request.session_id, session)

        await StorageService.mark_interview_completed(
            session_id=request.session_id,
            final_report=session.get("final_report"),
        )

    updated_session = interview_manager.get_session(request.session_id) or session
    return SessionResponse(session=updated_session)


@router.get("/report/{session_id}", response_model=InterviewReport)
async def get_interview_report(
    session_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get final evaluation report for an interview session."""
    user_id = str(current_user["_id"])
    session = await _get_or_hydrate_session(session_id, user_id)

    report = session.get("final_report")
    if not report:
        report = interview_manager._build_final_report(session)
        session["final_report"] = report
        interview_manager.session_store.update_session(session_id, {"final_report": report})
        await StorageService.update_interview_session(session_id, {"final_report": report})

    report["questions_asked"] = session.get("questions_asked", 0)
    return InterviewReport(**report)


# ==================== DATA RETRIEVAL ENDPOINTS ====================

@router.get("/sessions")
async def get_user_sessions(
    status: Optional[str] = None,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
):
    """Get all interview sessions for the authenticated user."""
    try:
        user_id = str(current_user["_id"])
        sessions = await StorageService.list_interview_sessions(
            user_id=user_id,
            status=status,
            limit=limit,
        )
        for s in sessions:
            s["_id"] = str(s["_id"])
            if s.get("resume_id"):
                s["resume_id"] = str(s["resume_id"])
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving sessions: {str(e)}",
        )


@router.get("/sessions/{session_id}/mongodb")
async def get_session_from_mongodb(
    session_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a specific interview session by session_id."""
    user_id = str(current_user["_id"])
    session = await _get_or_hydrate_session(session_id, user_id)
    session_copy = dict(session)
    if "_id" in session_copy:
        session_copy["_id"] = str(session_copy["_id"])
    return session_copy


@router.delete("/sessions/{session_id}")
async def delete_interview_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete an interview session by session_id."""
    user_id = str(current_user["_id"])
    await _get_or_hydrate_session(session_id, user_id)
    try:
        success = await StorageService.delete_interview_session(session_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        interview_manager.session_store.delete_session(session_id)
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting session: {str(e)}",
        )
