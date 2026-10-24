# AI Career Platform - Merged Frontend

This is the unified frontend combining:
- **AI Interview Platform** (interview UI and flows)
- **Resume Analyzer** (resume analysis and recommendations UI)

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Development Server
```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

### 3. Build for Production
```bash
npm build
```

## Features

### Interview Module (`/interview`)
- Role-based interviews
- Resume-based interviews
- Real-time question generation
- AI-powered answer evaluation
- Performance reports

### Resume Analysis Module (`/`)
- Resume upload and parsing
- Job description matching
- Skill gap analysis
- Learning recommendations
- Progress simulation

## Page Structure

```
pages/
├── interview/
│   ├── InterviewSetup.jsx    - Interview configuration
│   ├── InterviewSession.jsx  - Interview Q&A
│   └── InterviewReport.jsx   - Results and feedback
└── resume/
    ├── Home.jsx             - Landing page
    ├── Upload.jsx           - File upload
    ├── Dashboard.jsx        - Analysis results
    ├── Recommendations.jsx  - Learning recommendations
    └── Simulation.jsx       - Skill improvement simulation
```

## Component Structure

```
components/
├── shared/
│   └── Navigation.jsx    - Navigation between sections
├── interview/
│   ├── AnswerInput.jsx
│   ├── QuestionDisplay.jsx
│   ├── InterviewHeader.jsx
│   └── ScoreBreakdown.jsx
└── resume/
    ├── UploadForm.jsx
    ├── SkillMatcher.jsx
    ├── LearningPlan.jsx
    └── SimulationChart.jsx
```

## Context & State Management

### Interview Context (`InterviewContext.jsx`)
- Session data
- Loading states
- Error handling
- Interview state management

### Result Context (`ResultContext.jsx`)
- Analysis results
- Score data
- Learning recommendations
- Resume data

## API Integration

API calls are made to the backend at `http://localhost:8000`:

```javascript
// Interview endpoints
/interview/start/role
/interview/start/resume
/interview/answer
/interview/end
/interview/report/{session_id}

// Resume endpoints
/resume/analyze
/resume/upload
```

## Development Notes

1. **Styling**: Using Tailwind CSS with custom components
2. **Navigation**: React Router v7 for page routing
3. **Icons**: Lucide React for UI icons
4. **Notifications**: Sonner for toast messages
5. **Animations**: Framer Motion for smooth transitions
6. **Charts**: Recharts for data visualization

## Important Notes

1. **File Structure**: Still need to copy page and component files from original projects. See MIGRATION_GUIDE.md
2. **API URLs**: Backend should be running on `http://localhost:8000`
3. **Environment**: Uses Vite for development
4. **Build Target**: Modern browsers (ES2020+)

## See Also

- [MIGRATION_GUIDE.md](../MIGRATION_GUIDE.md) - Complete migration instructions
- [Backend README](../backend/README.md) - Backend setup instructions
