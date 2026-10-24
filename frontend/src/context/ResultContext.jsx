import { createContext, useState } from "react";

export const ResultContext = createContext();

export const ResultProvider = ({ children }) => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const clearResult = () => {
    setResult(null);
    setError(null);
  };

  const value = {
    result,
    setResult,
    loading,
    setLoading,
    error,
    setError,
    clearResult,
  };

  return (
    <ResultContext.Provider value={value}>
      {children}
    </ResultContext.Provider>
  );
};

// Custom hook to use result context
export const useResult = () => {
  const context = React.useContext(ResultContext);
  if (!context) {
    throw new Error("useResult must be used within ResultProvider");
  }
  return context;
};
