# Viva Questions and Answers - AI Career Platform

## Project Overview & Architecture

### 1. What is the AI Career Platform? Describe its main components and how they integrate.
The AI Career Platform is a unified web application combining AI-powered interview preparation and resume analysis. Main components:
- **Backend (FastAPI)**: Handles API endpoints, AI services, database operations
- **Frontend (React)**: User interface for interviews and resume uploads
- **MongoDB**: Data persistence for users, resumes, interviews, analysis results
- **AI Services**: Gemini (evaluation), OpenRouter (question generation), YouTube API (recommendations)
Integration: Frontend makes HTTP requests to backend APIs, backend stores/retrieves data from MongoDB and calls external AI APIs.

### 2. Explain the overall architecture. How does the backend communicate with the frontend?
The architecture follows a client-server model:
- **Frontend**: React SPA served by Vite dev server
- **Backend**: FastAPI REST API with async endpoints
- **Database**: MongoDB with Motor async driver
- **Communication**: HTTP/HTTPS with JSON payloads, CORS enabled for localhost origins
- **State Management**: React contexts for local state, API calls via Axios

### 3. What technologies are used in the backend? Why FastAPI, MongoDB, and Motor?
- **FastAPI**: Modern Python web framework with async support, automatic OpenAPI docs, type validation
- **MongoDB**: NoSQL document database for flexible schema, good for unstructured resume data
- **Motor**: Async MongoDB driver for non-blocking I/O, essential for FastAPI's async nature
These choices enable high performance, scalability, and easy API development.

### 4. Describe the frontend stack. Why React, Vite, and Tailwind CSS?
- **React**: Component-based UI library for reusable components and state management
- **Vite**: Fast build tool with hot reload for development
- **Tailwind CSS**: Utility-first CSS framework for rapid styling without custom CSS files
This stack provides fast development, good performance, and modern UI capabilities.

### 5. How is data persistence handled? Explain MongoDB collections and indexing strategy.
Data stored in MongoDB collections:
- `users`: User accounts with email indexes
- `resumes`: Parsed resume data with user_id and upload_date indexes  
- `job_descriptions`: JD text with user_id and creation_date indexes
- `analysis_results`: Matching scores with compound indexes for queries
- `interview_sessions`: Interview data with session_id unique index
Indexing strategy: Single field indexes for common queries, compound indexes for multi-field filtering, ensures fast lookups.

## AI Interview Module

### 6. How does the interview system work? Explain role-based vs resume-based interviews.
**Role-based**: User selects job role, system generates questions for that role using OpenRouter API
**Resume-based**: System analyzes uploaded resume, generates questions based on resume content and skills
Both create interview sessions in MongoDB, track Q&A, evaluate answers with Gemini API, store results for reports.

### 7. Describe the question generation process. What APIs are used and what happens without them?
Question generation uses OpenRouter API to call language models for creating interview questions.
- With API: Generates contextual, role-specific questions
- Without API: Falls back to predefined question templates with basic phrasing
Process: Takes role/resume context, generates 5-10 questions per session.

### 8. How are interview answers evaluated? Explain the scoring mechanism.
Answers evaluated using Gemini API for semantic analysis:
- Compares answer against expected criteria
- Scores on accuracy, completeness, relevance (0-100 scale)
- Without API: Falls back to basic keyword matching and length checks
Results stored in session data for final report generation.

### 9. What is the session management strategy? How are interviews stored and retrieved?
Sessions managed with unique session IDs, stored in MongoDB `interview_sessions` collection.
- Tracks: user_id, questions, answers, scores, timestamps, status
- Retrieved by session_id for reports or continuation
- In-memory session store as backup for quick access

### 10. Explain the interview report generation. What metrics are included?
Reports generated from completed interview sessions:
- Overall score (average of answer scores)
- Question-by-question breakdown
- Strengths and improvement areas
- Performance trends across questions
- Stored in MongoDB for historical tracking

## Resume Analysis Module

### 11. How does resume parsing work? What file formats are supported?
Supports PDF and DOCX formats:
- **PDF**: pdfplumber extracts text from all pages
- **DOCX**: python-docx reads paragraphs
- Text processed to extract sections (skills, education, experience)
- Skills normalized using O*NET database
- Parsed data stored in MongoDB

### 12. Explain skill extraction and normalization. What is O*NET and how is it used?
O*NET is US Department of Labor's occupational database with 1,000+ standardized skills.
- Skills extracted from resume text using regex patterns
- Normalized by matching against O*NET aliases (case-insensitive)
- Example: "js", "javascript" → "JavaScript"
- Enables consistent skill matching across resumes and job descriptions


### 13. Describe the job description matching algorithm. What scoring methods are used?
Multi-faceted scoring system:
- **Skill Overlap**: Exact matches between resume and JD skills
- **Category Overlap**: Matches broader skill categories  
- **TF-IDF Similarity**: Text similarity using term frequency analysis
- **Semantic Similarity**: Meaning-based comparison using sentence transformers
- **Final Score**: Weighted average (30% skill, 20% category, 25% TF-IDF, 25% semantic)

