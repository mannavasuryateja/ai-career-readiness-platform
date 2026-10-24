import React from "react";

const AnswerInput = ({
  answer,
  onChange,
  onSubmit,
  loading,
  isPlaceholder,
}) => {
  const handleKeyPress = (e) => {
    if (e.key === "Enter" && e.ctrlKey && !loading && !isPlaceholder) {
      onSubmit();
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
      <label className="block text-sm font-medium text-gray-700 uppercase tracking-wide mb-4">
        Your Answer
      </label>
      <textarea
        value={answer}
        onChange={(e) => onChange(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Type your answer here... (Ctrl+Enter to submit)"
        rows="6"
        disabled={isPlaceholder || loading}
        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none disabled:bg-gray-100 disabled:cursor-not-allowed"
      />
      <p className="text-xs text-gray-500 mt-2">
        Tip: Press Ctrl+Enter to quickly submit your answer
      </p>

      {!isPlaceholder && (
        <button
          onClick={onSubmit}
          disabled={loading || !answer.trim()}
          className="mt-4 w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold py-3 rounded-lg transition"
        >
          {loading ? "Submitting..." : "Submit Answer"}
        </button>
      )}
    </div>
  );
};

export default AnswerInput;
