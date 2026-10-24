import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Briefcase, FileText, Mic, MessageSquare } from "lucide-react";
import { useInterview } from "../../context/InterviewContext";
import { interviewApi } from "../../services/interviewApi";
import { Button, SelectionCard, Input, TextArea, Toggle, Card, Divider } from "../../components/interview";

const InterviewSetup = () => {
  const navigate = useNavigate();
  const { setSessionData, setErrorMessage } = useInterview();

  const [interviewType, setInterviewType] = useState(null);
  const [role, setRole] = useState("");
  const [resumeFile, setResumeFile] = useState(null);
  const [resumeSummary, setResumeSummary] = useState("");
  const [mode, setMode] = useState("text");
  const [loading, setLoading] = useState(false);
  const [localError, setLocalError] = useState(null);

  const handleStartRoleInterview = async () => {
    if (!role.trim()) {
      setLocalError("Please enter a role");
      return;
    }

    setLoading(true);
    setLocalError(null);

    try {
      const response = await interviewApi.startRoleInterview(role, mode);
      setSessionData(response.session);
      navigate("/interview/session");
    } catch (err) {
      setLocalError(err.message);
      setErrorMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStartResumeInterview = async () => {
    if (!resumeFile) {
      setLocalError("Please select a resume file");
      return;
    }

    if (!resumeSummary.trim()) {
      setLocalError("Please provide a resume summary");
      return;
    }

    setLoading(true);
    setLocalError(null);

    try {
      const response = await interviewApi.startResumeInterview(
        resumeFile,
        resumeSummary,
        mode
      );
      setSessionData(response.session);
      navigate("/interview/session");
    } catch (err) {
      setLocalError(err.message);
      setErrorMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-50 flex items-center justify-center p-4 overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{ 
            y: [0, 20, 0],
            opacity: [0.1, 0.2, 0.1]
          }}
          transition={{ duration: 8, repeat: Infinity }}
          className="absolute -top-40 -right-40 w-80 h-80 bg-primary-300 rounded-full blur-3xl"
        />
        <motion.div
          animate={{ 
            y: [0, -20, 0],
            opacity: [0.1, 0.2, 0.1]
          }}
          transition={{ duration: 10, repeat: Infinity }}
          className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-300 rounded-full blur-3xl"
        />
      </div>

      <div className="relative z-10 w-full max-w-4xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <h1 className="text-5xl font-bold text-gradient mb-3">AI Interview Platform</h1>
          <p className="text-xl text-gray-600">
            Prepare for your interview with AI-powered coaching
          </p>
        </motion.div>

        {/* Error message */}
        {localError && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-red-50 border border-red-300 text-red-700 rounded-lg flex items-center gap-2"
          >
            <span className="text-xl">⚠️</span>
            {localError}
          </motion.div>
        )}

        {/* Interview Type Selection */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Choose Your Interview Type
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <SelectionCard
                icon={Briefcase}
                title="Role-Based Interview"
                description="Prepare for a specific job role with targeted questions"
                selected={interviewType === "role"}
                onClick={() => {
                  setInterviewType("role");
                  setLocalError(null);
                }}
              />

              <SelectionCard
                icon={FileText}
                title="Resume-Based Interview"
                description="Get interview questions based on your resume"
                selected={interviewType === "resume"}
                onClick={() => {
                  setInterviewType("resume");
                  setLocalError(null);
                }}
              />
            </div>
          </div>

          {/* Content based on interview type */}
          {interviewType === "role" && (
            <motion.div
              key="role-form"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              className="mb-8"
            >
              <Card>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Job Role Details
                </h3>

                <Input
                  label="Position Title"
                  placeholder="e.g., Senior Software Engineer, Product Manager"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  icon={Briefcase}
                  containerClassName="mb-4"
                />

                <p className="text-sm text-gray-600">
                  💡 Be specific - the AI will generate questions tailored to this role
                </p>
              </Card>
            </motion.div>
          )}

          {interviewType === "resume" && (
            <motion.div
              key="resume-form"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              className="mb-8"
            >
              <Card>
                <h3 className="text-lg font-semibold text-gray-900 mb-6">
                  Resume Details
                </h3>

                {/* File Upload */}
                <div className="mb-6">
                  <label className="block text-sm font-semibold text-gray-700 mb-3">
                    Upload Resume
                  </label>
                  <div className="border-2 border-dashed border-primary-300 rounded-lg p-6 text-center hover:border-primary-500 transition cursor-pointer"
                    onClick={() => document.getElementById('resume-input').click()}
                  >
                    <FileText className="w-12 h-12 text-primary-400 mx-auto mb-2" />
                    <p className="text-sm font-medium text-gray-700 mb-1">
                      Click to upload or drag and drop
                    </p>
                    <p className="text-xs text-gray-500">
                      PDF, DOC, DOCX, or TXT (max 10MB)
                    </p>
                    {resumeFile && (
                      <p className="text-sm text-green-600 font-medium mt-3">
                        ✅ {resumeFile.name}
                      </p>
                    )}
                  </div>
                  <input
                    id="resume-input"
                    type="file"
                    onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                    accept=".pdf,.doc,.docx,.txt"
                    className="hidden"
                  />
                </div>

                {/* Resume Summary */}
                <TextArea
                  label="Professional Background"
                  placeholder="Share a brief summary of your professional experience, key skills, and recent achievements..."
                  value={resumeSummary}
                  onChange={(e) => setResumeSummary(e.target.value)}
                  rows={5}
                  containerClassName="mb-4"
                />

                <p className="text-sm text-gray-600">
                  💡 The AI will analyze your resume and background to generate relevant interview questions
                </p>
              </Card>
            </motion.div>
          )}

          {/* Mode Selection */}
          {interviewType && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              className="mb-8"
            >
              <Card>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Interview Mode
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Text Mode */}
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setMode("text")}
                    className={`p-4 rounded-lg border-2 transition ${
                      mode === "text"
                        ? "border-primary-500 bg-primary-50"
                        : "border-gray-300 hover:border-primary-300"
                    }`}
                  >
                    <MessageSquare className={`w-8 h-8 mx-auto mb-2 ${
                      mode === "text" ? "text-primary-600" : "text-gray-400"
                    }`} />
                    <p className="font-semibold text-gray-900 mb-1">Text Mode</p>
                    <p className="text-sm text-gray-600">Type your answers</p>
                  </motion.button>

                  {/* Voice Mode */}
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setMode("voice")}
                    className={`p-4 rounded-lg border-2 transition ${
                      mode === "voice"
                        ? "border-primary-500 bg-primary-50"
                        : "border-gray-300 hover:border-primary-300"
                    }`}
                  >
                    <Mic className={`w-8 h-8 mx-auto mb-2 ${
                      mode === "voice" ? "text-primary-600" : "text-gray-400"
                    }`} />
                    <p className="font-semibold text-gray-900 mb-1">Voice Mode</p>
                    <p className="text-sm text-gray-600">Speak your answers</p>
                  </motion.button>
                </div>

                <Divider label="Recommended" className="my-4" />

                <div className="flex items-start gap-3 text-sm text-gray-700">
                  <span className="text-lg">🎯</span>
                  <div>
                    <p className="font-medium">
                      {mode === "voice" ? "Voice Mode" : "Text Mode"} is selected
                    </p>
                    <p className="text-gray-600">
                      {mode === "voice"
                        ? "Great for practicing speaking and presentation skills"
                        : "Perfect for organizing thoughts and detailed responses"
                      }
                    </p>
                  </div>
                </div>
              </Card>
            </motion.div>
          )}

          {/* Start Button */}
          {interviewType === "role" && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.2 }}
            >
              <Button
                variant="primary"
                size="lg"
                onClick={handleStartRoleInterview}
                disabled={loading || !role.trim()}
                loading={loading}
                className="w-full"
              >
                Start Interview
              </Button>
            </motion.div>
          )}

          {interviewType === "resume" && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.2 }}
            >
              <Button
                variant="primary"
                size="lg"
                onClick={handleStartResumeInterview}
                disabled={loading || !resumeFile || !resumeSummary.trim()}
                loading={loading}
                className="w-full"
              >
                Start Interview
              </Button>
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default InterviewSetup;