"""
Gemini LLM service for AI Interview Platform
Handles integration with Google GenAI API for answer evaluation and question generation
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Gemini API"""

    def __init__(self):
        """Initialize Gemini service (client created on first use)"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        logger.info(f"GEMINI_API_KEY exists: {bool(self.api_key)}")
        logger.info(f"GEMINI_MODEL: {self.model}")

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set. Using fallback evaluation/question generation.")

    def _get_client(self):
        """Get or create Gemini client (lazy initialization)"""
        if self.client is None and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Gemini client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.client = None
        return self.client

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON robustly from Gemini response text."""
        text = text.strip()
        logger.info(f"Raw Gemini response: {text}")

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        if "```json" in text:
            try:
                candidate = text.split("```json", 1)[1].split("```", 1)[0].strip()
                return json.loads(candidate)
            except Exception:
                pass

        if "```" in text:
            try:
                candidate = text.split("```", 1)[1].split("```", 1)[0].strip()
                return json.loads(candidate)
            except Exception:
                pass

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except Exception:
                pass

        raise ValueError("Could not parse JSON from Gemini response")

    def _default_evaluation(self) -> Dict[str, Any]:
        return {
            "correctness": 1,
            "completeness": 1,
            "technical_depth": 1,
            "clarity": 2,
            "total_score": 5,
            "feedback": "Answer recorded. Evaluation fallback was used.",
            "strengths": ["Response was submitted"],
            "weaknesses": ["Needs more technical detail"],
            "follow_up_needed": True,
        }

    def _default_question_payload(self, current_stage: str, interview_type: str) -> Dict[str, Any]:
        fallback_question_map = {
            "intro": "Can you briefly introduce yourself and explain your relevant background?",
            "resume_deep_dive": "Can you explain one of the key projects from your resume in more detail?",
            "project_details": "Can you walk me through the scope and goals of that project?",
            "role_contribution": "What was your specific role and contribution in that project?",
            "technical_deep_dive": "What technologies and tools did you use, and why did you choose them?",
            "technical_skills": "Which technical skills would you like to highlight from your experience?",
            "role_technical": "Can you describe how you would solve a technical problem relevant to this role?",
            "follow_up": "Can you elaborate on the technical decisions you mentioned earlier?",
            "wrap_up": "How do you think your skills and experience fit this opportunity?",
        }
        return {
            "question": fallback_question_map.get(current_stage, "Can you tell me more about your experience?"),
            "question_type": current_stage,
            "target_topic": interview_type,
            "reason": "Fallback question used because Gemini generation was unavailable.",
        }

    def evaluate_answer(
        self,
        question: str,
        answer: str,
        interview_type: str,
        context: Optional[str] = None,
        role: Optional[str] = None,
        current_stage: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Evaluate candidate answer using Gemini."""
        default_evaluation = self._default_evaluation()

        try:
            client = self._get_client()
            if not client:
                logger.warning("Gemini client unavailable; using default evaluation")
                return default_evaluation

            prompt = f"""
You are an expert technical interviewer.

Evaluate the candidate's answer for a technical interview.

Interview type: {interview_type}
Target role: {role or "Not provided"}
Current stage: {current_stage or "Not provided"}
Additional context: {context or "None"}

Question:
{question}

Candidate answer:
{answer}

Score the answer on:
- correctness (0-3)
- completeness (0-3)
- technical_depth (0-3)
- clarity (0-3)

Scoring meaning:
0 = very poor / missing
1 = weak
2 = acceptable
3 = strong

Return ONLY a valid JSON object with this exact structure:
{{
  "correctness": 0,
  "completeness": 0,
  "technical_depth": 0,
  "clarity": 0,
  "feedback": "1-2 sentence evaluation",
  "strengths": ["item1", "item2"],
  "weaknesses": ["item1", "item2"],
  "follow_up_needed": true
}}
""".strip()

            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=400,
                    response_mime_type="application/json",
                ),
            )

            evaluation = self._extract_json(response.text)
            evaluation = self._validate_evaluation(evaluation)
            evaluation["total_score"] = (
                evaluation["correctness"]
                + evaluation["completeness"]
                + evaluation["technical_depth"]
                + evaluation["clarity"]
            )

            logger.info(f"Gemini evaluation successful: {evaluation['total_score']}/12")
            return evaluation

        except Exception as e:
            logger.error(f"Error evaluating answer with Gemini: {e}")
            return default_evaluation

    def _validate_evaluation(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize evaluation object."""
        valid_metrics = {
            "correctness": 1,
            "completeness": 1,
            "technical_depth": 1,
            "clarity": 2,
        }

        for metric, default in valid_metrics.items():
            try:
                value = int(evaluation.get(metric, default))
                evaluation[metric] = max(0, min(3, value))
            except Exception:
                evaluation[metric] = default

        if not isinstance(evaluation.get("feedback"), str) or not evaluation.get("feedback"):
            evaluation["feedback"] = "Answer recorded. Evaluation completed with fallback normalization."

        for field in ["strengths", "weaknesses"]:
            value = evaluation.get(field, [])
            if not isinstance(value, list):
                value = []
            evaluation[field] = [str(item).strip() for item in value if str(item).strip()][:3]

        if not evaluation["strengths"]:
            evaluation["strengths"] = ["Response submitted"]
        if not evaluation["weaknesses"]:
            evaluation["weaknesses"] = ["Could include more detail"]

        evaluation["follow_up_needed"] = bool(evaluation.get("follow_up_needed", False))
        return evaluation

    def generate_question(
        self,
        interview_type: str,
        current_stage: str,
        context: Optional[str] = None,
        role: Optional[str] = None,
        resume_summary: Optional[str] = None,
        previous_question: Optional[str] = None,
        previous_answer: Optional[str] = None,
        topics_covered: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate the next question using Gemini."""
        fallback = self._default_question_payload(current_stage, interview_type)

        try:
            client = self._get_client()
            if not client:
                logger.warning("Gemini client unavailable; using fallback question")
                return fallback

            prompt = f"""
You are an expert technical interviewer generating the next interview question.

Interview type: {interview_type}
Current stage: {current_stage}
Target role: {role or "Not provided"}
Resume summary: {resume_summary or "Not provided"}
Additional context: {context or "None"}
Previous question: {previous_question or "None"}
Previous answer: {previous_answer or "None"}
Topics already covered: {", ".join(topics_covered or []) if topics_covered else "None"}

Generate ONE strong next interview question that:
- matches the current stage
- is relevant to the role or resume context
- avoids repeating previous topics
- sounds natural and professional
- is concise

Return ONLY a valid JSON object with this exact structure:
{{
  "question": "the next interview question",
  "question_type": "{current_stage}",
  "target_topic": "main topic being assessed",
  "reason": "why this question is appropriate now"
}}
""".strip()

            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.5,
                    max_output_tokens=250,
                    response_mime_type="application/json",
                ),
            )

            payload = self._extract_json(response.text)

            if not isinstance(payload.get("question"), str) or not payload["question"].strip():
                logger.warning("Gemini question payload invalid; using fallback")
                return fallback

            payload["question"] = payload["question"].strip()
            payload["question_type"] = str(payload.get("question_type") or current_stage)
            payload["target_topic"] = str(payload.get("target_topic") or interview_type)
            payload["reason"] = str(payload.get("reason") or "Generated by Gemini based on interview context.")

            logger.info(f"Gemini question generated successfully for stage {current_stage}")
            return payload

        except Exception as e:
            logger.error(f"Error generating question with Gemini: {e}")
            return fallback


_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service instance."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service