# Resume Backend Services
# Files needed in this directory (copy from resume_analyzer/backend/app/):
# 1. parser.py - Resume and JD text extraction
# 2. matching.py - Skill matching algorithms
# 3. explainability.py - Score explanation generation
# 4. weighted_scoring.py - Weighted score calculations
# 5. recommendations.py - Learning recommendations
# 6. learning_roadmap.py - Learning path generation
# 7. gemini_service.py - Gemini LLM integration
# 8. youtube_service.py - YouTube resource fetching
# 9. simulation_engine.py - Skill improvement simulation
# 10. utils.py - Utility functions
# 11. onet_skills.py - ONET skills database
# 12. onet_categories.py - ONET categories
# 13. config.py - Configuration

# IMPORTANT: Update all imports in these files!
# Change: from app.FILENAME import ...
# To: from app.services.resume.FILENAME import ...

# After copying and updating imports, these should work:
# from app.services.resume.parser import extract_resume_data
# from app.services.resume.matching import skill_overlap_score
# from app.services.resume.gemini_service import generate_learning_plan_batch
