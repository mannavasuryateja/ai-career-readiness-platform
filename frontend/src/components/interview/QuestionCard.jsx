import React from "react";

const QuestionCard = ({ question }) => {
  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
      <p className="text-sm font-medium text-gray-600 uppercase tracking-wide mb-3">
        Current Question
      </p>
      <p className="text-2xl font-semibold text-gray-900 leading-relaxed">
        {question}
      </p>
    </div>
  );
};

export default QuestionCard;
