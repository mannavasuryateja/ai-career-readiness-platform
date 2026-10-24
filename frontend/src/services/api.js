/**
 * Unified API Service
 * Central export for all APIs
 */

export { interviewApi } from "./interviewApi";
export { resumeApi } from "./resumeApi";

export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Get current JWT auth headers
 */
export const getAuthHeaders = () => {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

/**
 * Health check - Verify backend is running
 */
export const healthCheck = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      throw new Error("Backend health check failed");
    }
    return response.json();
  } catch (error) {
    console.error("Health check error:", error);
    throw error;
  }
};

/**
 * Get API documentation URL
 */
export const getApiDocs = () => {
  return `${API_BASE_URL}/docs`;
};

/**
 * Generic API call wrapper with auth support
 */
export const apiCall = async (endpoint, options = {}) => {
  const defaultOptions = {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
      ...(options.headers || {}),
    },
    ...options,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, defaultOptions);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `API call failed: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error at ${endpoint}:`, error);
    throw error;
  }
};