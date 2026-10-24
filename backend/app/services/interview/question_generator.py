import re
from typing import Optional, List, Tuple, Dict, Any


class QuestionGenerator:
    """Stage-based, context-aware interview question generator with real interview flow."""

    ROLE_STAGES = [
        "introduction",
        "role_interest",
        "core_skills",
        "project_example",
        "technical_scenario",
        "problem_solving",
        "closing",
    ]

    RESUME_STAGES = [
        "introduction",
        "project_selection",
        "project_overview",
        "role_contribution",
        "technical_implementation",
        "challenge_discussion",
        "skill_validation",
        "scenario_question",
        "closing",
    ]

    SECTION_HEADERS = {
        "summary",
        "work experience",
        "projects",
        "education",
        "skills",
        "certifications",
        "hackathons",
        "experience",
    }

    BAD_PROJECT_PHRASES = {
        "github",
        "linkedin",
        "portfolio",
        "b.tech",
        "class 10th",
        "class 11th",
        "class 12th",
        "frontend developer",
        "full stack web development course",
        "srmap university",
        "sri chaitanya college",
        "sri chaitanya school",
    }

    PROJECT_LINE_PATTERN = re.compile(
        r"^(?:[-•]\s*)?([A-Z][A-Za-z0-9&+().,\-/ ]{2,80}?)(?:\s*\((.*?)\))?\s*(?:\[.*?\])*\s*$"
    )

    @staticmethod
    def get_interview_stage_sequence(interview_type: str, questions_asked: int) -> str:
        stages = (
            QuestionGenerator.ROLE_STAGES
            if interview_type == "role"
            else QuestionGenerator.RESUME_STAGES
        )
        if questions_asked <= 1:
            return stages[0]
        index = min(questions_asked - 1, len(stages) - 1)
        return stages[index]

    @staticmethod
    def _extract_candidate_name(text: str) -> Optional[str]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return None
        first_line = lines[0]
        if len(first_line.split()) <= 4 and not any(ch.isdigit() for ch in first_line):
            return first_line
        return None

    @staticmethod
    def _looks_like_valid_project(candidate: str, candidate_name: Optional[str]) -> bool:
        c = candidate.strip()
        cl = c.lower()

        if not c or cl in QuestionGenerator.SECTION_HEADERS:
            return False
        if candidate_name and cl == candidate_name.lower():
            return False
        if len(c.split()) > 8:
            return False
        if any(bad in cl for bad in QuestionGenerator.BAD_PROJECT_PHRASES):
            return False
        if any(token in cl for token in ["cgpa", "percentage", "present", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]):
            return False
        if "developer" in cl and "portal" not in cl and "assistant" not in cl and "platform" not in cl:
            return False

        return True

    @staticmethod
    def extract_resume_entities(
        extracted_text: Optional[str],
        resume_summary: Optional[str],
    ) -> Dict[str, Any]:
        text = f"{resume_summary or ''}\n{extracted_text or ''}".strip()
        lowered = text.lower()
        candidate_name = QuestionGenerator._extract_candidate_name(text)

        project_names: List[str] = []
        technologies: List[str] = []
        backend_skills: List[str] = []
        frontend_skills: List[str] = []
        databases: List[str] = []
        role_keywords: List[str] = []

        in_projects_section = False
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            line_lower = line.lower()

            if line_lower in QuestionGenerator.SECTION_HEADERS:
                in_projects_section = line_lower == "projects"
                continue

            if line_lower in {"education", "skills", "certifications", "hackathons", "work experience", "summary"}:
                in_projects_section = False

            if not in_projects_section:
                continue

            match = QuestionGenerator.PROJECT_LINE_PATTERN.match(line)
            if not match:
                continue

            candidate = (match.group(1) or "").strip()
            if not QuestionGenerator._looks_like_valid_project(candidate, candidate_name):
                continue

            if candidate not in project_names:
                project_names.append(candidate)

        keyword_map = {
            "react.js": "React.js",
            "react": "React.js",
            "node.js": "Node.js",
            "node": "Node.js",
            "express.js": "Express.js",
            "express": "Express.js",
            "mongodb": "MongoDB",
            "mongoose": "Mongoose",
            "mysql": "MySQL",
            "sql": "SQL",
            "jwt": "JWT Authentication",
            "tailwind css": "Tailwind CSS",
            "tailwind": "Tailwind CSS",
            "javascript": "JavaScript",
            "python": "Python",
            "java": "Java",
            "c++": "C++",
            "c": "C",
            "html": "HTML",
            "css": "CSS",
            "bootstrap": "Bootstrap",
            "material ui": "Material UI",
            "rest api": "REST API",
            "restful api": "REST API",
            "axios": "Axios",
            "git": "Git",
            "github": "GitHub",
            "vercel": "Vercel",
            "stripe": "Stripe",
            "authentication": "Authentication",
            "authorization": "Authorization",
            "file upload": "File Uploads",
            "backend": "Backend Development",
            "frontend": "Frontend Development",
            "full stack": "Full Stack Development",
            "mern": "MERN Stack",
            "database": "Database Design",
        }

        for raw, canonical in keyword_map.items():
            if raw in lowered and canonical not in technologies:
                technologies.append(canonical)

        for item in technologies:
            low = item.lower()
            if any(x in low for x in ["node", "express", "jwt", "authentication", "authorization", "backend", "api", "file upload"]):
                backend_skills.append(item)
            if any(x in low for x in ["react", "html", "css", "tailwind", "bootstrap", "material ui", "frontend"]):
                frontend_skills.append(item)
            if any(x in low for x in ["mongodb", "mysql", "sql", "mongoose", "database"]):
                databases.append(item)

        role_candidates = [
            "frontend developer",
            "backend developer",
            "full stack developer",
            "mern stack developer",
            "software developer",
            "web developer",
            "python developer",
            "java developer",
        ]
        for role in role_candidates:
            if role in lowered:
                role_keywords.append(role.title())

        return {
            "candidate_name": candidate_name,
            "project_names": project_names[:5],
            "technologies": technologies[:12],
            "backend_skills": backend_skills[:8],
            "frontend_skills": frontend_skills[:8],
            "databases": databases[:6],
            "role_keywords": role_keywords[:5],
        }

    @staticmethod
    def extract_answer_entities(answer: Optional[str]) -> Dict[str, Any]:
        text = (answer or "").strip()
        lowered = text.lower()

        mentioned_technologies: List[str] = []
        mentioned_projects: List[str] = []

        canonical_map = {
            "react": "React.js",
            "react.js": "React.js",
            "node": "Node.js",
            "node.js": "Node.js",
            "express": "Express.js",
            "express.js": "Express.js",
            "mongodb": "MongoDB",
            "mysql": "MySQL",
            "sql": "SQL",
            "jwt": "JWT Authentication",
            "tailwind": "Tailwind CSS",
            "javascript": "JavaScript",
            "python": "Python",
            "java": "Java",
            "api": "API Design",
            "authentication": "Authentication",
            "authorization": "Authorization",
            "file upload": "File Uploads",
            "backend": "Backend Development",
            "frontend": "Frontend Development",
            "database": "Database Design",
        }

        for raw, canonical in canonical_map.items():
            if raw in lowered and canonical not in mentioned_technologies:
                mentioned_technologies.append(canonical)

        project_like = re.findall(
            r"\b[A-Z][A-Za-z0-9&+\-]{2,}(?:\s+[A-Z][A-Za-z0-9&+\-]{2,}){0,4}\b",
            text,
        )
        for p in project_like:
            pl = p.lower().strip()
            if pl not in {"i", "my", "it"} and p not in mentioned_projects:
                mentioned_projects.append(p)

        word_count = len(text.split())
        if word_count <= 2:
            confidence = "very_low"
        elif word_count <= 8:
            confidence = "low"
        elif word_count <= 25:
            confidence = "medium"
        else:
            confidence = "high"

        return {
            "mentioned_technologies": mentioned_technologies[:8],
            "mentioned_projects": mentioned_projects[:5],
            "confidence_hint": confidence,
        }

    @staticmethod
    def detect_selected_project(
        previous_answer: Optional[str],
        resume_entities: Dict[str, Any],
    ) -> Optional[str]:
        if not previous_answer:
            return None

        answer_lower = previous_answer.lower()
        for project in resume_entities.get("project_names", []):
            if project.lower() in answer_lower:
                return project

        mentioned_projects = QuestionGenerator.extract_answer_entities(previous_answer).get("mentioned_projects", [])
        for mp in mentioned_projects:
            for project in resume_entities.get("project_names", []):
                if mp.lower() in project.lower() or project.lower() in mp.lower():
                    return project

        return None

    @staticmethod
    def choose_focus_topic(
        interview_type: str,
        current_stage: str,
        role: Optional[str],
        resume_entities: Dict[str, Any],
        answer_entities: Dict[str, Any],
        previous_answer: Optional[str],
        topics_covered: Optional[List[str]],
    ) -> Dict[str, str]:
        topics_covered = topics_covered or []

        project_names = resume_entities.get("project_names", [])
        technologies = resume_entities.get("technologies", [])
        backend_skills = resume_entities.get("backend_skills", [])
        frontend_skills = resume_entities.get("frontend_skills", [])
        databases = resume_entities.get("databases", [])

        selected_project = QuestionGenerator.detect_selected_project(previous_answer, resume_entities)
        if not selected_project and project_names:
            selected_project = project_names[0]

        mentioned_technologies = answer_entities.get("mentioned_technologies", [])
        confidence = answer_entities.get("confidence_hint", "medium")

        if interview_type == "resume":
            if current_stage == "introduction":
                return {"type": "intro", "value": "your background"}

            if current_stage == "project_selection":
                return {"type": "project", "value": selected_project or "your best project"}

            if current_stage in {"project_overview", "role_contribution", "challenge_discussion"}:
                return {"type": "project", "value": selected_project or "your project"}

            if current_stage in {"technical_implementation", "skill_validation"}:
                if mentioned_technologies:
                    return {"type": "technology", "value": mentioned_technologies[0]}
                for bucket in [backend_skills, frontend_skills, databases, technologies]:
                    for item in bucket:
                        if item.lower() not in [t.lower() for t in topics_covered]:
                            return {"type": "technology", "value": item}
                return {"type": "technology", "value": "your technical stack"}

            if current_stage == "scenario_question":
                if backend_skills:
                    return {"type": "scenario", "value": "backend scalability"}
                if frontend_skills:
                    return {"type": "scenario", "value": "frontend performance"}
                return {"type": "scenario", "value": "system design"}

            return {"type": "closing", "value": "your profile"}

        role_lower = (role or "this role").lower()
        if current_stage == "introduction":
            return {"type": "intro", "value": role or "this role"}
        if current_stage == "role_interest":
            return {"type": "role", "value": role or "this role"}
        if current_stage == "core_skills":
            if "frontend" in role_lower:
                return {"type": "technology", "value": "React.js"}
            if "backend" in role_lower:
                return {"type": "technology", "value": "Node.js and API design"}
            if "python" in role_lower:
                return {"type": "technology", "value": "Python"}
            return {"type": "role", "value": role or "this role"}
        if current_stage == "project_example":
            return {"type": "project", "value": "a relevant project from your experience"}
        if current_stage in {"technical_scenario", "problem_solving"}:
            if confidence in {"very_low", "low"}:
                return {"type": "clarification", "value": "your previous answer"}
            return {"type": "scenario", "value": role or "this role"}

        return {"type": "closing", "value": role or "this role"}

    @staticmethod
    def build_contextual_question(
        interview_type: str,
        current_stage: str,
        role: Optional[str],
        focus: Dict[str, str],
        answer_entities: Dict[str, Any],
    ) -> str:
        focus_type = focus.get("type", "")
        focus_value = focus.get("value", "")
        confidence = answer_entities.get("confidence_hint", "medium")

        if interview_type == "resume":
            if current_stage == "introduction":
                return "Tell me about yourself and walk me through your background."

            if current_stage == "project_selection":
                return "Which project on your resume are you most confident discussing, and why?"

            if current_stage == "project_overview":
                return f"Can you explain the goal of {focus_value} and what problem it was solving?"

            if current_stage == "role_contribution":
                if confidence in {"very_low", "low"}:
                    return f"Can you explain your specific role and contribution in {focus_value} in more detail?"
                return f"What was your specific role and contribution in {focus_value}?"

            if current_stage == "technical_implementation":
                return f"Can you explain how you implemented {focus_value} in that project?"

            if current_stage == "challenge_discussion":
                return f"What technical challenges did you face while working on {focus_value if focus_type == 'project' else 'that project'}, and how did you solve them?"

            if current_stage == "skill_validation":
                return f"How have you used {focus_value} in your projects, and why do you consider it one of your stronger skills?"

            if current_stage == "scenario_question":
                if focus_value == "backend scalability":
                    return "If your project suddenly had to support 10 times more users, what backend changes would you make?"
                if focus_value == "frontend performance":
                    return "If your frontend became slow with more users and data, how would you improve performance?"
                return "If this project had to scale significantly, what technical improvements would you make?"

            return "Why do you think your current skills and experience make you ready for your next role?"

        if current_stage == "introduction":
            return "Please introduce yourself."

        if current_stage == "role_interest":
            return f"Why are you interested in the {focus_value} role?"

        if current_stage == "core_skills":
            if focus_type == "technology":
                return f"For a {role or 'technical'} role, how would you apply {focus_value} in a real project?"
            return f"What technical skills do you think are most important for a {role or 'technical'} role?"

        if current_stage == "project_example":
            return "Can you describe a project from your experience that best demonstrates your fit for this role?"

        if current_stage == "technical_scenario":
            return f"Suppose you are working in a {role or 'technical'} role and a production issue occurs. How would you approach diagnosing and fixing it?"

        if current_stage == "problem_solving":
            if focus_type == "clarification":
                return "Could you explain your previous answer in more detail with a concrete example?"
            return f"What kind of technical challenges do you expect in a {role or 'technical'} role, and how would you handle them?"

        return f"Why do you think you are a good fit for the {role or 'technical'} role?"

    @staticmethod
    def _get_fallback_question(
        interview_type: str,
        next_stage: str,
        role: Optional[str] = None,
    ) -> Tuple[str, str, str]:
        fallback_map = {
            "introduction": "Tell me about yourself.",
            "project_selection": "Which project on your resume are you most confident discussing?",
            "project_overview": "Can you explain your project and its main goal?",
            "role_contribution": "What was your specific role in that project?",
            "technical_implementation": "Can you explain the technical implementation in more detail?",
            "challenge_discussion": "What challenges did you face in that project?",
            "skill_validation": "Which technical skill are you strongest in?",
            "scenario_question": "If your project had to scale, what changes would you make?",
            "closing": "Why do you think you are a good fit for this role?",
            "role_interest": f"Why are you interested in the {role or 'selected'} role?",
            "core_skills": f"What core technical skills are important for a {role or 'technical'} role?",
            "project_example": "Tell me about a relevant project you have worked on.",
            "technical_scenario": "How would you handle a real production issue?",
            "problem_solving": "How do you approach solving technical challenges?",
        }

        question = fallback_map.get(next_stage, "Tell me more about your experience.")
        return question, next_stage, next_stage

    @staticmethod
    def get_next_question(
        interview_type: str,
        questions_asked: int,
        role: Optional[str] = None,
        extracted_text: Optional[str] = None,
        resume_summary: Optional[str] = None,
        previous_question: Optional[str] = None,
        previous_answer: Optional[str] = None,
        topics_covered: Optional[List[str]] = None,
    ) -> Tuple[str, str, str]:
        next_stage = QuestionGenerator.get_interview_stage_sequence(
            interview_type,
            questions_asked + 1,
        )

        resume_entities = QuestionGenerator.extract_resume_entities(extracted_text, resume_summary)
        answer_entities = QuestionGenerator.extract_answer_entities(previous_answer)

        focus = QuestionGenerator.choose_focus_topic(
            interview_type=interview_type,
            current_stage=next_stage,
            role=role,
            resume_entities=resume_entities,
            answer_entities=answer_entities,
            previous_answer=previous_answer,
            topics_covered=topics_covered,
        )

        question = QuestionGenerator.build_contextual_question(
            interview_type=interview_type,
            current_stage=next_stage,
            role=role,
            focus=focus,
            answer_entities=answer_entities,
        )

        if not question or len(question.strip()) < 10:
            return QuestionGenerator._get_fallback_question(
                interview_type=interview_type,
                next_stage=next_stage,
                role=role,
            )

        return question, next_stage, next_stage

    @staticmethod
    def get_intro_question(
        interview_type: str,
        role: Optional[str] = None,
        extracted_text: Optional[str] = None,
        resume_summary: Optional[str] = None,
    ) -> Tuple[str, str, str]:
        first_stage = QuestionGenerator.get_interview_stage_sequence(interview_type, 1)
        question = (
            "Please introduce yourself."
            if interview_type == "role"
            else "Tell me about yourself and walk me through your background."
        )
        return question, first_stage, first_stage

    @staticmethod
    def extract_topic_from_answer(answer: Optional[str]) -> Optional[str]:
        entities = QuestionGenerator.extract_answer_entities(answer)
        if entities["mentioned_technologies"]:
            return entities["mentioned_technologies"][0]
        if entities["mentioned_projects"]:
            return entities["mentioned_projects"][0]
        return None

    @staticmethod
    def get_topic_from_stage(stage_name: str) -> str:
        stage_to_topic = {
            "introduction": "introduction",
            "project_selection": "project_selection",
            "project_overview": "project_overview",
            "role_contribution": "role_and_contribution",
            "technical_implementation": "technical_implementation",
            "challenge_discussion": "challenge_discussion",
            "skill_validation": "skill_validation",
            "scenario_question": "scenario_question",
            "closing": "closing",
            "role_interest": "role_interest",
            "core_skills": "core_skills",
            "project_example": "project_example",
            "technical_scenario": "technical_scenario",
            "problem_solving": "problem_solving",
        }
        return stage_to_topic.get(stage_name, stage_name)