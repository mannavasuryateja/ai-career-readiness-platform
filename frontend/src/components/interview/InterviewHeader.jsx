import React from "react";

const InterviewHeader = ({ session }) => {
  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 mb-8">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            {session.interview_type === "role"
              ? `${session.role} Interview`
              : "Resume Interview"}
          </h1>
          <p className="text-gray-600 mb-3">
            Interview Type:{" "}
            <span className="font-semibold capitalize">
              {session.interview_type}
            </span>
          </p>
          {session.interview_type === "role" ? (
            <p className="text-gray-600">
              Role: <span className="font-semibold">{session.role}</span>
            </p>
          ) : (
            <>
              <p className="text-gray-600 mb-2">
                Resume: <span className="font-semibold">{session.resume_filename}</span>
              </p>
              <p className="text-sm text-gray-600">
                Mode: <span className="font-semibold capitalize">{session.mode}</span>
              </p>
            </>
          )}
        </div>
        <div className="text-right">
          <p className="text-sm font-medium text-gray-600 uppercase tracking-wide mb-2">
            Status
          </p>
          <p
            className={`text-lg font-bold capitalize ${
              session.status === "completed"
                ? "text-green-600"
                : "text-blue-600"
            }`}
          >
            {session.status}
          </p>
        </div>
      </div>
    </div>
  );
};

export default InterviewHeader;
