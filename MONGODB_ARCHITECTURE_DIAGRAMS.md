# MongoDB Architecture & Workflow Diagrams

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                      │
│  - Upload Resume/JD                                          │
│  - Start Interview                                           │
│  - View Results & History                                    │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI)                           │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    Routes Layer                      │    │
│  │  /resume     /interview     /auth                   │    │
│  └────────────────────┬────────────────────────────────┘    │
│                       │                                      │
│  ┌─────────────────────┴────────────────────────────────┐    │
│  │              Services Layer                          │    │
│  │                                                      │    │
│  │  Resume Analysis   Interview Manager   Auth Service │    │
│  └────────────────────┬────────────────────────────────┘    │
│                       │                                      │
│  ┌─────────────────────┴────────────────────────────────┐    │
│  │          Storage Service (NEW)                       │    │
│  │                                                      │    │
│  │  store_resume()           get_resume()              │    │
│  │  store_jd()               get_analysis_result()     │    │
│  │  store_analysis_result()  list_interview_sessions()│    │
│  │  store_interview_session()                          │    │
│  └────────────────────┬────────────────────────────────┘    │
│                       │                                      │
│  ┌─────────────────────┴────────────────────────────────┐    │
│  │          Database Layer                             │    │
│  │  (Motor - Async MongoDB Driver)                     │    │
│  └────────────────────┬────────────────────────────────┘    │
└─────────────────────────┬─────────────────────────────────────┘
                          │ Async Queries
                          ↓
        ┌─────────────────────────────────────┐
        │      MongoDB Instance                │
        │  (Local or Atlas)                    │
        │                                      │
        │  Collections:                        │
        │  - resumes                           │
        │  - job_descriptions                  │
        │  - analysis_results                  │
        │  - interview_sessions                │
        │  - users (existing)                  │
        │                                      │
        │  Indexes: Automatic (on startup)     │
        └─────────────────────────────────────┘
