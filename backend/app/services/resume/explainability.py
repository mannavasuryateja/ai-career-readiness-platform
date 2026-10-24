from app.services.resume.onet_skills import ONET_SKILLS


def classify_missing_skills(missing_skills):

    critical = []
    moderate = []
    optional = []

    for skill in missing_skills:
        category = ONET_SKILLS.get(skill, {}).get("category", "")

        if category in ["Programming", "Cloud Computing"]:
            critical.append(skill)

        elif category in ["Web Development", "Database", "DevOps"]:
            moderate.append(skill)

        else:
            optional.append(skill)

    return {
        "critical_missing": critical,
        "moderate_missing": moderate,
        "optional_missing": optional
    }


def generate_score_breakdown(skill_score, category_score, tfidf_score, semantic_score):

    return {
        "skill_overlap_percent": round(skill_score * 100, 2),
        "category_overlap_percent": round(category_score * 100, 2),
        "tfidf_similarity_percent": round(tfidf_score * 100, 2),
        "semantic_similarity_percent": round(semantic_score * 100, 2)
    }


def generate_explanation(final_score, matched, critical_missing):

    if final_score >= 70:
        level = "Strong Match"
    elif final_score >= 45:
        level = "Moderate Match"
    else:
        level = "Low Match"

    explanation = (
        f"Overall Assessment: {level}. "
        f"You matched {len(matched)} required skills. "
        f"There are {len(critical_missing)} critical skills missing, "
        f"primarily in high-impact domains such as programming or cloud technologies. "
        f"Addressing these gaps will significantly improve your readiness score."
    )

    return explanation

