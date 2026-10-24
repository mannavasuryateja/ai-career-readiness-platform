import os
import logging
from typing import Optional, Dict, Any, List
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class OpenRouterQuestionService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
        self.site_url = os.getenv("OPENROUTER_SITE_URL", "http://localhost:3000")
        self.site_name = os.getenv("OPENROUTER_SITE_NAME", "AI Interview Platform")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

        logger.info(f"OPENROUTER_API_KEY exists: {bool(self.api_key)}")
        logger.info(f"OPENROUTER_MODEL: {self.model}")

        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY not set. Using fallback question generation.")

    def _default_response(self, current_stage: str) -> Dict[str, Any]:
        fallback_map = {
            "intro": "Can you briefly introduce yourself and explain your background?",
            "project_details": "Can you walk me through one of your key projects and its main goals?",
            "role_contribution": "What was your specific role and contribution in that project?",
            "technical_deep_dive": "What technologies and tools did you use, and why did you choose them?",
            "technical_skills": "Which technical skills would you like to highlight from your experience?",
            "role_technical": "Can you describe how you would solve a technical problem relevant to this role?",
            "follow_up": "Can you elaborate on the technical decisions you mentioned earlier?",
            "wrap_up": "How do you think your skills and experience fit this opportunity?",
        }
        return {
            "question": fallback_map.get(current_stage, "Can you tell me more about your experience?"),
            "question_type": current_stage,
        }

    def _flatten_text_field(self, value: Any) -> str:
        if value is None:
            return ""

        if isinstance(value, str):
            return value.strip()

        if isinstance(value, list):
            parts = []
            for item in value:
                if isinstance(item, dict):
                    text = item.get("text")
                    if text:
                        parts.append(str(text).strip())
                elif isinstance(item, str):
                    parts.append(item.strip())
            return "\n".join([p for p in parts if p]).strip()

        if isinstance(value, dict):
            text = value.get("text")
            return str(text).strip() if text else ""

        return str(value).strip()

    def _clean_question(self, text: str) -> str:
        if not text:
            return ""

        cleaned = str(text).strip().replace('"', "").replace("'", "").strip()

        prefixes = [
            "Here is the question:",
            "Interview question:",
            "Question:",
        ]
        for prefix in prefixes:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):].strip()

        cleaned = " ".join(cleaned.split())
        return cleaned

    def _is_meta_line(self, line: str) -> bool:
        low = line.lower().strip()

        bad_starts = [
            "first,",
            "first ",
            "resume summary:",
            "interview type:",
            "current stage:",
            "target role:",
            "previous question:",
            "previous answer:",
            "topics already covered:",
            "additional context:",
            "rules:",
            "you are",
            "generate exactly",
            "the user is",
            "i need to",
            "let me",
            "here is",
            "here's",
            "analysis:",
            "reasoning:",
            "thinking:",
        ]

        return any(low.startswith(x) for x in bad_starts)

    def _extract_question_from_response(self, text: str) -> str:
        if not text:
            return ""

        cleaned = str(text).strip()
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]

        candidates = []
        for line in lines:
            line = self._clean_question(line)
            if not line:
                continue
            if self._is_meta_line(line):
                continue
            if len(line) < 12:
                continue
            candidates.append(line)

        # Prefer actual question lines
        for line in candidates:
            if line.endswith("?"):
                return line

        # If there is one decent line, turn it into a question only if it looks like interviewer text
        for line in candidates:
            low = line.lower()
            interviewer_starts = [
                "can you",
                "could you",
                "tell me",
                "walk me through",
                "what",
                "why",
                "how",
                "which",
                "describe",
                "explain",
            ]
            if any(low.startswith(x) for x in interviewer_starts):
                return line if line.endswith("?") else line + "?"

        return ""

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
        default_response = self._default_response(current_stage)

        if not self.api_key:
            logger.warning("No OPENROUTER_API_KEY found; using fallback question")
            return default_response

        try:
            context_items = [
                f"Interview type: {interview_type}",
                f"Current stage: {current_stage}",
            ]

            if role:
                context_items.append(f"Target role: {role}")
            if resume_summary:
                context_items.append(f"Resume summary: {resume_summary[:300]}")
            if previous_question:
                context_items.append(f"Previous question: {previous_question[:200]}")
            if previous_answer:
                context_items.append(f"Previous answer: {previous_answer[:200]}")
            if topics_covered:
                context_items.append(f"Topics already covered: {', '.join(topics_covered[-5:])}")
            if context:
                context_items.append(f"Additional context: {context[:400]}")

            prompt = f"""
Generate exactly one natural technical interview question for the candidate.

{chr(10).join(context_items)}

Strict rules:
- Return only the final interview question
- Do not repeat the prompt
- Do not mention resume summary, stage, or context labels
- Do not include reasoning
- Do not include analysis
- Do not include JSON
- Do not include bullet points
- Do not include any prefix like 'Question:'
- The output must be a single natural interviewer-style sentence ending with '?'
""".strip()

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": self.site_url,
                "X-Title": self.site_name,
            }

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Return exactly one natural interviewer question and nothing else."
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
                "max_tokens": 60,
            }

            logger.info(f"Calling OpenRouter model: {self.model} for stage: {current_stage}")

            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30,
            )

            logger.info(f"OpenRouter status code: {response.status_code}")
            logger.info(f"OpenRouter raw response: {response.text[:1000]}")

            response.raise_for_status()
            data = response.json()

            message = data["choices"][0].get("message", {})
            raw_text = self._flatten_text_field(message.get("content"))

            if not raw_text:
                raw_text = self._flatten_text_field(message.get("reasoning"))

            logger.info(f"Raw extracted text: {str(raw_text)[:500]}")

            question = self._extract_question_from_response(raw_text)

            logger.info(f"Final extracted question: {question}")

            if not question:
                logger.warning("OpenRouter returned invalid question; using fallback")
                return default_response

            return {
                "question": question,
                "question_type": current_stage,
            }

        except Exception as e:
            logger.error(f"OpenRouter question generation failed: {e}")
            return default_response


_openrouter_service: Optional[OpenRouterQuestionService] = None


def get_openrouter_question_service() -> OpenRouterQuestionService:
    global _openrouter_service
    if _openrouter_service is None:
        _openrouter_service = OpenRouterQuestionService()
    return _openrouter_service