```

## Data Flow: Resume Upload & Analysis

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│  1. USER UPLOADS RESUME                                          │
│  ┌──────────────────────┐                                        │
│  │ Frontend             │                                        │
│  │ - Select PDF file    │                                        │
│  │ - Click "Upload"     │                                        │
│  └────────────┬─────────┘                                        │
│               │ POST /resume/upload (multipart/form-data)        │
│               ↓                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Backend                                                  │   │
│  │ 1. Save file to disk (uploads/)                          │   │
│  │ 2. Extract text via pdfplumber                           │   │
│  │ 3. Parse sections (skills, experience)                   │   │
│  │ 4. Normalize skills with ONET                            │   │
│  │ 5. Categorize skills (Backend, Frontend, etc)            │   │
│  └────────────┬─────────────────────────────────────────────┘   │
│               │                                                  │
│  ┌────────────┴────────────────────────────────────────────┐    │
│  │ 6. StorageService.store_resume()                        │    │
│  │    - filename: "resume_user123_john_doe.pdf"            │    │
│  │    - extracted_text: "John Doe..."                       │    │
│  │    - skills: ["Python", "JavaScript"]                   │    │
│  │    - categories: {"Backend": [...]}                     │    │
│  └────────────┬────────────────────────────────────────────┘    │
│               │                                                  │
│  ┌────────────┴────────────────────────────────────────────┐    │
│  │ MongoDB.insert_one(resumes, document)                   │    │
│  │ Returns: ObjectId("507f1f77bcf86cd799439011")           │    │
│  └────────────┬────────────────────────────────────────────┘    │
│               │ resume_id                                       │
│               ↓                                                  │
│  ┌──────────────────────┐                                        │
│  │ Frontend             │                                        │
│  │ - Store resume_id    │                                        │
│  │ - Show success       │                                        │
│  │ - Extracted skills   │                                        │
│  └──────────────────────┘                                        │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│  2. USER PROVIDES JOB DESCRIPTION                                │
│  ┌──────────────────────┐                                        │
│  │ Frontend             │                                        │
│  │ - Select JD file OR  │                                        │
│  │ - Enter text         │                                        │
│  │ - Click "Analyze"    │                                        │
│  └────────────┬─────────┘                                        │
│               │ POST /resume/analyze                             │
│               │ - resume: (file)                                 │
│               │ - job_description_text: (text)                   │
│               │ - user_id: "user123"                             │
│               ↓                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Backend                                                  │   │
│  │ 1. Parse JD text                                         │   │
│  │ 2. Extract/normalize JD skills                           │   │
│  │ 3. Categorize JD skills                                  │   │
│  └────────────┬─────────────────────────────────────────────┘   │
│               │                                                  │
│  ┌────────────┴────────────────────────────────────────────┐    │
│  │ StorageService.store_jd()                               │    │
│  │ - title: "Senior Python Developer"                      │    │
│  │ - company: "TechCorp"                                   │    │
│  │ - skills: ["Python", "Django", "PostgreSQL"]            │    │
│  └────────────┬────────────────────────────────────────────┘    │
│               │ jd_id                                            │
│               ↓                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Backend (continued)                                      │   │
│  │ 1. Skill overlap score                                   │   │
│  │ 2. Category overlap score                                │   │
│  │ 3. TF-IDF similarity score                               │   │
│  │ 4. Semantic similarity score (embeddings)                │   │
│  │ 5. Compute weighted final score                          │   │
│  │ 6. Classify missing skills (critical, moderate, optional)│   │
│  │ 7. Generate learning plan recommendations                │   │
│  │ 8. Simulate skill improvement scenarios                  │   │
│  └────────────┬─────────────────────────────────────────────┘   │
│               │                                                  │
│  ┌────────────┴────────────────────────────────────────────┐    │
│  │ StorageService.store_analysis_result()                  │    │
│  │ - resume_id: ObjectId(...)                              │    │
│  │ - jd_id: ObjectId(...)                                  │    │
│  │ - final_readiness_score: 0.79                           │    │
│  │ - matched_skills: ["Python"]                            │    │
│  │ - missing_skills: ["Django", "PostgreSQL"]              │    │
│  │ - critical_missing: ["Django"]                          │    │
│  │ - learning_plan: [...]                                  │    │
│  └────────────┬────────────────────────────────────────────┘    │
│               │                                                  │
│  ┌────────────┴────────────────────────────────────────────┐    │
│  │ MongoDB.insert_one(analysis_results, document)          │    │
│  │ Returns: ObjectId("507f1f77bcf86cd799439022")           │    │
│  └────────────┬────────────────────────────────────────────┘    │
│               │ analysis_id + full analysis result              │
│               ↓                                                  │
│  ┌──────────────────────────────────┐                           │
│  │ Frontend                          │                           │
│  │ - Display matching score: 79%     │                           │
│  │ - Show matched skills             │                           │
│  │ - List critical gaps              │                           │
│  │ - Display learning plan           │                           │
│  │ - Show improvement simulations     │                           │
│  └──────────────────────────────────┘                           │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow: Interview Session

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│  1. USER STARTS INTERVIEW                                        │
│  ┌──────────────────────┐                                        │
│  │ Frontend             │                                        │
│  │ - Select role        │                                        │
│  │ - Click "Start"      │                                        │
│  └────────────┬─────────┘                                        │
│               │ POST /interview/start/role                       │
│               │ {role: "Python Developer", user_id: "user123"}   │
│               ↓                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Backend                                                  │   │
│  │ 1. Generate session_id                                   │   │
│  │ 2. Create session in memory                              │   │
│  │ 3. Generate first question                               │   │
│  └────────────┬─────────────────────────────────────────────┘   │
│               │                                                  │
│  ┌────────────┴────────────────────────────────────────────┐    │
│  │ StorageService.store_interview_session()                │    │
│  │ - session_id: "sess_abc123"                             │    │
│  │ - interview_type: "role"                                │    │
│  │ - role: "Python Developer"                              │    │
│  │ - status: "in_progress"                                 │    │
│  │ - created_at: now()                                     │    │
│  └────────────┬────────────────────────────────────────────┘    │
│               │                                                  │
│  ┌────────────┴────────────────────────────────────────────┐    │
│  │ MongoDB.insert_one(interview_sessions, document)        │    │
│  │ Returns: ObjectId("507f1f77bcf86cd799439033")           │    │
│  └────────────┬────────────────────────────────────────────┘    │
│               │ mongo_id + session data                         │
│               ↓                                                  │
│  ┌──────────────────────────────────────┐                       │
│  │ Frontend                              │                       │
│  │ - Store session_id                    │                       │
│  │ - Display first question              │                       │
│  │ - Ready for user input                │                       │
│  └──────────────────────────────────────┘                       │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│  2. USER SUBMITS ANSWER                                          │
│  ┌──────────────────────┐                                        │
│  │ Frontend             │                                        │
│  │ - Type answer        │                                        │
│  │ - Click "Submit"     │                                        │
│  └────────────┬─────────┘                                        │
│               │ POST /interview/answer                           │
│               │ {session_id: "sess_abc123", answer: "..."}      │
│               ↓                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Backend                                                  │   │
│  │ 1. Retrieve session from memory                          │   │
│  │ 2. Evaluate answer (Gemini or heuristic)                 │   │
│  │ 3. Generate feedback & next question                     │   │
│  │ 4. Update session state                                  │   │
│  └────────────┬─────────────────────────────────────────────┘   │
│               │                                                  │
│  ┌────────────┴────────────────────────────────────────────┐    │
│  │ StorageService.update_interview_session()               │    │
│  │ - session_id: "sess_abc123"                             │    │
│  │ - questions_asked: 1                                    │    │
│  │ - transcript: [{question, answer, evaluation}]          │    │
│  │ - current_question: (new question)                      │    │
│  │ - last_answer: (user's answer)                          │    │
│  └────────────┬────────────────────────────────────────────┘    │
│               │                                                  │
│  ┌────────────┴────────────────────────────────────────────┐    │
│  │ MongoDB.update_one(interview_sessions, {_id, fields})   │    │
│  │ Document updated with new transcript entry              │    │
│  └────────────┬────────────────────────────────────────────┘    │
│               │ updated session                                 │
│               ↓                                                  │
│  ┌──────────────────────────────────────┐                       │
│  │ Frontend                              │                       │
│  │ - Show feedback                       │                       │
│  │ - Display next question               │                       │
│  │ - Update progress (1/6 answered)      │                       │
│  └──────────────────────────────────────┘                       │
│                                                                   │
│  [Repeat steps 2 until max_questions reached]                    │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│  3. USER ENDS INTERVIEW                                          │
│  ┌──────────────────────┐                                        │
│  │ Frontend             │                                        │
│  │ - Click "End"        │                                        │
│  └────────────┬─────────┘                                        │
│               │ POST /interview/end                              │
│               │ {session_id: "sess_abc123"}                     │
│               ↓                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Backend                                                  │   │
│  │ 1. Generate final report                                 │   │
│  │ 2. Calculate overall score                               │   │
│  │ 3. Build recommendations                                 │   │
│  └────────────┬─────────────────────────────────────────────┘   │
│               │                                                  │
│  ┌────────────┴────────────────────────────────────────────┐    │
│  │ StorageService.mark_interview_completed()               │    │
│  │ - session_id: "sess_abc123"                             │    │
│  │ - status: "completed"                                   │    │
│  │ - is_finished: true                                     │    │
│  │ - final_report: {...}                                   │    │
│  │ - completed_at: now()                                   │    │
│  └────────────┬────────────────────────────────────────────┘    │
│               │                                                  │
│  ┌────────────┴────────────────────────────────────────────┐    │
│  │ MongoDB.update_one(interview_sessions, {fields})        │    │
│  │ Document marked as completed with report                │    │
│  └────────────┬────────────────────────────────────────────┘    │
│               │ final session data                              │
│               ↓                                                  │
│  ┌──────────────────────────────────────┐                       │
│  │ Frontend                              │                       │
│  │ - Display final report                │                       │
│  │ - Show overall score                  │                       │
│  │ - Strengths & weaknesses              │                       │
│  │ - Recommendations                     │                       │
│  │ - Option to save/export               │                       │
│  └──────────────────────────────────────┘                       │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## MongoDB Collections Relationships

```
                    ┌─────────────────────┐
                    │       Users         │
                    │                     │
                    │ _id (ObjectId)      │
                    │ email               │
                    │ ...                 │
                    └────────┬────────────┘
                             │
                    ┌────────┴───────────┐
                    │                    │
                    ↓                    ↓
        ┌─────────────────────┐  ┌─────────────────────┐
        │      Resumes        │  │ Job Descriptions    │
        │                     │  │                     │
        │ _id (ObjectId)      │  │ _id (ObjectId)      │
        │ user_id ───────┐    │  │ user_id ────────┐   │
        │ skills []      │    │  │ skills []       │   │
        │ extracted_text │    │  │ description_text│   │
        │ ...            │    │  │ ...             │   │
        └────────┬───────────┘  └─────────┬────────────┘
                 │                        │
                 │                        │
                 └────────┬───────────────┘
                          │
                          ↓
            ┌─────────────────────────────┐
            │   Analysis Results          │
            │                             │
            │ _id (ObjectId)              │
            │ user_id                     │
            │ resume_id → Resumes._id     │
            │ jd_id → JobDescriptions._id │
            │ matched_skills []           │
            │ missing_skills []           │
            │ final_readiness_score       │
            │ ...                         │
            └─────────────────────────────┘

        ┌──────────────────────────────────┐
        │   Interview Sessions             │
        │                                  │
        │ _id (ObjectId)                   │
        │ session_id (unique)              │
        │ user_id                          │
        │ resume_id → Resumes._id (opt)    │
        │ interview_type                   │
        │ transcript []                    │
        │ status                           │
        │ final_report                     │
        │ ...                              │
        └──────────────────────────────────┘
