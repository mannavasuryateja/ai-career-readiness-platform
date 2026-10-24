import random
import json
from app.services.resume.onet_skills import ONET_SKILLS


def get_random_alias(skill_name):
    skill_data = ONET_SKILLS.get(skill_name, {})
    aliases = skill_data.get("aliases", [])
    if aliases:
        return random.choice(aliases)
    return skill_name


def add_case_noise(skill):
    transformations = [
        skill.lower(),
        skill.upper(),
        skill.title(),
        skill
    ]
    return random.choice(transformations)


def generate_synthetic_dataset(
    num_resumes=50,
    num_jds=20,
    output_file="evaluation_dataset.json"
):

    canonical_skills = list(ONET_SKILLS.keys())

    resumes = {}
    jds = {}
    evaluation_pairs = []

    print(f"Total canonical skills: {len(canonical_skills)}")

    # ---- STEP 1: Generate canonical resume + JD base skills ----

    canonical_resume_map = {}
    canonical_jd_map = {}

    for r in range(1, num_resumes + 1):
        base_skills = random.sample(canonical_skills, random.randint(8, 15))
        canonical_resume_map[f"resume_{r}"] = base_skills

    for j in range(1, num_jds + 1):
        base_skills = random.sample(canonical_skills, random.randint(6, 12))
        canonical_jd_map[f"jd_{j}"] = base_skills

    # ---- STEP 2: Create noisy display versions ----

    for r_id, base_skills in canonical_resume_map.items():

        noisy_skills = []
        for skill in base_skills:
            alias = get_random_alias(skill)
            noisy = add_case_noise(alias)
            noisy_skills.append(noisy)

        # Optional random noise skill
        if random.random() < 0.3:
            noisy_skills.append("RandomToolXYZ")

        resumes[r_id] = noisy_skills

    for j_id, base_skills in canonical_jd_map.items():

        noisy_skills = []
        for skill in base_skills:
            alias = get_random_alias(skill)
            noisy = add_case_noise(alias)
            noisy_skills.append(noisy)

        if random.random() < 0.3:
            noisy_skills.append("Communication")

        jds[j_id] = noisy_skills

    # ---- STEP 3: Create evaluation pairs with CORRECT ground truth ----

    for r_id in canonical_resume_map:
        for j_id in canonical_jd_map:

            canonical_resume = set(canonical_resume_map[r_id])
            canonical_jd = set(canonical_jd_map[j_id])

            ground_truth = list(canonical_resume & canonical_jd)

            evaluation_pairs.append({
                "resume_id": r_id,
                "jd_id": j_id,
                "resume_skills": resumes[r_id],      # noisy version
                "jd_skills": jds[j_id],              # noisy version
                "true_matched_skills": ground_truth  # clean canonical
            })

    dataset = {
        "resumes": resumes,
        "job_descriptions": jds,
        "evaluation_pairs": evaluation_pairs
    }

    with open(output_file, "w") as f:
        json.dump(dataset, f, indent=4)

    print(f"Dataset generated correctly: {output_file}")


if __name__ == "__main__":
    generate_synthetic_dataset()
