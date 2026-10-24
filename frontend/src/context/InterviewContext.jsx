import React, { createContext, useState, useCallback } from "react";

export const InterviewContext = createContext();

export const InterviewProvider = ({ children }) => {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const setSessionData = useCallback((data) => {
    setSession(data);
    setError(null);
  }, []);

  const setErrorMessage = useCallback((message) => {
    setError(message);
  }, []);

  const setLoadingState = useCallback((state) => {
    setLoading(state);
  }, []);

  const clearSession = useCallback(() => {
    setSession(null);
    setError(null);
  }, []);

  const value = {
    session,
    setSessionData,
    loading,
    setLoadingState,
    error,
    setErrorMessage,
    clearSession,
  };

  return (
    <InterviewContext.Provider value={value}>
      {children}
    </InterviewContext.Provider>
  );
};

// Custom hook to use interview context
export const useInterview = () => {
  const context = React.useContext(InterviewContext);
  if (!context) {
    throw new Error("useInterview must be used within InterviewProvider");
  }
  return context;
};