### 14. How are skill gaps identified? What recommendations are generated?
Skill gaps found by comparing JD requirements vs resume skills.
- Missing skills identified and prioritized
- Recommendations include: learning resources, courses, certifications
- YouTube tutorials fetched for gap-filling
- Personalized learning roadmap created

### 15. Explain the YouTube video recommendation system. How does it work?
Uses YouTube Data API v3 to search for educational content:
- Query: `"{skill_name} full course tutorial"`
- Returns 3 videos per skill with title, thumbnail, channel, URL
- Integrated into learning recommendations
- Helps users bridge identified skill gaps

## Technical Implementation

### 16. How is authentication implemented? What JWT configuration is used?
JWT-based authentication:
- Users register/login with email/password
- Passwords hashed with bcrypt
- JWT tokens issued with 24-hour expiration
- HS256 algorithm, configurable secret key
- Tokens validated on protected endpoints

### 17. Explain CORS configuration. Why are specific origins allowed?
CORS allows cross-origin requests from frontend to backend:
- Origins: `http://localhost:3000` (React dev), `http://localhost:5173` (Vite dev)
- Credentials enabled for cookie/auth headers
- All methods and headers allowed for API flexibility
- Prevents unauthorized cross-origin access in production

### 18. Describe the database connection lifecycle. When does it connect/disconnect?
- **Connect**: On FastAPI startup event, creates Motor client and database instance
- **Disconnect**: On shutdown event, closes client connection
- **Indexes**: Created on connect for query performance
- **Global Instance**: Single client reused across requests

### 19. How are API keys managed? What happens if they're missing?
API keys loaded from `.env` file using python-dotenv:
- GEMINI_API_KEY: For answer evaluation
- OPENROUTER_API_KEY: For question generation
- Missing keys: System logs warnings, uses fallback logic (basic scoring/templates)
- App still starts but AI features reduced

### 20. Explain the deployment setup. How would you run this in production?
- **Backend**: Gunicorn/Uvicorn with multiple workers, reverse proxy (nginx)
- **Frontend**: Build with Vite, serve static files
- **Database**: MongoDB Atlas or self-hosted cluster
- **Environment**: Docker containers, environment variables for config
- **Security**: HTTPS, proper CORS origins, secure API keys

## AI Integration & Fallbacks

### 21. What AI services are integrated? How do Gemini and OpenRouter contribute?
- **Gemini (Google)**: Answer evaluation and semantic analysis
- **OpenRouter**: Question generation using various LLMs
- **YouTube API**: Educational video recommendations
Integration via REST API calls with error handling and fallbacks.

### 22. Explain fallback mechanisms when API keys are unavailable.
- **Question Generation**: Uses predefined templates instead of AI-generated questions
- **Answer Evaluation**: Basic keyword matching and length-based scoring
- **System**: Logs warnings but continues operating with reduced functionality
- **User Experience**: Clear messaging about limited features

### 23. How does the system handle AI service failures gracefully?
- Try-catch blocks around API calls
- Timeout handling for slow responses
- Fallback to basic logic when services unavailable
- Error logging without crashing the application
- User notifications about service status

### 24. Describe any machine learning models used in the project.
- **Sentence Transformers**: For semantic similarity in resume-JD matching
- **TF-IDF Vectorizer**: For text similarity analysis
- **Scikit-learn**: For cosine similarity calculations
- **spaCy**: For potential NLP processing (imported but usage varies)

## Frontend Implementation

### 25. How is state management handled in React? Explain contexts used.
- **React Context API**: For global state management
- **AuthContext**: User authentication state and login/logout
- **InterviewContext**: Interview session data and progress
- **ResultContext**: Analysis results and recommendations
- **Local State**: useState for component-specific state

### 26. Describe the routing strategy. How are pages organized?
- **React Router v7**: Client-side routing
- **Routes**: `/` (home), `/interview/*` (interview flow), `/resume/*` (resume analysis)
- **Nested Routes**: Interview setup, session, report pages
- **Protected Routes**: Authentication checks for user-specific pages

### 27. Explain component structure. How are shared components reused?
- **Modular Components**: Button, Input, Card, etc. in `components/shared/`
- **Feature Components**: Interview and resume-specific in respective folders
- **Composition**: Higher-order components and props for customization
- **Styling**: Tailwind classes for consistent design system

### 28. How does the frontend handle API calls? What library is used?
- **Axios**: HTTP client for API requests
- **Configuration**: Base URL pointing to backend (`http://localhost:8000`)
- **Error Handling**: Try-catch with user notifications
- **Loading States**: Loading spinners during requests

### 29. Describe UI/UX considerations. How are loading states and errors handled?
- **Loading**: Skeleton components and spinners during data fetching
- **Errors**: Toast notifications (Sonner) for API failures
- **Responsive**: Tailwind responsive classes for mobile/desktop
- **Accessibility**: Semantic HTML, proper ARIA labels
- **Animations**: Framer Motion for smooth transitions

## Security & Best Practices

