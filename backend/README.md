# AI Career Platform - Merged Backend

This is the unified backend combining:
- **AI Interview Platform** (interview endpoints and services)
- **Resume Analyzer** (resume analysis endpoints and services)

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment
Create `.env` file:
```bash
GEMINI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
```

### 3. Run Backend
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

## API Routes

### Interview Endpoints
- `POST /interview/start/role` - Start role-based interview
- `POST /interview/start/resume` - Start resume-based interview
- `POST /interview/answer` - Submit interview answer
- `POST /interview/end` - End interview
- `GET /interview/report/{session_id}` - Get interview report

### Resume Endpoints
- `POST /resume/analyze` - Analyze resume against job description
- `POST /resume/upload` - Upload and extract resume data

### Health
- `GET /health` - Health check endpoint

## Project Structure

```
app/
├── main.py              # FastAPI app setup
├── models/
│   └── schemas.py       # Combined Pydantic schemas
├── routes/
│   ├── interview.py     # Interview endpoints
│   └── resume.py        # Resume endpoints
├── services/
│   ├── interview_manager.py
│   ├── interview/       # Interview services
│   │   ├── question_generator.py
│   │   ├── evaluator.py
│   │   └── ...other services...
│   └── resume/          # Resume services
│       ├── parser.py
│       ├── matching.py
│       └── ...other services...
└── core/
    └── session_store.py
```

## Important Notes

1. **File Structure**: Still need to copy service files from original projects. See MIGRATION_GUIDE.md
2. **Uploads**: Resumes are stored in `uploads/` folder
3. **Sessions**: Interview sessions are stored in memory (not persistent)
4. **API Keys**: Required for Gemini and OpenRouter services

## See Also

- [MIGRATION_GUIDE.md](../MIGRATION_GUIDE.md) - Complete migration instructions
- [Original Projects](../) - Reference old project structures
