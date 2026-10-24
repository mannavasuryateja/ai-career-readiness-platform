import os
import json
import re
import logging
from typing import List, Dict, Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_model_instance = None


def _get_gemini_model():
    global _model_instance
    if _model_instance is not None:
        return _model_instance

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        settings = get_settings()
        _model_instance = genai.GenerativeModel(settings.gemini_model)
        return _model_instance
    except Exception as e:
        logger.error(f"Failed to initialize Gemini model: {e}")
        return None


def _fallback_learning_plan(skill: str) -> Dict[str, Any]:
    return {
        "skill": skill,
        "recommendation": f"Focus on core principles and build hands-on projects with {skill} to bridge this gap.",
        "roadmap_steps": [
            f"Understand fundamentals and architecture of {skill}",
            f"Build a practical demo project using {skill}",
            f"Study best practices and standard interview patterns for {skill}",
            f"Integrate {skill} into your existing portfolio"
        ],
        "estimated_time": "1 - 2 weeks",
        "career_impact": "High"
    }


def generate_learning_plan_batch(skills: List[str]) -> List[Dict[str, Any]]:
    if not skills:
        return []

    # Limit to top 8 skills to preserve token quota
    skills_to_process = skills[:8]
    model = _get_gemini_model()

    if not model:
        logger.info("Gemini API key not configured or model unavailable; generating fallback learning plans.")
        return [_fallback_learning_plan(skill) for skill in skills_to_process]

    skill_list = "\n".join([f"- {skill}" for skill in skills_to_process])

    prompt = f"""
Generate structured learning plans for the following missing skills:

{skill_list}

Return strictly valid JSON as an array with this exact structure:
[
  {{
    "skill": "Skill Name",
    "recommendation": "Short 2 sentence career advice",
    "roadmap_steps": ["Step 1", "Step 2", "Step 3", "Step 4"],
    "estimated_time": "1-2 weeks",
    "career_impact": "High"
  }}
]

Do not add explanations or Markdown wrapping outside JSON.
"""

    try:
        response = model.generate_content(prompt)
        text = getattr(response, "text", "") or ""
        text = re.sub(r"```json|```", "", text).strip()

        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]
            plans = json.loads(text)
            if isinstance(plans, list) and len(plans) > 0:
                return plans
    except Exception as e:
        logger.warning(f"Gemini learning plan generation failed ({e}); using fallback.")

    return [_fallback_learning_plan(skill) for skill in skills_to_process]


def generate_cover_letter(
    candidate_name: str,
    target_role: str,
    company_name: str,
    matched_skills: List[str],
    resume_text: str,
    jd_text: str,
) -> Dict[str, Any]:
    """
    Generate a concise, professional 3-paragraph cover letter bridging resume highlights to the JD.
    """
    role = target_role or "Software Engineer"
    company = company_name or "Hiring Team"
    name = candidate_name or "Candidate"
    skills_highlight = ", ".join(matched_skills[:6]) if matched_skills else "relevant industry skills"

    model = _get_gemini_model()

    if model:
        prompt = f"""
You are an expert career coach. Write a tailored, impactful, 3-paragraph cover letter for:
Candidate: {name}
Target Role: {role}
Company: {company}
Key Matched Skills: {skills_highlight}

Resume Summary:
{(resume_text or '')[:1200]}

Job Description Summary:
{(jd_text or '')[:1200]}

Instructions:
- Paragraph 1: Enthusiastic introduction mentioning the {role} position at {company} and core strengths.
- Paragraph 2: Specific evidence of hands-on impact, project accomplishments, and alignment with the {skills_highlight}.
- Paragraph 3: Forward-looking closing reiterating excitement and requesting a discussion.
- Tone: Confident, professional, modern, no clichés.
- Return ONLY the cover letter text. Do not include placeholders like '[Insert Date]' or markdown headers.
"""
        try:
            response = model.generate_content(prompt)
            letter_text = getattr(response, "text", "").strip()
            if letter_text and len(letter_text) > 150:
                return {
                    "cover_letter": letter_text,
                    "target_role": role,
                    "company_name": company,
                    "generated_by": "gemini-2.0-flash",
                }
        except Exception as e:
            logger.warning(f"Cover letter generation via Gemini failed ({e}); using template fallback.")

    # Deterministic high-quality fallback
    fallback_letter = f"""Dear Hiring Team at {company},

I am writing to express my strong interest in the {role} position. With a solid foundation in {skills_highlight} and a demonstrated passion for solving real-world technical problems, I am excited about the opportunity to contribute effectively to your team.

Throughout my recent projects and practical work, I have focused on building scalable, reliable applications and refining my expertise in {skills_highlight}. I enjoy translating product requirements into clean, maintainable code and collaborating across teams to deliver user-focused outcomes. My background aligns directly with the core competencies highlighted in your job requirements.

I would welcome the opportunity to discuss how my skill set and enthusiasm can support {company}'s ongoing initiatives. Thank you for your time and consideration, and I look forward to the possibility of an interview.

Sincerely,
{name}"""

    return {
        "cover_letter": fallback_letter.strip(),
        "target_role": role,
        "company_name": company,
        "generated_by": "template-fallback",
    }


