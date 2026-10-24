import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const getHeaders = (extraHeaders = {}) => {
  const token = localStorage.getItem("token");
  return {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extraHeaders,
  };
};

/**
 * Resume API Service
 */
export const resumeApi = {
  // Analyze resume against job description
  analyzeResume: async (
    resumeFile,
    jobDescriptionFile = null,
    jobDescriptionText = null
  ) => {
    const formData = new FormData();
    formData.append("resume", resumeFile);

    if (jobDescriptionFile) {
      formData.append("job_description_file", jobDescriptionFile);
    }

    if (jobDescriptionText) {
      formData.append("job_description_text", jobDescriptionText);
    }

    try {
      const response = await axios.post(
        `${API_BASE_URL}/resume/analyze`,
        formData,
        {
          headers: getHeaders({
            "Content-Type": "multipart/form-data",
          }),
        }
      );

      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.detail || "Failed to analyze resume"
      );
    }
  },

  // Upload resume
  uploadResume: async (resumeFile) => {
    const formData = new FormData();
    formData.append("file", resumeFile);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/resume/upload`,
        formData,
        {
          headers: getHeaders({
            "Content-Type": "multipart/form-data",
          }),
        }
      );

      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.detail || "Failed to upload resume"
      );
    }
  },

  // Get user's saved resumes
  getUserResumes: async (limit = 20) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/resume/resumes?limit=${limit}`, {
        headers: getHeaders(),
      });
      return response.data?.resumes || [];
    } catch (error) {
      throw new Error(error.response?.data?.detail || "Failed to fetch resumes");
    }
  },

  // Get past analysis results
  getAnalysisResults: async (limit = 20) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/resume/analysis-results?limit=${limit}`, {
        headers: getHeaders(),
      });
      return response.data?.analysis_results || [];
    } catch (error) {
      throw new Error(error.response?.data?.detail || "Failed to fetch analysis history");
    }
  },

  // Get single analysis result
  getAnalysisResultById: async (analysisId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/resume/analysis-results/${analysisId}`, {
        headers: getHeaders(),
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || "Failed to fetch analysis details");
    }
  },

  // Generate tailored cover letter
  createCoverLetter: async ({ analysisId, targetRole, companyName, resumeText, jdText, matchedSkills }) => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/resume/cover-letter`,
        {
          analysis_id: analysisId,
          target_role: targetRole,
          company_name: companyName,
          resume_text: resumeText,
          jd_text: jdText,
          matched_skills: matchedSkills || [],
        },
        {
          headers: getHeaders({
            "Content-Type": "application/json",
          }),
        }
      );
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || "Failed to generate cover letter");
    }
  },

  // Delete resume
  deleteResume: async (resumeId) => {
    try {
      const response = await axios.delete(`${API_BASE_URL}/resume/resumes/${resumeId}`, {
        headers: getHeaders(),
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || "Failed to delete resume");
    }
  },

  // Delete analysis result
  deleteAnalysisResult: async (analysisId) => {
    try {
      const response = await axios.delete(`${API_BASE_URL}/resume/analysis-results/${analysisId}`, {
        headers: getHeaders(),
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || "Failed to delete analysis result");
    }
  },
};