# Project Architecture

## Project Overview

**An Explainable AI-Based Career Readiness Platform with LLM-Assisted Technical Interview Evaluation**

A comprehensive full-stack application that combines resume analysis, skill matching, learning roadmaps, and AI-powered technical interview evaluation. The platform uses Large Language Models (LLMs) to provide explainable recommendations for career readiness and technical interview preparation.

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + Vite)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Pages: Auth | Resume Analysis | Interview Session  │   │
│  │ Components: Shared, Resume, Interview UI            │   │
│  │ Context: Auth | Interview | Result State Management │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                    REST API Endpoints
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI/Python)                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Routes: /auth | /interview | /resume                │   │
│  │ Services: Interview | Resume Management             │   │
│  │ Core: Database | Security | Session Store           │   │
│  │ Models: Schemas & Data Models                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
        ┌─────▼────┐   ┌─────▼────┐   ┌─────▼────┐
        │ Database │   │   LLM    │   │  O*NET   │
        │ (SQLite  │   │ (Gemini) │   │  Data    │
        │  or SQL) │   │          │   │ (Skills) │
        └──────────┘   └──────────┘   └──────────┘
```

---

## Frontend Architecture (React + Vite)

### Directory Structure
```
src/
├── components/
│   ├── interview/          # Interview-specific UI components
│   │   ├── AnswerInput.jsx
│   │   ├── ChatBubble.jsx
│   │   ├── InterviewHeader.jsx
│   │   ├── QuestionCard.jsx
│   │   └── ... (UI components)
│   ├── resume/             # Resume analysis UI components
│   │   ├── FileUpload.jsx
│   │   ├── ExplanationCard.jsx
│   │   ├── ScoreBreakdown.jsx
│   │   ├── RecommendationCard.jsx
│   │   └── ... (Resume-specific UI)
│   └── shared/             # Shared UI components
│       └── Navigation.jsx
├── pages/
│   ├── auth/               # Authentication pages
│   │   ├── LoginPage.jsx
│   │   ├── RegisterPage.jsx
│   │   └── ProfilePage.jsx
│   ├── interview/          # Interview pages
│   │   ├── InterviewSession.jsx
│   │   └── InterviewReport.jsx
│   └── resume/             # Resume analysis pages
├── context/                # Global state management
│   ├── AuthContext.jsx     # User authentication state
│   ├── InterviewContext.jsx# Interview session state
│   └── ResultContext.jsx   # Results state
├── services/               # API client services
│   ├── api.js              # Base API configuration
│   ├── interviewApi.js     # Interview endpoints
│   └── resumeApi.js        # Resume endpoints
└── App.jsx                 # Root component

```

### Frontend Data Flow
1. **Authentication**: AuthContext manages user login/registration
2. **Resume Analysis**: FileUpload → resumeApi → ResultContext
3. **Interview Session**: InterviewContext manages question flow and answers
4. **Results Display**: ResultContext provides data to pages

### State Management
- **AuthContext**: User authentication, tokens, profile
- **InterviewContext**: Current question, answers, session progress
- **ResultContext**: Analysis results, scores, recommendations

---

## Backend Architecture (FastAPI/Python)

### Directory Structure
```
app/
├── main.py                 # FastAPI application entry point
├── core/
│   ├── database.py         # Database configuration & connection
│   ├── security.py         # JWT, password hashing, auth logic
│   └── session_store.py    # Interview session management
├── models/
│   ├── auth_schemas.py     # Authentication request/response schemas
│   └── schemas.py          # General data models
├── routes/
│   ├── auth.py             # /auth endpoints (login, register, profile)
│   ├── interview.py        # /interview endpoints (start, answer, evaluate)
│   └── resume.py           # /resume endpoints (upload, analyze)
└── services/
    ├── interview/          # Interview management services
    │   ├── interview_manager.py      # Interview workflow
    │   ├── question_generator.py     # Generate questions
    │   ├── question_llm_service.py   # LLM-based question generation
    │   ├── evaluator.py              # Answer evaluation logic
    │   ├── evaluation_llm_service.py # LLM-based evaluation
    │   ├── llm_service.py            # LLM API integration
    │   └── resume_parser.py          # Parse resume data
    └── resume/             # Resume analysis services
        ├── parser.py                 # Resume parsing (PDF/text)
        ├── evaluation.py             # Resume evaluation logic
        ├── matching.py               # Job description matching
        ├── weighted_scoring.py       # Scoring algorithm
        ├── explainability.py         # Generate explanations
        ├── learning_roadmap.py       # Generate learning recommendations
        ├── recommendations.py        # Career recommendations
        ├── gemini_service.py         # Gemini LLM integration
        ├── youtube_service.py        # YouTube learning resource fetch
        ├── onet_skills.py            # O*NET skill database
        ├── onet_categories.py        # O*NET category data
        ├── config.py                 # Resume service configuration
        ├── utils.py                  # Utility functions
        └── simulate_engine.py        # Simulation for analysis
