import logging
import re
from typing import Optional, Dict, Any, List

from app.services.interview.evaluation_llm_service import get_gemini_evaluation_service

logger = logging.getLogger(__name__)


class EvaluatorService:
    """Evaluates interview answers using Gemini first, then heuristic fallback."""

    TECH_KEYWORDS = [
        "react", "react.js", "node", "node.js", "express", "express.js", "mongodb",
        "mongoose", "mysql", "sql", "jwt", "tailwind", "javascript", "python",
        "java", "c++", "html", "css", "bootstrap", "material ui", "rest api",
        "restful api", "axios", "git", "github", "vercel", "stripe", "authentication",
        "authorization", "database", "schema", "api", "backend", "frontend",
        "deployment", "performance", "scalability", "security", "token", "route",
        "middleware", "component", "state", "props", "server", "client"
    ]

    IMPLEMENTATION_TERMS = [
        "implemented", "built", "designed", "integrated", "optimized", "configured",
        "used", "developed", "handled", "managed", "created", "deployed", "validated",
        "secured", "connected", "stored", "fetched", "protected"
    ]

    EXPLANATION_TERMS = [
        "because", "so that", "in order to", "therefore", "which helped",
        "this allowed", "the reason", "for example", "for instance", "such as"
    ]

    def __init__(self) -> None:
        self.gemini_service = get_gemini_evaluation_service()

    def evaluate_answer_response(
        self,
        question: str,
        answer: str,
        interview_type: str,
        current_stage: Optional[str] = None,
        role: Optional[str] = None,
        resume_summary: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Main evaluation entry point."""

        llm_result = self.gemini_service.evaluate_answer(
            question=question,
            answer=answer,
            interview_type=interview_type,
            current_stage=current_stage,
            role=role,
            resume_summary=resume_summary,
        )

        if llm_result is not None:
            return self._finalize_result(llm_result)

        logger.info("Using heuristic fallback evaluation.")
        fallback_result = self._heuristic_evaluate(question, answer, current_stage, role)
        return self._finalize_result(fallback_result)

    def _finalize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
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

        total_score = correctness + completeness + technical_depth + clarity

        feedback = str(result.get("feedback", "")).strip()
        follow_up_needed = bool(result.get("follow_up_needed", False))

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

    def _heuristic_evaluate(
        self,
        question: str,
        answer: str,
        current_stage: Optional[str],
        role: Optional[str],
    ) -> Dict[str, Any]:
        answer = (answer or "").strip()
        question = (question or "").strip()

        if not answer:
            return {
                "correctness": 0,
                "completeness": 0,
                "technical_depth": 0,
                "clarity": 0,
                "feedback": "The answer was empty and did not address the question.",
                "strengths": [],
                "weaknesses": ["Did not provide an answer", "No technical detail", "Needs a complete response"],
                "follow_up_needed": True,
            }

        word_count = len(answer.split())
        sentence_count = max(1, len(re.findall(r"[.!?]+", answer)))
        lower_answer = answer.lower()
        lower_question = question.lower()

        tech_matches = self._count_keyword_matches(lower_answer, self.TECH_KEYWORDS)
        impl_matches = self._count_keyword_matches(lower_answer, self.IMPLEMENTATION_TERMS)
        explanation_matches = self._count_phrase_matches(lower_answer, self.EXPLANATION_TERMS)
        question_overlap = self._question_overlap_score(lower_question, lower_answer)

        correctness = 0
        completeness = 0
        technical_depth = 0
        clarity = 0

        strengths: List[str] = []
        weaknesses: List[str] = []

        # Correctness
        if word_count <= 1:
            correctness = 0
            weaknesses.append("Answer does not meaningfully address the question")
        elif question_overlap >= 3:
            correctness = 3
            strengths.append("Directly addresses the question")
        elif question_overlap >= 1:
            correctness = 2
            strengths.append("Partially addresses the question")
        else:
            correctness = 1
            weaknesses.append("Needs to connect more clearly to the question")

        # Completeness
        if word_count <= 3:
            completeness = 0
            weaknesses.append("Response is too short")
        elif word_count <= 10:
            completeness = 1
            weaknesses.append("Response needs more detail")
        elif word_count <= 30:
            completeness = 2
            strengths.append("Provides a reasonable amount of detail")
        else:
            completeness = 3
            strengths.append("Provides detailed explanation")

        # Technical depth
        depth_signal = tech_matches + impl_matches + explanation_matches
        if depth_signal <= 0:
            technical_depth = 0
            weaknesses.append("Lacks technical depth")
        elif depth_signal == 1:
            technical_depth = 1
            weaknesses.append("Needs more technical explanation")
        elif depth_signal <= 3:
            technical_depth = 2
            strengths.append("Includes some technical detail")
        else:
            technical_depth = 3
            strengths.append("Shows strong technical understanding")

        # Clarity
        if word_count <= 2:
            clarity = 0
            weaknesses.append("Answer is too brief to be clear")
        elif sentence_count >= 1 and word_count <= 12:
            clarity = 1
            weaknesses.append("Explanation could be clearer and more structured")
        elif sentence_count >= 1 and word_count <= 40:
            clarity = 2
            strengths.append("Answer is reasonably clear")
        else:
            clarity = 3
            strengths.append("Answer is clear and well-structured")

        # Stage-specific nudges
        stage = (current_stage or "").lower()
        role_lower = (role or "").lower()

        if stage in {"technical_deep_dive", "technical_skills", "role_technical"} and tech_matches == 0:
            technical_depth = max(0, technical_depth - 1)
            if "Needs more role-relevant technical detail" not in weaknesses:
                weaknesses.append("Needs more role-relevant technical detail")

        if "backend" in role_lower and not any(
            x in lower_answer for x in ["api", "database", "server", "authentication", "jwt", "express", "node"]
        ):
            correctness = max(0, correctness - 1)
            if "Could include more backend-specific details" not in weaknesses:
                weaknesses.append("Could include more backend-specific details")

        if "frontend" in role_lower and not any(
            x in lower_answer for x in ["react", "ui", "component", "state", "css", "frontend"]
        ):
            correctness = max(0, correctness - 1)
            if "Could include more frontend-specific details" not in weaknesses:
                weaknesses.append("Could include more frontend-specific details")

        correctness = max(0, min(3, correctness))
        completeness = max(0, min(3, completeness))
        technical_depth = max(0, min(3, technical_depth))
        clarity = max(0, min(3, clarity))

        total_score = correctness + completeness + technical_depth + clarity
        follow_up_needed = total_score <= 5 or word_count <= 8

        feedback = self._build_feedback(
            total_score=total_score,
            word_count=word_count,
            tech_matches=tech_matches,
            impl_matches=impl_matches,
            question_overlap=question_overlap,
        )

        strengths = self._dedupe_list(strengths)
        weaknesses = self._dedupe_list(weaknesses)

        if not strengths and total_score >= 6:
            strengths.append("Shows some relevant understanding")
        if not weaknesses and total_score < 8:
            weaknesses.append("Could provide more depth and specificity")

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

    def _count_keyword_matches(self, text: str, keywords: List[str]) -> int:
        count = 0
        seen = set()
        for keyword in keywords:
            pattern = re.escape(keyword.lower())
            if re.search(rf"\b{pattern}\b", text) and keyword.lower() not in seen:
                seen.add(keyword.lower())
                count += 1
        return count

    def _count_phrase_matches(self, text: str, phrases: List[str]) -> int:
        count = 0
        seen = set()
        for phrase in phrases:
            if phrase in text and phrase not in seen:
                seen.add(phrase)
                count += 1
        return count

    def _question_overlap_score(self, question: str, answer: str) -> int:
        stop_words = {
            "the", "is", "a", "an", "of", "to", "and", "in", "for", "your", "you",
            "me", "can", "could", "would", "how", "what", "why", "did", "do"
        }
        q_words = {
            w for w in re.findall(r"[a-zA-Z0-9+.#-]+", question.lower())
            if len(w) > 2 and w not in stop_words
        }
        a_words = set(re.findall(r"[a-zA-Z0-9+.#-]+", answer.lower()))
        return len(q_words.intersection(a_words))

    def _build_feedback(
        self,
        total_score: int,
        word_count: int,
        tech_matches: int,
        impl_matches: int,
        question_overlap: int,
    ) -> str:
        if total_score <= 2:
            return "The answer is too brief and does not adequately address the question."
        if total_score <= 5:
            return "The answer shows some relevance, but it needs more detail, clarity, and technical explanation."
        if total_score <= 8:
            return "The answer is reasonably good and relevant, but it could be improved with more specific implementation details."
        if tech_matches > 2 and impl_matches > 1 and question_overlap > 1:
            return "This is a strong answer with relevant technical detail, good structure, and clear alignment to the question."
        if word_count > 20:
            return "This is a solid answer with good detail, though it could be even stronger with deeper technical reasoning."
        return "This is a good answer overall with clear relevance and acceptable detail."

    def _dedupe_list(self, items: List[str]) -> List[str]:
        result = []
        seen = set()
        for item in items:
            normalized = item.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                result.append(item.strip())
        return result


_evaluator_service: Optional[EvaluatorService] = None


def get_evaluator_service() -> EvaluatorService:
    global _evaluator_service
    if _evaluator_service is None:
        _evaluator_service = EvaluatorService()
    return _evaluator_service