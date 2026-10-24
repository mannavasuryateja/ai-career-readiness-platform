from fastapi import FastAPI, File, UploadFile, Form
import shutil
import os
from fastapi.middleware.cors import CORSMiddleware



from app.services.resume.parser import extract_resume_data, extract_text_from_pdf, extract_text_from_docx, extract_sections, normalize_with_onet, categorize_skills
from app.services.resume.matching import (
    skill_overlap_score,
    category_overlap_score,
    tfidf_similarity,
    semantic_similarity,
    compute_final_score
)

from app.services.resume.explainability import (
    classify_missing_skills,
    generate_score_breakdown,
    generate_explanation
)
from app.services.resume.weighted_scoring import calculate_weighted_skill_score

from app.services.resume.recommendations import generate_recommendations
from app.services.resume.learning_roadmap import generate_learning_roadmap



from app.services.resume.gemini_service import generate_learning_plan_batch
from app.services.resume.youtube_service import fetch_youtube_links


from app.services.resume.simulation_engine import simulate_skill_improvement







app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.post("/analyze/")
async def analyze(
    resume: UploadFile = File(...),
    job_description_file: UploadFile = File(None),
    job_description_text: str = Form(None)
):

    # ------------------------
    # Save Resume
    # ------------------------
    resume_path = os.path.join(UPLOAD_FOLDER, resume.filename)
    with open(resume_path, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)

    resume_data = extract_resume_data(resume_path)
    resume_skills = resume_data["cleaned_skills"]
    resume_categories = resume_data["onet_categorized_skills"]
    resume_text = "\n".join(
        resume_data["sections"]["skills"] +
        resume_data["sections"]["projects"] +
        resume_data["sections"]["experience"]
    )

    # ------------------------
    # Handle JD Input (Flexible)
    # ------------------------
    jd_text = ""

    # Case 1: JD uploaded as file
    if job_description_file:
        jd_path = os.path.join(UPLOAD_FOLDER, job_description_file.filename)
        with open(jd_path, "wb") as buffer:
            shutil.copyfileobj(job_description_file.file, buffer)

        if jd_path.endswith(".pdf"):
            jd_text = extract_text_from_pdf(jd_path)
        elif jd_path.endswith(".docx"):
            jd_text = extract_text_from_docx(jd_path)

    # Case 2: JD entered as raw text
    elif job_description_text:
        jd_text = job_description_text

    else:
        return {"error": "Please provide job description as file or text."}

    # ------------------------
    # Parse JD
    # ------------------------
    # Extract skills directly from full JD text
    jd_skills = normalize_with_onet([jd_text])
    jd_categories = categorize_skills(jd_skills)

    jd_categories = categorize_skills(jd_skills)

    # ------------------------
    # Compute Scores
    # ------------------------
    s_score = calculate_weighted_skill_score(resume_skills, jd_skills)
    c_score = category_overlap_score(resume_categories, jd_categories)
    tfidf_score = tfidf_similarity(resume_text, jd_text)
    sem_score = semantic_similarity(resume_text, jd_text)

    final_score = compute_final_score(
        s_score, c_score, tfidf_score, sem_score
    )

    missing_skills = list(set(jd_skills) - set(resume_skills))
    
    
    
    


    matched_skills = list(set(jd_skills).intersection(set(resume_skills)))

    classification = classify_missing_skills(missing_skills)
    recommendations = generate_recommendations(
    classification["critical_missing"],
    classification["moderate_missing"]
    )
    learning_roadmap = generate_learning_roadmap(
    classification["critical_missing"],
    classification["moderate_missing"]
    )
    
    score_simulation = simulate_skill_improvement(
    resume_skills,
    jd_skills,
    c_score,
    tfidf_score,
    sem_score,
    missing_skills,
    classification["critical_missing"],
    classification["moderate_missing"],
    classification["optional_missing"]
    )
    
    missing_for_learning = classification["critical_missing"] + classification["moderate_missing"] + classification["optional_missing"] 

    gemini_plans = generate_learning_plan_batch(missing_for_learning)

    learning_output = []

    for plan in gemini_plans:

        # yt_links = fetch_youtube_links(plan["skill"])
        
        yt_links = fetch_youtube_links(plan["skill"], max_results=3)


        learning_output.append({
            "skill": plan["skill"],
            "priority": "High" if plan["skill"] in classification["critical_missing"] else "Medium",
            "recommendation": plan["recommendation"],
            "roadmap_steps": plan["roadmap_steps"],
            "estimated_time": plan["estimated_time"],
            "career_impact": plan["career_impact"],
            "youtube_links": yt_links
        })

    
    



    breakdown = generate_score_breakdown(
        s_score, c_score, tfidf_score, sem_score
    )

    explanation_text = generate_explanation(
        final_score,
        matched_skills,
        classification["critical_missing"]
    )

    return {
    "resume_skills": resume_skills,
    "jd_skills": jd_skills,
    "matched_skills": matched_skills,
    "missing_skills": missing_skills,
    "critical_missing": classification["critical_missing"],
    "moderate_missing": classification["moderate_missing"],
    "optional_missing": classification["optional_missing"],
    "score_breakdown": breakdown,
    "final_readiness_score": final_score,
    "learning_plan": learning_output,
    "explanation": explanation_text,
    "score_simulation": score_simulation,

}




# UPLOAD_FOLDER = "uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_data = extract_resume_data(file_path)

    return {
        "filename": file.filename,
        "extracted_data": extracted_data
    }