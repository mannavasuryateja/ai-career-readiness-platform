# Project Workflow

## Overview

This document outlines the complete workflows for users, developers, and system processes in the Career Readiness Platform.

---

## Table of Contents

1. [User Workflows](#user-workflows)
2. [Technical Workflows](#technical-workflows)
3. [Data Flow Sequences](#data-flow-sequences)
4. [Developer Workflow](#developer-workflow)
5. [System Process Flows](#system-process-flows)

---

## User Workflows

### 1. User Authentication Workflow

#### Registration Flow
```
┌─ User opens app
│
├─ Clicks "Register"
│
├─ Frontend: RegisterPage displays form
│  (Email, Username, Password, Confirm Password)
│
├─ User fills form & submits
│
├─ Frontend: Validates fields locally
│  (Email format, password strength)
│
├─ Frontend: POST /auth/register
│  {email, username, password_hash}
│
├─ Backend: Validates input (Pydantic)
│
├─ Backend: Check duplicate email/username
│  (Query database)
│
├─ Backend: Hash password (Bcrypt)
│
├─ Backend: Create user record in DB
│
├─ Backend: Generate JWT token
│
├─ Frontend: Receive token → Store in AuthContext
│  (localStorage or sessionStorage)
│
├─ Frontend: Redirect to ProfilePage
│
└─ User: Account created ✓
```

#### Login Flow
```
┌─ User opens LoginPage
│
├─ Enters email & password
│
├─ Frontend: POST /auth/login
│  {email, password}
│
├─ Backend: Query user by email
│
├─ Backend: Compare password hash
│
├─ Decision: Valid credentials?
│  ├─ YES: Generate JWT → Return token
│  └─ NO: Return 401 Unauthorized
│
├─ Frontend: Store JWT in AuthContext
│
├─ Frontend: Set Authorization header for future requests
│
├─ Frontend: Redirect to Dashboard
│
└─ User: Logged in ✓
```

---

### 2. Resume Analysis Workflow

#### A. Upload & Parse Resume
```
┌─ User navigates to Resume Analysis
│
├─ Frontend: Display FileUpload component
│
├─ User selects PDF/DOCX/TXT file
│
├─ Frontend: Validation
│  ├─ File size < 10MB?
│  ├─ File type supported?
│  └─ File not empty?
│
├─ Frontend: FormData + file
│     POST /resume/upload
│     Headers: Authorization: Bearer {JWT}
│
├─ Backend: Authenticate request (JWT)
│
├─ Backend: Save file to uploads/
│
├─ Backend: Parse document
│  ├─ Extract text
│  ├─ Clean formatting
│  └─ Identify sections
│
├─ Backend: Call parser.py
│  ├─ Extract skills
│  ├─ Extract experience
│  ├─ Extract education
│  ├─ Extract contact info
│  └─ Identify gaps
│
├─ Backend: Store parsed data in DB
│     (Resume Analysis record)
│
├─ Frontend: Receive parsed resume data
│
├─ Frontend: Display in ResultContext
│
├─ Frontend: Show resume preview & extracted data
│
└─ User: Resume uploaded ✓
```

#### B. Enter Job Description & Analyze
```
┌─ Frontend: Display JDInput component
│
├─ User pastes job description
│
├─ Frontend: POST /resume/analyze
│  {
│    resume_id,
│    job_description,
│    user_id
│  }
│
├─ Backend: Retrieve resume from DB
│
├─ Backend: Call matching.py
│  ├─ Parse JD for skills/requirements
│  ├─ Extract key competencies
│  └─ Build requirement list
│
├─ Backend: Call weighted_scoring.py
│  ├─ Compare resume skills ↔ JD skills
│  ├─ Calculate match score (0-100%)
│  ├─ Identify skill gaps
│  ├─ Identify surplus skills
│  └─ Score experience relevance
│
├─ Backend: Call evaluation.py
│  ├─ Evaluate resume quality
│  ├─ Score presentation
│  ├─ Score completeness
│  └─ Generate quality score
│
├─ Backend: Call gemini_service.py
│  ├─ Generate detailed analysis
│  ├─ Create explanations
│  ├─ Identify strengths
│  └─ Identify weaknesses
│
├─ Backend: Store analysis results
│
├─ Frontend: Receive analysis
│     {
│       match_score,
│       skill_gaps,
│       strengths,
│       weaknesses,
│       explanations
│     }
│
├─ Frontend: Display ScoreCircle (match %)
│
├─ Frontend: Display SkillTags (matched/missing)
│
├─ Frontend: Display ImpactChart (score breakdown)
│
├─ Frontend: Display ExplanationCards
│
└─ User: Analysis complete ✓
```

#### C. Get Recommendations & Learning Roadmap
```
┌─ Frontend: GET /resume/recommendations
│  Headers: Authorization
│
├─ Backend: Retrieve analysis from DB
│
├─ Backend: Call learning_roadmap.py
│  ├─ Identify top 5 skill gaps
│  ├─ Query O*NET database (onet_skills.py)
│  ├─ Find related skills/categories
│  └─ Determine learning sequence
│
├─ Backend: Call recommendations.py
│  ├─ Generate career suggestions
│  ├─ Suggest certifications
│  ├─ Recommend resume improvements
│  └─ Prioritize by impact
│
├─ Backend: Call youtube_service.py
│  ├─ Search learning resources
│  ├─ Fetch top videos per skill
│  └─ Create curated playlist
│
├─ Backend: Call gemini_service.py
│  ├─ Generate detailed explanations
│  ├─ Create personalized advice
│  └─ Explain why recommendations matter
│
├─ Backend: Return:
│  {
│    roadmap: [
│      {skill, difficulty, resources, duration}
│    ],
│    recommendations: [...],
│    explanations: [...]
│  }
│
├─ Frontend: Store in ResultContext
│
├─ Frontend: Display RoadmapItem components
│
├─ Frontend: Display RecommendationCards
│
├─ Frontend: Show resource links
│
└─ User: Sees learning path ✓
```

---

### 3. Technical Interview Workflow

#### A. Start Interview Session
```
┌─ User navigates to Interview
│
├─ Frontend: Display session options
│  ├─ Select difficulty level (Easy/Medium/Hard)
│  ├─ Select topic (optional)
│  └─ Select resume (if available)
│
├─ User confirms start
│
├─ Frontend: POST /interview/start
│  {
│    difficulty,
│    topic,
│    resume_id (optional),
│    user_id
│  }
│
├─ Backend: Create InterviewSession in DB
│  {
│    id, user_id, status: "in_progress",
│    created_at, questions: [], answers: []
│  }
│
├─ Backend: Call interview_manager.py
│
├─ Backend: Call question_llm_service.py
│  ├─ If resume provided:
│  │  └─ Generate questions based on resume skills
│  ├─ Else:
│  │  └─ Generate general questions for topic
│  ├─ Create diverse question set
│  └─ Set difficulty level
│
├─ Backend: Store questions in session
│
├─ Frontend: Receive session_id & first question
│
├─ Frontend: Store in InterviewContext
│
├─ Frontend: Display InterviewSession page
│
├─ Frontend: Display QuestionCard (question #1)
│
├─ Frontend: Show ProgressBar (1/N)
│
└─ Interview: Started ✓
```

#### B. Answer Question & Get Evaluation
```
┌─ Frontend: Display AnswerInput component
│
├─ User types/speaks answer
│
├─ Frontend: User clicks "Submit"
│
├─ Frontend: Validate answer (not empty)
│
├─ Frontend: POST /interview/answer
│  {
│    session_id,
│    question_id,
│    answer_text,
│    question_number: N
│  }
│
├─ Backend: Retrieve session & question
│
├─ Backend: Call evaluator.py
│  ├─ Parse answer
│  ├─ Extract key concepts
│  └─ Prepare for LLM evaluation
│
├─ Backend: Call evaluation_llm_service.py
│  ├─ Send to Gemini API:
│  │  {
│  │    question,
│  │    answer,
│  │    difficulty,
│  │    topic,
│  │    evaluation_criteria
│  │  }
│  │
│  ├─ Gemini evaluates:
│  │  ├─ Correctness (0-100%)
│  │  ├─ Completeness
│  │  ├─ Clarity
│  │  ├─ Technical depth
│  │  └─ Communication
│  │
│  └─ Gemini generates:
│     ├─ Final score
│     ├─ Explanation
│     ├─ Strengths identified
│     └─ Areas for improvement
│
├─ Backend: Store answer + evaluation in session
│
├─ Backend: Generate next question
│  ├─ Determine difficulty:
│  │  ├─ If score > 80: Increase difficulty
│  │  ├─ If score < 50: Decrease difficulty
│  │  └─ Else: Keep same difficulty
│  │
│  └─ Call question_llm_service.py for next Q
│
├─ Frontend: Receive evaluation
│  {
│    score: 75,
│    explanation: "...",
│    feedback: {...},
│    next_question: {...}
│  }
│
├─ Frontend: Update InterviewContext
│
├─ Frontend: Display score + feedback (ChatBubble)
│
├─ Frontend: Show next question
│
├─ Frontend: Update ProgressBar (2/N)
│
└─ Answer: Evaluated ✓
```

#### C. Complete Interview & View Report
```
┌─ After N questions answered
│
├─ Frontend: Display completion message
│
├─ Frontend: POST /interview/end
│  {session_id}
│
├─ Backend: Update session status: "completed"
│
├─ Backend: Calculate aggregate scores
│  ├─ Average score across all answers
│  ├─ Score by topic
│  ├─ Score by difficulty
│  └─ Performance trend
│
├─ Backend: Call evaluation_llm_service.py
│  ├─ Generate overall assessment
│  ├─ Identify top strengths
│  ├─ Identify gaps
│  ├─ Provide improvement recommendations
│  └─ Generate personalized feedback
│
├─ Backend: Store final report in DB
│
├─ Backend: Return InterviewReport data
│
├─ Frontend: Store in ResultContext
│
├─ Frontend: Navigate to InterviewReport page
│
├─ Frontend: Display ScoreCircle (overall %)
│
├─ Frontend: Display score breakdown by topic
│
├─ Frontend: Display ScoreBreakdown chart
│
├─ Frontend: Display feedback & recommendations
│
├─ Frontend: Display TranscriptPanel (Q&A history)
│
└─ User: Interview completed ✓
```

---

## Technical Workflows

### Data Processing Pipeline

#### Resume Processing Pipeline
```
Raw Resume File (PDF/DOCX/TXT)
        ↓ (parser.py)
    Extract Text
        ↓
    Clean & Normalize
        ↓
    Segment Sections
    (Experience, Education, Skills, etc.)
        ↓
    Extract Entities
    (Companies, Dates, Skills, Technologies)
        ↓
    Skill Matching (onet_skills.py)
    (Map to O*NET skills)
        ↓
    Store Parsed Data
        ↓
    Structured Resume Object
    {
      skills: [...],
      experience: [...],
      education: [...],
      gaps: [...]
    }
```

#### Analysis Pipeline
```
Resume Data + Job Description
        ↓
    Skill Extraction (matching.py)
    ├─ Extract required skills from JD
    ├─ Extract resume skills
    └─ Cross-reference O*NET
        ↓
    Scoring (weighted_scoring.py)
    ├─ Skill match score
    ├─ Experience relevance
    ├─ Education match
    └─ Overall match percentage
        ↓
    Gap Analysis
    ├─ Missing skills
    ├─ Experience deficits
    └─ Priority ranking
        ↓
    Generate Explanations (explainability.py)
    ├─ Why score is X%
    ├─ Why specific skills matter
    └─ Why gaps are important
        ↓
    Final Analysis Object
    {
      match_score: 75,
      matched_skills: [...],
      gap_skills: [...],
      explanations: [...],
      recommendations: [...]
    }
```

#### Interview Question Generation Pipeline
```
Input: {difficulty, topic, resume_data (optional)}
        ↓
    Question Requirements (question_llm_service.py)
    ├─ Difficulty level constraints
    ├─ Topic specifications
    ├─ Avoid repeating questions
    └─ If resume: map to candidate skills
        ↓
    Prompt Engineering
    ├─ Create detailed LLM prompt
    ├─ Include evaluation criteria
    ├─ Specify answer format
    └─ Add contextual constraints
        ↓
    Call Gemini API
    (Send prompt + requirements)
        ↓
    Parse Response
    ├─ Extract question text
    ├─ Extract evaluation criteria
    ├─ Extract sample answers
    └─ Validate quality
        ↓
    Cache & Store Question
    (Avoid regenerating same Q)
        ↓
    Return Question Object
    {
      id,
      text,
      difficulty,
      topic,
      evaluation_criteria: [...]
    }
```

#### Interview Evaluation Pipeline
```
Question + Candidate Answer
        ↓
    Prepare Evaluation Context (evaluator.py)
    ├─ Extract key concepts from Q
    ├─ Parse answer for structure
    ├─ Identify major points
    └─ Prepare scoring rubric
        ↓
    Call Gemini API (evaluation_llm_service.py)
    ├─ Send: question, answer, rubric
    ├─ Request: score, feedback, explanation
    └─ Expect: structured JSON response
        ↓
    Parse Evaluation Response
    {
      score: 0-100,
      correctness: 0-100,
      completeness: 0-100,
      clarity: 0-100,
      strengths: ["..."],
      improvements: ["..."],
      explanation: "..."
    }
        ↓
    Adaptive Difficulty (interview_manager.py)
    ├─ If score > 80: Next question harder
    ├─ If score < 50: Next question easier
    └─ Else: Keep difficulty
        ↓
    Generate Next Question
    (Back to question generation pipeline)
        ↓
    Store Evaluation & Answer
    (Update session record)
        ↓
    Return Feedback to User
```

---

## Data Flow Sequences

### Sequence 1: Complete Resume Analysis

```
Actor: User | Frontend | Backend | Database | Gemini API | O*NET
────────────────────────────────────────────────────────────────

User -> Frontend: Upload resume
Frontend -> Backend: POST /resume/upload
Backend -> Database: Save file, create record
Backend -> Parser: Extract data
Parser -> Backend: {skills, exp, edu}
Backend -> Database: Store parsed resume
Backend -> Frontend: Return parsed data
Frontend -> User: Show resume preview

User -> Frontend: Enter job description
Frontend -> Backend: POST /resume/analyze
Backend -> Matcher: Extract JD + resume skills
Matcher -> O*NET: Validate/normalize skills
O*NET -> Matcher: Standard skill codes
Matcher -> Backend: {matched, missing skills}
Backend -> Scorer: Calculate scores
Scorer -> Backend: {match%, score breakdown}
Backend -> Gemini: Generate analysis
Gemini -> Backend: {explanations, insights}
Backend -> Frontend: Complete analysis
Frontend -> User: Display results
```

### Sequence 2: Interview Session Flow

```
Actor: User | Frontend | Backend | Database | Session Store | Gemini API
────────────────────────────────────────────────────────────────────────

User -> Frontend: Click "Start Interview"
Frontend -> Backend: POST /interview/start
Backend -> DB: Create session (status: in_progress)
Backend -> Session: Store session_id
Backend -> Gemini: Generate Q1
Gemini -> Backend: Question object
Backend -> Session: Store Q1
Backend -> Frontend: Return Q1
Frontend -> User: Display question

User -> Frontend: Type answer
Frontend -> Backend: POST /interview/answer
Backend -> Session: Store answer
Backend -> Gemini: Evaluate answer
Gemini -> Backend: {score, feedback}
Backend -> DB: Store evaluation
Backend -> Gemini: Generate Q2
Gemini -> Backend: Question object
Backend -> Session: Store Q2
Backend -> Frontend: Return score + Q2
Frontend -> User: Show feedback + next Q

[Repeat for each question]

User -> Frontend: Submit final answer
Frontend -> Backend: POST /interview/answer
Backend -> Gemini: Evaluate final answer
Gemini -> Backend: {score, feedback}
Backend -> DB: Store evaluation
Backend -> Gemini: Generate overall assessment
Gemini -> Backend: {report, recommendations}
Backend -> Frontend: POST /interview/end
Backend -> DB: Update session (status: completed)
Backend -> Frontend: Return final report
Frontend -> User: Display report + recommendations
```

---

## Developer Workflow

### Development Environment Setup

```
1. Clone Repository
   git clone <repo-url>
   cd project

2. Backend Setup
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt

3. Frontend Setup
   cd ../frontend
   npm install

4. Environment Configuration
   Backend: Create .env (DB_URL, GEMINI_API_KEY, JWT_SECRET)
   Frontend: Create .env (VITE_API_BASE_URL)

5. Database Initialization
   python manage.py migrate

6. Start Development Servers
   Terminal 1: cd backend && uvicorn app.main:app --reload
   Terminal 2: cd frontend && npm run dev

7. Access Application
   Frontend: http://localhost:5173
   Backend API: http://localhost:8000
   API Docs: http://localhost:8000/docs
```

### Feature Development Workflow

```
1. Create Feature Branch
   git checkout -b feature/resume-analysis

2. Backend Development
   a) Define data model (models/schemas.py)
   b) Create service logic (services/resume/*)
   c) Add route handlers (routes/resume.py)
   d) Write tests (tests/test_resume.py)
   e) Test with Postman/cURL

3. Frontend Development
   a) Create components (components/resume/*)
   b) Create pages (pages/resume/*)
   c) Add context management (context/*.jsx)
   d) Integrate API calls (services/resumeApi.js)
   e) Test in browser

4. Integration Testing
   a) Test full user workflow
   b) Test error cases
   c) Test edge cases
   d) Performance testing

5. Code Review
   git push origin feature/resume-analysis
   Create Pull Request
   Code review + approval

6. Merge & Deploy
   git merge feature/resume-analysis
   git push origin main
   Deploy to staging/production
```

### Testing Workflow

```
Backend Testing
├─ Unit Tests (pytest)
│  ├─ Service logic
│  ├─ Route handlers
│  └─ Utility functions
│
├─ Integration Tests
│  ├─ Full API endpoints
│  ├─ Database operations
│  └─ LLM service calls
│
└─ Manual Testing (Postman)
   ├─ All endpoints
   ├─ Error scenarios
   └─ Edge cases

Frontend Testing
├─ Unit Tests (Jest/Vitest)
│  ├─ Components
│  ├─ Utility functions
│  └─ Context logic
│
├─ Integration Tests
│  ├─ Page flows
│  ├─ API integration
│  └─ State management
│
└─ Manual Testing (Browser)
   ├─ User workflows
   ├─ UI/UX
   └─ Cross-browser compatibility
```

### Debugging Workflow

```
Backend Issues
1. Check logs (terminal output)
2. Add print/logging statements
3. Use pdb breakpoints
4. Check API response in Postman
5. Verify database state
6. Check Gemini API responses

Frontend Issues
1. Check browser console
2. Check Network tab (API calls)
3. Use React DevTools
4. Check Context state
5. Verify component props
6. Test API endpoints independently

Common Issues
├─ 401 Unauthorized: JWT expired/invalid
├─ 404 Not Found: Endpoint/resource not found
├─ 500 Server Error: Backend exception (check logs)
├─ CORS Error: Backend CORS config
├─ API timeout: Gemini API slow
└─ Database error: Connection/schema issue
```

---

## System Process Flows

### User Session Management Flow

```
Request Received
        ↓
Extract JWT from Authorization header
        ↓
Validate JWT signature
        ↓
Check token expiration
        ↓
Decision: Token valid?
├─ YES: Extract user_id from claims
│       ↓
│       Attach user to request context
│       ↓
│       Proceed to route handler
│
└─ NO: Return 401 Unauthorized
       (Send refresh token prompt)

Refresh Token Flow (if expired)
├─ Frontend receives 401
├─ Send refresh token
├─ Backend validates refresh token
├─ Generate new access token
├─ Return new token
├─ Frontend stores new token
└─ Retry original request
```

### Error Handling Flow

```
Error Occurs in Route Handler
        ↓
Catch Exception
        ↓
Determine Error Type
├─ Validation Error (400)
├─ Authentication Error (401)
├─ Authorization Error (403)
├─ Not Found (404)
├─ Conflict (409)
├─ Rate Limited (429)
└─ Server Error (500)
        ↓
Generate Error Response
{
  error_code: "...",
  message: "...",
  details: {...}
}
        ↓
Log Error
├─ Error type
├─ Stack trace
├─ User context
└─ Timestamp
        ↓
Return HTTP Response
├─ Status code
├─ Error JSON
└─ CORS headers
        ↓
Frontend: Receive error
        ↓
Display User-Friendly Message
├─ Show notification
├─ Suggest action
└─ Offer support contact
```

### Database Transaction Flow

```
Start Transaction
        ↓
Operation 1: Create user
        ↓
Operation 2: Create profile
        ↓
Operation 3: Create default settings
        ↓
All Successful?
├─ YES: Commit transaction
│       ├─ All changes saved
│       ├─ Release locks
│       └─ Return success
│
└─ NO: Rollback transaction
       ├─ Undo all changes
       ├─ Release locks
       ├─ Log error
       └─ Return error to user
```

### Async LLM Call Flow

```
User Request
        ↓
Backend receives request
        ↓
Queue LLM task (if async)
        ↓
Return job_id to user
        ↓
LLM Worker Process
├─ Dequeue task
├─ Call Gemini API
├─ Handle timeout/error
├─ Store result
└─ Update status
        ↓
Frontend polls for result
        ↓
Result ready?
├─ YES: Fetch result
│       └─ Display to user
│
└─ NO: Continue polling
       (with backoff)
```

---

## Performance Optimization Workflows

### Caching Strategy

```
Frequently Accessed Data
├─ Parsed O*NET skills (Redis)
├─ Generated questions (Memory + DB)
├─ User profiles (Redis, 1 hour TTL)
└─ Analysis results (DB + Browser localStorage)

Cache Invalidation
├─ Resume updated → Clear resume cache
├─ Skills updated → Invalidate O*NET cache
├─ Questions generated → Store new set
└─ User profile edited → Clear profile cache
```

### Database Query Optimization

```
Resume Analysis Query
├─ Use indexes on user_id, resume_id
├─ Eager load relations (skills, recommendations)
├─ Paginate large result sets
└─ Cache frequently accessed queries

Session Management Query
├─ Index on session_id
├─ Batch store answers (don't update per answer)
├─ Archive old sessions
└─ Optimize JSON storage
```

---

## Workflow Summary Table

| Workflow | Actors | Key Steps | Duration | Status |
|----------|--------|-----------|----------|--------|
| User Registration | User, Frontend, Backend | Form → Validate → Hash → Store → Token | 2-3s | Common |
| Resume Upload & Parse | User, Frontend, Backend, Parser | Upload → Save → Parse → Extract → Store | 5-10s | Common |
| Resume Analysis | User, Frontend, Backend, Gemini, O*NET | Analyze → Score → Gap Analysis → Explain | 10-15s | Common |
| Interview Start | User, Frontend, Backend, Gemini | Create Session → Generate Q → Present | 5-8s | Frequent |
| Answer Evaluation | User, Frontend, Backend, Gemini | Submit → Evaluate → Score → Feedback | 8-12s | Frequent |
| Learning Roadmap | Frontend, Backend, Gemini, YouTube | Generate Path → Fetch Resources → Explain | 10-20s | Occasional |

---

*Last Updated: April 30, 2026*