```

## Query Patterns

```
1. Get User's Resumes
   db.resumes.find({user_id: "user123"}).sort({uploaded_at: -1})
   Index Used: (user_id, uploaded_at)

2. Get Analysis Results for Resume
   db.analysis_results.find({resume_id: ObjectId(...)})
   Index Used: resume_id

3. Get Interview Sessions by Status
   db.interview_sessions.find({
     user_id: "user123",
     status: "completed"
   }).sort({created_at: -1})
   Index Used: (user_id, created_at)

4. Get High-Scoring Analyses
   db.analysis_results.find({
     user_id: "user123",
     final_readiness_score: {$gt: 0.8}
   })
   Index Used: (user_id, analyzed_at)

5. Find Sessions by Date Range
   db.interview_sessions.find({
     user_id: "user123",
     created_at: {$gte: ISODate("2024-01-01")}
   }).sort({created_at: -1})
   Index Used: (user_id, created_at)
```

## Async Operation Flow

```
┌─────────────────┐
│  HTTP Request   │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────┐
│  FastAPI Route Handler          │
│  (async def)                    │
└────────┬────────────────────────┘
         │
         ↓
┌─────────────────────────────────┐
│  StorageService Method          │
│  (async/await)                  │
└────────┬────────────────────────┘
         │
         ↓
