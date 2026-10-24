from app.services.resume.weighted_scoring import calculate_weighted_skill_score


def get_skill_priority_weight(skill, critical, moderate, optional):
    if skill in critical:
        return 3
    elif skill in moderate:
        return 2
    else:
        return 1


def get_impact_level(weight):
    if weight == 3:
        return "High"
    elif weight == 2:
        return "Medium"
    else:
        return "Low"


def simulate_skill_improvement(
    resume_skills,
    jd_skills,
    category_overlap,
    tfidf_score,
    semantic_score,
    missing_skills,
    critical_missing,
    moderate_missing,
    optional_missing
):

    simulations = []

    # ---- CURRENT SCORE ----
    current_skill_score = calculate_weighted_skill_score(
        resume_skills, jd_skills
    )

    current_final_score = (
        0.4 * current_skill_score +
        0.2 * category_overlap +
        0.2 * tfidf_score +
        0.2 * semantic_score
    ) * 100

    # ✅ FIX: avoid negative gap
    remaining_gap = max(0, 100 - current_final_score)

    # ---- Compute Weights ----
    skill_weights = {}
    total_weight = 0

    for skill in missing_skills:
        weight = get_skill_priority_weight(
            skill,
            critical_missing,
            moderate_missing,
            optional_missing
        )
        skill_weights[skill] = weight
        total_weight += weight

    # ---- Distribute Gap ----
    total_allocated = 0

    for i, skill in enumerate(missing_skills):

        weight = skill_weights[skill]

        if i == len(missing_skills) - 1:
            contribution = remaining_gap - total_allocated
        else:
            contribution = (weight / total_weight) * remaining_gap
            total_allocated += contribution

        projected_score = current_final_score + contribution

        simulations.append({
            "skill_if_learned": skill,
            "priority_weight": weight,
            "projected_score": float(round(projected_score, 2)),   # ✅ safe float
            "score_increase": float(round(contribution, 2)),       # ✅ safe float
            "impact_level": get_impact_level(weight)              # ✅ NEW
        })

    simulations = sorted(
        simulations,
        key=lambda x: x["score_increase"],
        reverse=True
    )

    return simulations