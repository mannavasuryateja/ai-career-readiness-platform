from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends, status
from typing import Optional

from app.models.schemas import (
    AnalysisResult,
    UploadResumeResponse,
    CoverLetterRequest,
    CoverLetterResponse,
)

from app.core.deps import get_current_user
from app.core.quota import consume_daily_quota, KIND_ANALYSIS
from app.core.uploads import (
    read_allowed_upload,
    parse_resume_upload,
    extract_document_text,
    validate_jd_text,
)
from app.services.storage_service import StorageService

# Import all resume analysis functions
from app.services.resume.parser import normalize_with_onet, categorize_skills
from app.services.resume.matching import (
    category_overlap_score,
    tfidf_similarity,
    semantic_similarity,
    compute_final_score,
)
from app.services.resume.explainability import (
    classify_missing_skills,
    generate_score_breakdown,
    generate_explanation,
)
from app.services.resume.weighted_scoring import calculate_weighted_skill_score
from app.services.resume.recommendations import generate_recommendations
from app.services.resume.learning_roadmap import generate_learning_roadmap
from app.services.resume.gemini_service import generate_learning_plan_batch, generate_cover_letter
from app.services.resume.youtube_service import fetch_youtube_links

from app.services.resume.simulation_engine import simulate_skill_improvement

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post("/analyze", response_model=AnalysisResult)
async def analyze(
    resume: UploadFile = File(...),
    job_description_file: Optional[UploadFile] = File(None),
    job_description_text: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Analyze resume against job description in-memory.
    Enforces per-user daily quota and stores extracted data in MongoDB.
    """
    user_id = str(current_user["_id"])

    # 1. Enforce & consume daily analysis quota
    await consume_daily_quota(user_id, KIND_ANALYSIS)

    try:
        # 2. Read and parse resume strictly in-memory (no disk writes)
        resume_bytes, resume_filename, resume_ext = await read_allowed_upload(resume)
        resume_data = parse_resume_upload(resume_bytes, resume_ext)

        resume_skills = resume_data["cleaned_skills"]
        resume_categories = resume_data["onet_categorized_skills"]
        resume_text = "\n".join(
            resume_data["sections"]["skills"] +
            resume_data["sections"]["projects"] +
            resume_data["sections"]["experience"]
        )

        # Store resume in MongoDB
        resume_id = await StorageService.store_resume(
            filename=resume_filename,
            original_filename=resume_filename,
            extracted_text=resume_text,
            extracted_data=resume_data,
            skills=resume_skills,
            categories=resume_categories,
            user_id=user_id,
            file_path=None,
        )

        # 3. Read and parse JD in-memory
        jd_text = ""
        jd_title = "Target Job Description"
        jd_company = "Unknown"

        if job_description_file and job_description_file.filename:
            jd_bytes, jd_filename, jd_ext = await read_allowed_upload(job_description_file)
            jd_text = extract_document_text(jd_bytes, jd_ext)
            jd_title = jd_filename
        elif job_description_text:
            jd_text = validate_jd_text(job_description_text)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please provide a job description as a file or text.",
            )

        jd_skills = normalize_with_onet([jd_text])
        jd_categories = categorize_skills(jd_skills)

        # Store JD in MongoDB
        jd_id = await StorageService.store_jd(
            title=jd_title,
            company=jd_company,
            description_text=jd_text,
            skills=jd_skills,
            categories=jd_categories,
            user_id=user_id,
            file_path=None,
        )

        # 4. Compute Match Scores
        s_score = calculate_weighted_skill_score(resume_skills, jd_skills)
        c_score = category_overlap_score(resume_categories, jd_categories)
        tfidf_score = tfidf_similarity(resume_text, jd_text)
        sem_score = semantic_similarity(resume_text, jd_text)

        final_score = compute_final_score(s_score, c_score, tfidf_score, sem_score)

        missing_skills = list(set(jd_skills) - set(resume_skills))
        matched_skills = list(set(jd_skills).intersection(set(resume_skills)))

        classification = classify_missing_skills(missing_skills)
        recommendations = generate_recommendations(
            classification["critical_missing"],
            classification["moderate_missing"],
        )
        learning_roadmap = generate_learning_roadmap(
            classification["critical_missing"],
            classification["moderate_missing"],
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
            classification["optional_missing"],
        )

        missing_for_learning = (
            classification["critical_missing"] +
            classification["moderate_missing"] +
            classification["optional_missing"]
        )

        gemini_plans = generate_learning_plan_batch(missing_for_learning)

        learning_output = []
        for plan in gemini_plans:
            yt_links = fetch_youtube_links(plan.get("skill", ""), max_results=3)
            learning_output.append({
                "skill": plan.get("skill", ""),
                "priority": "High" if plan.get("skill") in classification["critical_missing"] else "Medium",
                "recommendation": plan.get("recommendation", ""),
                "roadmap_steps": plan.get("roadmap_steps", []),
                "estimated_time": plan.get("estimated_time", "1-2 weeks"),
                "career_impact": plan.get("career_impact", "Medium"),
                "youtube_links": yt_links,
            })

        breakdown = generate_score_breakdown(s_score, c_score, tfidf_score, sem_score)

        explanation_text = generate_explanation(
            final_score,
            matched_skills,
            classification["critical_missing"],
        )

        # 5. Build AnalysisResult
        analysis_result = AnalysisResult(
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            critical_missing=classification["critical_missing"],
            moderate_missing=classification["moderate_missing"],
            optional_missing=classification["optional_missing"],
            score_breakdown=breakdown,
            final_readiness_score=final_score,
            learning_plan=learning_output,
            explanation=explanation_text,
            score_simulation=score_simulation,
        )

        # Store analysis result in MongoDB
        await StorageService.store_analysis_result(
            resume_filename=resume_filename,
            jd_title=jd_title,
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            critical_missing=classification["critical_missing"],
            moderate_missing=classification["moderate_missing"],
            optional_missing=classification["optional_missing"],
            score_breakdown=breakdown,
            final_readiness_score=final_score,
            learning_plan=learning_output,
            explanation=explanation_text,
            score_simulation=score_simulation,
            user_id=user_id,
            resume_id=resume_id,
            jd_id=jd_id,
        )

        return analysis_result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error analyzing resume: {str(e)}",
        )


@router.post("/upload", response_model=UploadResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Upload and extract resume data in-memory, store in MongoDB."""
    try:
        user_id = str(current_user["_id"])
        resume_bytes, original_filename, ext = await read_allowed_upload(file)
        extracted_data = parse_resume_upload(resume_bytes, ext)

        resume_text = "\n".join(
            extracted_data["sections"]["skills"] +
            extracted_data["sections"]["projects"] +
            extracted_data["sections"]["experience"]
        )
        resume_skills = extracted_data["cleaned_skills"]
        resume_categories = extracted_data["onet_categorized_skills"]

        resume_id = await StorageService.store_resume(
            filename=original_filename,
            original_filename=original_filename,
            extracted_text=resume_text,
            extracted_data=extracted_data,
            skills=resume_skills,
            categories=resume_categories,
            user_id=user_id,
            file_path=None,
        )

        return UploadResumeResponse(
            filename=original_filename,
            extracted_data={
                **extracted_data,
                "resume_id": resume_id,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error uploading resume: {str(e)}",
        )


@router.post("/cover-letter", response_model=CoverLetterResponse)
async def create_cover_letter(
    request: CoverLetterRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Generate a tailored cover letter from analysis result or direct resume & JD text.
    """
    try:
        user_name = current_user.get("full_name") or "Candidate"
        target_role = request.target_role or "Software Engineer"
        company_name = request.company_name or "Hiring Team"
        resume_text = request.resume_text or ""
        jd_text = request.jd_text or ""
        matched_skills = request.matched_skills or []

        # If analysis_id provided, hydrate from stored analysis
        if request.analysis_id:
            analysis = await StorageService.get_analysis_result(request.analysis_id)
            if analysis and str(analysis.get("user_id")) == str(current_user["_id"]):
                matched_skills = analysis.get("matched_skills") or matched_skills
                target_role = analysis.get("jd_title") or target_role

                if analysis.get("resume_id"):
                    resume_doc = await StorageService.get_resume(str(analysis["resume_id"]))
                    if resume_doc:
                        resume_text = resume_doc.get("extracted_text") or resume_text

                if analysis.get("jd_id"):
                    jd_doc = await StorageService.get_jd(str(analysis["jd_id"]))
                    if jd_doc:
                        jd_text = jd_doc.get("description_text") or jd_text
                        company_name = jd_doc.get("company") or company_name

        result = generate_cover_letter(
            candidate_name=user_name,
            target_role=target_role,
            company_name=company_name,
            matched_skills=matched_skills,
            resume_text=resume_text,
            jd_text=jd_text,
        )

        return CoverLetterResponse(
            cover_letter=result["cover_letter"],
            target_role=result["target_role"],
            company_name=result["company_name"],
            generated_by=result["generated_by"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error generating cover letter: {str(e)}",
        )


# ==================== DATA RETRIEVAL ENDPOINTS ====================


@router.get("/resumes")
async def get_user_resumes(
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
):
    """Get all resumes for the authenticated user."""
    try:
        user_id = str(current_user["_id"])
        resumes = await StorageService.list_resumes(user_id=user_id, limit=limit)
        for resume in resumes:
            resume["_id"] = str(resume["_id"])
        return {"resumes": resumes}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving resumes: {str(e)}",
        )


@router.get("/resumes/{resume_id}")
async def get_resume_by_id(
    resume_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a specific resume by ID (ownership checked)."""
    try:
        resume = await StorageService.get_resume(resume_id)
        if not resume or str(resume.get("user_id")) != str(current_user["_id"]):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
        resume["_id"] = str(resume["_id"])
        return resume
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving resume: {str(e)}",
        )


@router.get("/jds")
async def get_user_jds(
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
):
    """Get all job descriptions for the authenticated user."""
    try:
        user_id = str(current_user["_id"])
        jds = await StorageService.list_jds(user_id=user_id, limit=limit)
        for jd in jds:
            jd["_id"] = str(jd["_id"])
        return {"jds": jds}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving job descriptions: {str(e)}",
        )


@router.get("/jds/{jd_id}")
async def get_jd_by_id(
    jd_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a specific job description by ID (ownership checked)."""
    try:
        jd = await StorageService.get_jd(jd_id)
        if not jd or str(jd.get("user_id")) != str(current_user["_id"]):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
        jd["_id"] = str(jd["_id"])
        return jd
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving job description: {str(e)}",
        )


@router.get("/analysis-results")
async def get_user_analysis_results(
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
):
    """Get all analysis results for the authenticated user."""
    try:
        user_id = str(current_user["_id"])
        results = await StorageService.list_analysis_results(user_id=user_id, limit=limit)
        for result in results:
            result["_id"] = str(result["_id"])
            if result.get("resume_id"):
                result["resume_id"] = str(result["resume_id"])
            if result.get("jd_id"):
                result["jd_id"] = str(result["jd_id"])
        return {"analysis_results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving analysis results: {str(e)}",
        )


@router.get("/analysis-results/{analysis_id}")
async def get_analysis_result_by_id(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a specific analysis result by ID (ownership checked)."""
    try:
        result = await StorageService.get_analysis_result(analysis_id)
        if not result or str(result.get("user_id")) != str(current_user["_id"]):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis result not found")
        result["_id"] = str(result["_id"])
        if result.get("resume_id"):
            result["resume_id"] = str(result["resume_id"])
        if result.get("jd_id"):
            result["jd_id"] = str(result["jd_id"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving analysis result: {str(e)}",
        )


@router.delete("/resumes/{resume_id}")
async def delete_resume_by_id(
    resume_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a resume by ID."""
    try:
        resume = await StorageService.get_resume(resume_id)
        if not resume or str(resume.get("user_id")) != str(current_user["_id"]):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
        success = await StorageService.delete_resume(resume_id)
        return {"message": "Resume deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting resume: {str(e)}",
        )


@router.delete("/analysis-results/{analysis_id}")
async def delete_analysis_result_by_id(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete an analysis result by ID."""
    try:
        result = await StorageService.get_analysis_result(analysis_id)
        if not result or str(result.get("user_id")) != str(current_user["_id"]):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis result not found")
        success = await StorageService.delete_analysis_result(analysis_id)
        return {"message": "Analysis result deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting analysis result: {str(e)}",
        )
