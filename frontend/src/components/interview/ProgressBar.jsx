import React from "react";

const ProgressBar = ({ current, max }) => {
  const percentage = (current / max) * 100;

  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 mb-8">
      <div className="flex justify-between items-center mb-3">
        <p className="text-sm font-medium text-gray-700 uppercase tracking-wide">
          Interview Progress
        </p>
        <p className="text-sm font-semibold text-gray-600">
          Question {current} of {max}
        </p>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div
          className="bg-indigo-600 h-full transition-all duration-300 ease-out"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <p className="text-xs text-gray-500 mt-2">
        {Math.round(percentage)}% complete
      </p>
    </div>
  );
};

export default ProgressBar;
