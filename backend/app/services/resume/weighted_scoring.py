from app.services.resume.onet_skills import ONET_SKILLS

def get_skill_weight(skill):

    category = ONET_SKILLS.get(skill, {}).get("category", "")

    if category in ["Programming", "Cloud Computing"]:
        return 5

    elif category in ["Web Development"]:
        return 4

    elif category in ["Database", "DevOps"]:
        return 3

    elif category in ["Development Tools"]:
        return 2

    elif category in ["Soft Skills"]:
        return 1

    else:
        return 2



def calculate_weighted_skill_score(resume_skills, jd_skills):

    total_weight = 0
    matched_weight = 0

    for skill in jd_skills:
        weight = get_skill_weight(skill)
        total_weight += weight

        if skill in resume_skills:
            matched_weight += weight

    if total_weight == 0:
        return 0

    return matched_weight / total_weight