### 30. What security measures are implemented? Explain JWT and password hashing.
- **JWT**: Stateless authentication with expiration
- **Password Hashing**: bcrypt for secure password storage
- **CORS**: Restricted origins in production
- **Input Validation**: Pydantic schemas for API data
- **HTTPS**: Required for production deployment

### 31. How is data validation handled? What libraries are used for schemas?
- **Pydantic**: Python data validation with type hints
- **FastAPI Integration**: Automatic request/response validation
- **MongoDB Models**: Custom ObjectId type for database compatibility
- **Error Responses**: Detailed validation error messages

### 32. Explain error handling and logging strategies.
- **Logging**: Python logging module with INFO/WARNING levels
- **API Errors**: FastAPI exception handlers for 4xx/5xx responses
- **Database Errors**: Connection and query error handling
- **User Feedback**: Frontend error toasts and loading states
- **Startup Checks**: API key and database connection validation

### 33. How would you scale this application? What improvements would you suggest?
- **Horizontal Scaling**: Multiple backend instances with load balancer
- **Database**: MongoDB sharding for large datasets
- **Caching**: Redis for frequently accessed data
- **CDN**: For static frontend assets
- **Monitoring**: Application performance monitoring
- **Improvements**: Add user management, more AI models, real-time features

### 34. Additional considerations for production deployment.
- **Environment Variables**: Secure key management
- **Database Backups**: Regular MongoDB backups
- **Rate Limiting**: API rate limits to prevent abuse
- **Testing**: Unit and integration tests
- **Documentation**: API docs and user guides
- **Containerization**: Docker for consistent deployment

---

## How Resume Parsing Works

The resume parsing system extracts structured data from uploaded resume files (PDF or DOCX) and normalizes skills for analysis:

### 1. File Processing
- **PDF Files**: Uses `pdfplumber` library to extract text from all pages
- **DOCX Files**: Uses `python-docx` to read paragraphs and combine into text
- **Output**: Raw text content from the entire document

### 2. Section Extraction
- Splits text into lines and identifies sections using regex patterns:
  - **Skills**: Lines after "skills" header
  - **Education**: Lines after "education" header  
  - **Experience**: Lines after "experience" header
  - **Projects**: Lines after "projects" header
- Returns a dictionary with lists of content for each section

### 3. Skill Normalization
- Takes skill section lines and matches against O*NET database
- **O*NET Database**: Contains 1,000+ canonical skills with aliases (e.g., "JavaScript" → ["javascript", "js", "ecmascript"])
- **Matching Process**: 
  - Converts text to lowercase
  - Uses regex to find exact matches with aliases
  - Returns canonical skill names (e.g., "JavaScript" instead of "js")
- **Case-Insensitive**: Handles variations like "mongodb", "MongoDB", "mongo db"

### 4. Data Storage
- Parsed resume data stored in MongoDB `resumes` collection
- Includes: extracted text, normalized skills, metadata (upload date, user ID)
- Creates indexes for efficient querying by user and date

This process enables accurate skill matching against job descriptions and personalized recommendations.

---

## How Skills Are Given and YouTube Recommendations Are Generated

### Skill Extraction & Assignment

Skills are extracted from resumes and assigned through a multi-step process:

#### 1. Resume Skill Extraction
- During parsing, skills section is identified and extracted
- Raw skill text is normalized using O*NET database mapping
- **Example**: "js", "javascript", "ecmascript" all map to canonical "JavaScript"

#### 2. Job Description Skill Extraction  
- Similar process for job descriptions (JDs)
- Extracts required skills from JD text
- Normalizes to canonical O*NET skills

#### 3. Skill Matching & Scoring
- **Overlap Score**: Counts matching skills between resume and JD
- **Category Score**: Matches broader skill categories (e.g., "Programming Languages")
- **TF-IDF Similarity**: Compares text similarity using term frequency analysis
- **Semantic Similarity**: Uses sentence transformers to understand meaning/context
- **Final Score**: Weighted combination (30% overlap, 20% category, 25% TF-IDF, 25% semantic)

#### 4. Gap Analysis
- Identifies missing skills from JD requirements
- Calculates skill proficiency levels
- Prioritizes gaps based on job relevance

### YouTube Video Recommendations

Recommendations are generated based on identified skill gaps:

#### 1. Skill Gap Identification
- Compares resume skills vs JD requirements
- Identifies skills present in JD but missing/absent in resume

#### 2. YouTube API Integration
- Uses Google YouTube Data API v3
- **Search Query**: `"{skill_name} full course tutorial"`
- **Parameters**: 
  - `maxResults`: 3 videos per skill
  - `type`: "video" only
  - Filters for educational content

#### 3. Video Selection & Formatting
- Returns structured data for each video:
  - Title, thumbnail URL, channel name, YouTube URL
- Prioritizes official tutorials and courses
- Limits to 3 videos per skill to avoid overload

#### 4. Recommendation Delivery
- Integrated into learning roadmap
- Presented in UI with clickable links
- Helps users bridge skill gaps through self-paced learning

This system provides personalized, actionable learning paths based on actual career gaps identified through resume-JD matching.