```

### Core Layers

#### 1. **Routes Layer** (`/routes`)
- Handles HTTP requests/responses
- Routes:
  - **Auth Routes** (`/auth`): Login, register, refresh token, get profile
  - **Interview Routes** (`/interview`): Start session, submit answer, get evaluation
  - **Resume Routes** (`/resume`): Upload, parse, analyze, get recommendations

#### 2. **Services Layer** (`/services`)

**Interview Services:**
- `interview_manager.py`: Orchestrates interview workflow
- `question_generator.py`: Creates interview questions
- `question_llm_service.py`: Uses LLM to generate contextual questions
- `evaluator.py`: Evaluates user answers
- `evaluation_llm_service.py`: Uses LLM for answer evaluation with explanations

**Resume Services:**
- `parser.py`: Extracts data from resumes
- `evaluation.py`: Evaluates resume quality
- `matching.py`: Matches resume against job descriptions
- `weighted_scoring.py`: Calculates match scores
- `explainability.py`: Generates human-readable explanations
- `learning_roadmap.py`: Creates personalized learning paths
- `recommendations.py`: Suggests career improvements
- `gemini_service.py`: Integrates with Google Gemini LLM
- `onet_skills.py` & `onet_categories.py`: References O*NET skill database

#### 3. **Core Layer** (`/core`)
- `database.py`: Database connection and ORM setup
- `security.py`: Authentication (JWT), password hashing, authorization
- `session_store.py`: Interview session storage and retrieval

#### 4. **Models Layer** (`/models`)
- `auth_schemas.py`: Pydantic models for authentication
- `schemas.py`: General request/response schemas

---

## Data Models

### Key Entities
```
User
├── id
├── email
├── username
├── password_hash
├── profile_data
└── created_at

InterviewSession
├── id
├── user_id
├── status (in_progress, completed)
├── questions (list)
├── answers (list)
├── scores (list)
└── started_at

ResumeAnalysis
├── id
├── user_id
├── resume_text
├── parsed_data
├── job_description
├── match_score
├── recommendations (list)
└── created_at

Question
├── id
├── topic
├── difficulty
├── description
└── evaluation_criteria

Answer
├── id
├── question_id
├── response_text
├── score
├── explanation
└── submitted_at
```

---

## Technology Stack

### Frontend
- **Framework**: React 18+
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **HTTP Client**: Axios/Fetch API

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite / PostgreSQL
- **Authentication**: JWT (PyJWT)
- **LLM Integration**: Google Gemini API
- **ORM**: SQLAlchemy (likely)
- **Validation**: Pydantic

### External Services
- **LLM**: Google Gemini API (question generation, answer evaluation, recommendations)
- **Skills Data**: O*NET API / Database (job skills and categories)
- **Learning Resources**: YouTube API (learning roadmaps)

---

## Key Features & Data Flow

### 1. Resume Analysis Flow
```
User Upload Resume
        ↓
Parser extracts skills, experience, education
        ↓
Evaluation scores resume quality
        ↓
Matching compares against job description
        ↓
Weighted scoring calculates match percentage
        ↓
