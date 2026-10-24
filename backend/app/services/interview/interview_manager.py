import uuid
import logging
import tempfile
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

from app.services.interview.question_generator import QuestionGenerator
from app.services.interview.evaluator import get_evaluator_service

logger = logging.getLogger(__name__)


class InMemorySessionStore:
    """Simple in-memory session store for interview sessions."""

    def __init__(self) -> None:
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        self.sessions[session_data["session_id"]] = session_data
        return session_data

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.sessions.get(session_id)

    def update_session(self, session_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        session = self.sessions.get(session_id)
        if not session:
            return None
        session.update(updates)
        self.sessions[session_id] = session
        return session

    def delete_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False


class InterviewManager:
    """Controls interview lifecycle, questioning, evaluation, and reporting."""

    def __init__(self, resume_parser=None) -> None:
        self.session_store = InMemorySessionStore()
        self.resume_parser = resume_parser
        self.evaluator = get_evaluator_service()
        self.default_max_questions = 6

    def _now_iso(self) -> str:
        return datetime.utcnow().isoformat()

    def _build_resume_summary(self, extracted_text: Optional[str]) -> str:
        if not extracted_text:
            return "NA"

        if self.resume_parser and hasattr(self.resume_parser, "generate_summary"):
            try:
                return self.resume_parser.generate_summary(extracted_text)
            except Exception as exc:
                logger.warning("Resume summary generation failed, using fallback: %s", exc)

        cleaned = " ".join(extracted_text.split())
        if len(cleaned) <= 250:
            return cleaned

        return cleaned[:250].rsplit(" ", 1)[0] + "..."

    def _stage_topic(self, stage_name: str) -> str:
        return QuestionGenerator.get_topic_from_stage(stage_name)

    def _append_unique_topics(self, topics: List[str], new_items: List[str]) -> List[str]:
        existing = {item.lower() for item in topics}
        for item in new_items:
            cleaned = str(item).strip()
            if cleaned and cleaned.lower() not in existing:
                topics.append(cleaned)
                existing.add(cleaned.lower())
        return topics

    def _extract_resume_text_from_upload(self, resume_file, filename: Optional[str]) -> str:
        if resume_file is None:
            return ""

        try:
            from app.core.uploads import file_extension
            from app.services.resume.parser import extract_text_from_bytes
            
            ext = file_extension(filename)
            file_bytes = resume_file.file.read()
            if hasattr(resume_file.file, "seek"):
                resume_file.file.seek(0)
            return extract_text_from_bytes(file_bytes, ext) or ""
        except Exception as exc:
            logger.error("Resume in-memory parsing failed: %s", exc)
            return ""

    def _build_initial_session(
        self,
        interview_type: str,
        mode: str,
        role: Optional[str] = None,
        resume_filename: Optional[str] = None,
        extracted_text: Optional[str] = None,
        resume_summary: Optional[str] = None,
        max_questions: Optional[int] = None,
    ) -> Dict[str, Any]:
        question, stage_name, question_type = QuestionGenerator.get_intro_question(
            interview_type=interview_type,
            role=role,
            extracted_text=extracted_text,
            resume_summary=resume_summary,
        )

        session = {
            "session_id": str(uuid.uuid4()),
            "interview_type": interview_type,
            "role": role,
            "mode": mode,
            "resume_filename": resume_filename,
            "resume_summary": resume_summary or "NA",
            "extracted_text": extracted_text or "",
            "current_question": question,
            "current_stage": stage_name,
            "questions_asked": 0,
            "max_questions": max_questions or self.default_max_questions,
            "transcript": [],
            "topics_covered": [],
            "last_answer": "",
            "last_question_type": question_type,
            "status": "in_progress",
            "is_finished": False,
            "created_at": self._now_iso(),
        }
        return session

    def start_role_interview(
        self,
        role: str,
        mode: str = "text",
        max_questions: Optional[int] = None,
    ) -> Dict[str, Any]:
        session = self._build_initial_session(
            interview_type="role",
            mode=mode,
            role=role,
            resume_filename=None,
            extracted_text="",
            resume_summary="NA",
            max_questions=max_questions,
        )
        self.session_store.create_session(session)
        logger.info("Started role interview session: %s", session["session_id"])
        return session

    def start_resume_interview(
        self,
        resume_file=None,
        filename: Optional[str] = None,
        mode: str = "text",
        max_questions: Optional[int] = None,
    ) -> Dict[str, Any]:
        extracted_text = ""
        resume_filename = filename

        if resume_file is not None:
            try:
                extracted_text = self._extract_resume_text_from_upload(resume_file, filename)
            except Exception as exc:
                logger.error("Resume parsing failed: %s", exc)
                extracted_text = ""

        resume_summary = self._build_resume_summary(extracted_text)

        session = self._build_initial_session(
            interview_type="resume",
            mode=mode,
            role=None,
            resume_filename=resume_filename,
            extracted_text=extracted_text,
            resume_summary=resume_summary,
            max_questions=max_questions,
        )
        self.session_store.create_session(session)
        logger.info("Started resume interview session: %s", session["session_id"])
        return session

    def start_resume_interview_from_text(
        self,
        extracted_text: str,
        filename: Optional[str] = None,
        resume_summary: Optional[str] = None,
        mode: str = "text",
        max_questions: Optional[int] = None,
    ) -> Dict[str, Any]:
        summary = resume_summary or self._build_resume_summary(extracted_text)
        session = self._build_initial_session(
            interview_type="resume",
            mode=mode,
            role=None,
            resume_filename=filename,
            extracted_text=extracted_text,
            resume_summary=summary,
            max_questions=max_questions,
        )
        self.session_store.create_session(session)
        logger.info("Started resume interview session from text: %s", session["session_id"])
        return session

    def load_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Load session data into in-memory store (e.g. hydrated from MongoDB)."""
        session_id = session_data.get("session_id")
        if session_id:
            self.session_store.sessions[session_id] = session_data
        return session_data

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.session_store.get_session(session_id)

    def submit_answer(self, session_id: str, answer: str) -> Dict[str, Any]:
        session = self.session_store.get_session(session_id)
        if not session:
            raise ValueError("Session not found")


        if session.get("is_finished"):
            return session

        current_question = session.get("current_question", "")
        current_stage = session.get("current_stage", "")
        interview_type = session.get("interview_type", "resume")
        role = session.get("role")
        resume_summary = session.get("resume_summary", "NA")

        evaluation = self.evaluator.evaluate_answer_response(
            question=current_question,
            answer=answer,
            interview_type=interview_type,
            current_stage=current_stage,
            role=role,
            resume_summary=resume_summary,
        )

        transcript_item = {
            "question": current_question,
            "answer": answer,
            "evaluation": evaluation,
        }

        transcript = list(session.get("transcript", []))
        transcript.append(transcript_item)

        topics_covered = list(session.get("topics_covered", []))
        stage_topic = self._stage_topic(current_stage)
        answer_topic = QuestionGenerator.extract_topic_from_answer(answer)
        topics_covered = self._append_unique_topics(
            topics_covered,
            [stage_topic] + ([answer_topic] if answer_topic else []),
        )

        questions_asked = int(session.get("questions_asked", 0)) + 1
        max_questions = int(session.get("max_questions", self.default_max_questions))

        updates: Dict[str, Any] = {
            "transcript": transcript,
            "topics_covered": topics_covered,
            "last_answer": answer,
            "questions_asked": questions_asked,
            "last_question_type": current_stage,
        }

        if questions_asked >= max_questions:
            report = self._build_final_report(session={**session, **updates})
            updates.update(
                {
                    "current_question": "Interview completed. Thank you for your time!",
                    "current_stage": "wrap_up",
                    "status": "completed",
                    "is_finished": True,
                    "final_report": report,
                }
            )
            updated_session = self.session_store.update_session(session_id, updates)
            logger.info("Interview completed. Session: %s", session_id)
            return updated_session

        next_question, next_stage, next_question_type = QuestionGenerator.get_next_question(
            interview_type=interview_type,
            questions_asked=questions_asked,
            role=role,
            extracted_text=session.get("extracted_text", ""),
            resume_summary=resume_summary,
            previous_question=current_question,
            previous_answer=answer,
            topics_covered=topics_covered,
        )

        updates.update(
            {
                "current_question": next_question,
                "current_stage": next_stage,
                "last_question_type": next_question_type,
                "status": "in_progress",
                "is_finished": False,
            }
        )

        updated_session = self.session_store.update_session(session_id, updates)
        logger.info(
            "Generated next question. Interview progress: %s/%s",
            questions_asked,
            max_questions,
        )
        return updated_session

    def _build_final_report(self, session: Dict[str, Any]) -> Dict[str, Any]:
        transcript = session.get("transcript", [])

        total_score = 0
        count = 0
        strengths: List[str] = []
        weaknesses: List[str] = []

        for item in transcript:
            evaluation = item.get("evaluation", {}) or {}
            total_score += int(evaluation.get("total_score", 0))
            count += 1

            for strength in evaluation.get("strengths", []) or []:
                if strength not in strengths:
                    strengths.append(strength)

            for weakness in evaluation.get("weaknesses", []) or []:
                if weakness not in weaknesses:
                    weaknesses.append(weakness)

        average_score = round(total_score / count, 2) if count else 0.0

        recommendations: List[str] = []
        weak_text = " ".join(weaknesses).lower()

        if "detail" in weak_text or "short" in weak_text or "brief" in weak_text:
            recommendations.append("Provide more detailed and structured answers.")
        if "technical" in weak_text:
            recommendations.append("Include more technical depth and implementation details.")
        if "clarity" in weak_text or "clear" in weak_text:
            recommendations.append("Organize your answers more clearly using concrete examples.")
        if "backend" in weak_text:
            recommendations.append("Strengthen backend-specific explanations with APIs, databases, and security examples.")
        if "frontend" in weak_text:
            recommendations.append("Strengthen frontend-specific explanations with UI, state, and performance examples.")

        if not recommendations:
            recommendations.append("Continue practicing concise, structured, and example-driven interview responses.")

        if average_score >= 9:
            readiness_label = "Highly Ready"
        elif average_score >= 6:
            readiness_label = "Moderately Ready"
        else:
            readiness_label = "Needs Improvement"

        return {
            "total_score": total_score,
            "average_score": average_score,
            "strengths": strengths[:10],
            "weaknesses": weaknesses[:10],
            "recommendations": recommendations[:5],
            "readiness_label": readiness_label,
            "questions_asked": count,
        }


_interview_manager: Optional[InterviewManager] = None


def get_interview_manager(resume_parser=None) -> InterviewManager:
    global _interview_manager
    if _interview_manager is None:
        _interview_manager = InterviewManager(resume_parser=resume_parser)
    elif resume_parser is not None and _interview_manager.resume_parser is None:
        _interview_manager.resume_parser = resume_parser
    return _interview_manager