┌─────────────────────────────────┐
│  Motor AsyncIOMotorClient       │
│  (Non-blocking connection)      │
└────────┬────────────────────────┘
         │
         ↓
┌─────────────────────────────────┐
│  MongoDB Query                  │
│  (Executed on DB server)        │
└────────┬────────────────────────┘
         │
         ↓
┌─────────────────────────────────┐
│  Result (ObjectId or Dict)      │
└────────┬────────────────────────┘
         │
         ↓
┌─────────────────────────────────┐
│  Response Serialization         │
│  (ObjectId → string)            │
└────────┬────────────────────────┘
         │
         ↓
┌─────────────────────────────────┐
│  JSON Response                  │
│  (200/400/404/500)              │
└─────────────────────────────────┘
```

## Collection Size Growth (Estimated)

```
Timeline: 1 Month of Usage

Week 1:
├─ 50 resumes uploaded: ~25-50 MB
├─ 100 JD entries: ~5-10 MB
├─ 150 analysis results: ~2-3 MB
└─ 200 interview sessions: ~10-15 MB
   Total: ~42-78 MB

Week 2-4 (assuming 3x growth):
└─ Total: ~126-234 MB (after 1 month)

Storage Optimization:
├─ Archive old resumes quarterly
├─ Delete analysis results older than 1 year
├─ Compress interview transcripts if needed
└─ Monitor with MongoDB Atlas metrics
```

---

This architecture ensures:
✅ Scalability with proper indexing
✅ Performance with async operations
✅ Data integrity with linked references
✅ Flexibility for future enhancements
✅ Easy querying and filtering
