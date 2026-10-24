import os
import json
import logging
from typing import Optional, Dict, Any

from dotenv import load_dotenv

from app.core.config import get_settings

load_dotenv()
logger = logging.getLogger(__name__)

try:
    from google import genai
    GENAI_AVAILABLE = True
except Exception:
    genai = None
    GENAI_AVAILABLE = False


class GeminiEvaluationService:
    """Gemini service for rubric-based interview answer evaluation."""

    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY")
        try:
            settings = get_settings()
            self.model = settings.gemini_model
        except Exception:
            self.model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.client = None

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found. Gemini evaluation disabled.")
            return


        if not GENAI_AVAILABLE:
            logger.warning("google-genai package not installed. Gemini evaluation disabled.")
            return

        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Gemini evaluation client initialized successfully.")
        except Exception as exc:
            logger.error(f"Failed to initialize Gemini client: {exc}")
            self.client = None

    def is_available(self) -> bool:
        return self.client is not None

    def _extract_json_text(self, raw_text: str) -> Optional[str]:
        if not raw_text:
            return None

        text = raw_text.strip()

        if text.startswith("```"):
            text = text.strip("`").strip()
            if text.lower().startswith("json"):
                text = text[4:].strip()

        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None

        return text[start:end + 1]

    def _sanitize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        def clamp_score(value: Any) -> int:
            try:
                value = int(value)
            except Exception:
                value = 0
            return max(0, min(3, value))

        correctness = clamp_score(result.get("correctness", 0))
        completeness = clamp_score(result.get("completeness", 0))
        technical_depth = clamp_score(result.get("technical_depth", 0))
        clarity = clamp_score(result.get("clarity", 0))

        strengths = result.get("strengths", [])
        weaknesses = result.get("weaknesses", [])

        if not isinstance(strengths, list):
            strengths = [str(strengths)] if strengths else []
        if not isinstance(weaknesses, list):
            weaknesses = [str(weaknesses)] if weaknesses else []

        strengths = [str(item).strip() for item in strengths if str(item).strip()]
        weaknesses = [str(item).strip() for item in weaknesses if str(item).strip()]

        feedback = str(result.get("feedback", "")).strip()
        follow_up_needed = bool(result.get("follow_up_needed", False))

        total_score = correctness + completeness + technical_depth + clarity

        return {
            "correctness": correctness,
            "completeness": completeness,
            "technical_depth": technical_depth,
            "clarity": clarity,
            "total_score": total_score,
            "feedback": feedback,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "follow_up_needed": follow_up_needed,
        }

    def evaluate_answer(
        self,
        question: str,
        answer: str,
        interview_type: str,
        current_stage: Optional[str] = None,
        role: Optional[str] = None,
        resume_summary: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Evaluate one answer with Gemini. Returns None on any failure."""

        if not self.client:
            return None

        try:
            prompt = f"""
You are an expert technical interviewer.

Evaluate the candidate's answer using this rubric:
- correctness: 0 to 3
- completeness: 0 to 3
- technical_depth: 0 to 3
- clarity: 0 to 3

Context:
- interview_type: {interview_type}
- current_stage: {current_stage or "unknown"}
- role: {role or "N/A"}
- resume_summary: {(resume_summary or "N/A")[:400]}

Question:
{question}

Candidate Answer:
{answer}

Return ONLY valid JSON in this exact structure:
{{
  "correctness": 0,
  "completeness": 0,
  "technical_depth": 0,
  "clarity": 0,
  "feedback": "short overall feedback",
  "strengths": ["strength 1", "strength 2"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "follow_up_needed": false
}}

Scoring guidance:
- 0 = missing / incorrect / unusable
- 1 = weak / vague / minimal
- 2 = acceptable / partially detailed
- 3 = strong / accurate / well-explained

Rules:
- return JSON only
- do not use markdown
- do not add explanation before or after JSON
""".strip()

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )

            raw_text = getattr(response, "text", None)
            if not raw_text:
                logger.warning("Gemini returned empty response text.")
                return None

            json_text = self._extract_json_text(raw_text)
            if not json_text:
                logger.warning(f"Gemini did not return valid JSON. Raw text: {raw_text[:500]}")
                return None

            parsed = json.loads(json_text)
            sanitized = self._sanitize_result(parsed)

            logger.info(
                "Gemini evaluation succeeded. Score: %s/12",
                sanitized["total_score"],
            )
            return sanitized

        except Exception as exc:
            logger.error(f"Gemini evaluation error: {exc}")
            return None


_gemini_evaluation_service: Optional[GeminiEvaluationService] = None


def get_gemini_evaluation_service() -> GeminiEvaluationService:
    global _gemini_evaluation_service
    if _gemini_evaluation_service is None:
        _gemini_evaluation_service = GeminiEvaluationService()
    return _gemini_evaluation_service