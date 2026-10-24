const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const getAuthHeaders = (contentType = "application/json") => {
  const token = localStorage.getItem("token");
  const headers = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  if (contentType) {
    headers["Content-Type"] = contentType;
  }
  return headers;
};

const handleResponse = async (response, defaultErrorMsg) => {
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || defaultErrorMsg);
  }
  return response.json();
};

/**
 * Interview API
 */
export const interviewApi = {
  // Start role-based interview
  startRoleInterview: async (role, mode = "text", maxQuestions = 6) => {
    const response = await fetch(`${API_BASE_URL}/interview/start/role`, {
      method: "POST",
      headers: getAuthHeaders("application/json"),
      body: JSON.stringify({ role, mode, max_questions: maxQuestions }),
    });
    return handleResponse(response, "Failed to start role interview");
  },

  // Start resume-based interview
  startResumeInterview: async (
    resumeFile,
    resumeSummary = "",
    mode = "text",
    maxQuestions = 6
  ) => {
    const formData = new FormData();
    formData.append("resume_file", resumeFile);
    formData.append("resume_summary", resumeSummary);
    formData.append("mode", mode);
    formData.append("max_questions", maxQuestions);

    // When sending FormData, do not set Content-Type header manually so browser sets boundary
    const headers = getAuthHeaders(null);

    const response = await fetch(`${API_BASE_URL}/interview/start/resume`, {
      method: "POST",
      headers,
      body: formData,
    });
    return handleResponse(response, "Failed to start resume interview");
  },

  // Submit answer
  submitAnswer: async (sessionId, answer) => {
    const response = await fetch(`${API_BASE_URL}/interview/answer`, {
      method: "POST",
      headers: getAuthHeaders("application/json"),
      body: JSON.stringify({ session_id: sessionId, answer }),
    });
    return handleResponse(response, "Failed to submit answer");
  },

  // End interview
  endInterview: async (sessionId) => {
    const response = await fetch(`${API_BASE_URL}/interview/end`, {
      method: "POST",
      headers: getAuthHeaders("application/json"),
      body: JSON.stringify({ session_id: sessionId }),
    });
    return handleResponse(response, "Failed to end interview");
  },

  // Get report
  getReport: async (sessionId) => {
    const response = await fetch(
      `${API_BASE_URL}/interview/report/${sessionId}`,
      {
        headers: getAuthHeaders("application/json"),
      }
    );
    return handleResponse(response, "Failed to fetch report");
  },

  // Get user interview sessions
  getUserSessions: async (limit = 20) => {
    const response = await fetch(
      `${API_BASE_URL}/interview/sessions?limit=${limit}`,
      {
        headers: getAuthHeaders("application/json"),
      }
    );
    const data = await handleResponse(response, "Failed to fetch interview sessions");
    return data.sessions || [];
  },
};