Explainability generates insights
        ↓
Learning roadmap suggests improvements
        ↓
Display results with explanations
```

### 2. Interview Session Flow
```
Start Interview
        ↓
Generate initial question (via LLM)
        ↓
Present question to candidate
        ↓
Candidate submits answer
        ↓
LLM evaluates answer with score & explanation
        ↓
Generate next question (adaptive or fixed)
        ↓
Repeat or end session
        ↓
Generate interview report with scores
```

### 3. Authentication Flow
```
Register/Login
        ↓
Validate credentials
        ↓
Generate JWT token
        ↓
Store token in context
        ↓
Authenticate subsequent requests
```

---

## API Endpoints

### Authentication
- `POST /auth/register` - Create new account
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh JWT token
- `GET /auth/profile` - Get user profile
- `POST /auth/logout` - User logout

### Resume Analysis
- `POST /resume/upload` - Upload and parse resume
- `POST /resume/analyze` - Analyze against job description
- `GET /resume/recommendations` - Get learning recommendations
- `GET /resume/report` - Get analysis report

### Interview
- `POST /interview/start` - Start interview session
- `GET /interview/question` - Get next question
- `POST /interview/answer` - Submit answer
- `GET /interview/report` - Get interview results
- `POST /interview/end` - End session

---

## Deployment Architecture

```
┌──────────────────┐         ┌──────────────────┐
│  Frontend Build  │         │  Backend Server  │
│  (dist/)         │         │  (Python/Uvicorn)│
│  Hosted on CDN   │ ◄─────► │  Port: 8000      │
│  or Static Host  │         │  Database        │
└──────────────────┘         └──────────────────┘
                                      │
                          ┌───────────┼───────────┐
                          │           │           │
                    ┌─────▼──┐  ┌─────▼──┐  ┌────▼───┐
                    │  DB    │  │ Gemini │  │ O*NET  │
                    │ SQLite │  │  API   │  │ Data   │
                    │ or PG  │  │        │  │        │
                    └────────┘  └────────┘  └────────┘
```

---

## Security Considerations

1. **Authentication**: JWT tokens with expiration
2. **Password Security**: Bcrypt hashing
3. **CORS**: Configure frontend/backend CORS
4. **Input Validation**: Pydantic schemas validate all inputs
5. **Session Security**: Session store with timeout
6. **API Rate Limiting**: Prevent abuse
7. **Data Encryption**: Sensitive data encryption at rest

---

## Scalability Considerations

1. **Database**: Migrate from SQLite to PostgreSQL for production
2. **Caching**: Redis for session/cache management
3. **Microservices**: Separate interview and resume services
4. **Queue System**: Celery for async LLM calls
5. **CDN**: Static assets on CDN for frontend
6. **Load Balancer**: Distribute backend requests
7. **Monitoring**: Logging and performance tracking

---

## Development Workflow

1. **Frontend Development**: `npm run dev` (Vite dev server)
2. **Backend Development**: `uvicorn app.main:app --reload` (FastAPI dev server)
3. **Database Migrations**: Alembic (if using SQLAlchemy)
4. **Testing**: PyTest (backend), Jest (frontend)
5. **API Testing**: Postman / cURL

---

## File Organization Best Practices

- **Services**: Business logic separated by domain
- **Routes**: HTTP endpoints and validation
- **Models**: Data schemas and validation
- **Core**: Cross-cutting concerns
- **Components**: Reusable UI components
- **Pages**: Full-page views
- **Context**: Global state management
- **Utils**: Helper functions

---

## Future Enhancements

1. **Real-time Collaboration**: WebSockets for live interviews
2. **Mock Interview Panels**: Video-based assessments
3. **Advanced Analytics**: Candidate performance dashboards
4. **Skill Benchmarking**: Industry-wide comparisons
5. **Personalization**: ML-based recommendation engine
6. **Multi-language Support**: Internationalization
7. **Mobile App**: React Native version
8. **Certifications**: Industry certification preparation

---

*Last Updated: April 30, 2026*
