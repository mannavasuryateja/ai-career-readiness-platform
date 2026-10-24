import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  CheckCircle,
  AlertCircle,
  Lightbulb,
  TrendingUp,
  Download,
  Share2,
  RotateCcw,
  Trophy,
  Target,
  MessageCircle,
  BarChart3,
  Zap,
} from "lucide-react";
import { useInterview } from "../../context/InterviewContext";
import { Button, Badge, Card, ProgressRing, Divider } from "../../components/interview";

const InterviewReport = () => {
  const navigate = useNavigate();
  const { session, clearSession } = useInterview();
  const [expandedSection, setExpandedSection] = useState("performance");

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-white">
        <Card>
          <p className="text-gray-600">No session data available</p>
          <Button onClick={() => navigate("/interview")} className="mt-4">
            Start New Interview
          </Button>
        </Card>
      </div>
    );
  }

  const report = session.final_report || {};
  const averageScore = report.average_score || 0;
  const totalScore = report.total_score || 0;

  const handleStartNew = () => {
    clearSession();
    navigate("/interview");
  };

  // Determine readiness level and color
  const getReadinessConfig = (score) => {
    if (score >= 85) return { label: "Excellent", color: "success", icon: Trophy };
    if (score >= 70) return { label: "Good", color: "info", icon: TrendingUp };
    if (score >= 55) return { label: "Fair", color: "warning", icon: AlertCircle };
    return { label: "Needs Work", color: "error", icon: AlertCircle };
  };

  const readinessConfig = getReadinessConfig(averageScore);
  const ReadinessIcon = readinessConfig.icon;

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 },
    },
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-50 p-4">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-6xl mx-auto"
      >
        {/* Header */}
        <div className="mb-8">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="flex items-center justify-between gap-4 flex-wrap"
          >
            <div>
              <h1 className="text-5xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                <motion.div
                  animate={{ rotate: [0, 10, -10, 0] }}
                  transition={{ duration: 0.6, delay: 0.3 }}
                >
                  🎉
                </motion.div>
                Interview Complete!
              </h1>
              <p className="text-lg text-gray-600">
                Here's your comprehensive performance report
              </p>
            </div>

            <div className="flex gap-2">
              <Button variant="secondary" size="sm" icon={Download}>
                Download
              </Button>
              <Button variant="secondary" size="sm" icon={Share2}>
                Share
              </Button>
            </div>
          </motion.div>
        </div>

        {/* Performance Summary - Score Cards */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8"
        >
          {/* Average Score */}
          <motion.div variants={itemVariants}>
            <Card hover={true}>
              <div className="text-center">
                <p className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3">
                  Average Score
                </p>
                <motion.p
                  initial={{ opacity: 0, scale: 0.5 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5, delay: 0.3 }}
                  className="text-4xl font-bold text-gradient mb-2"
                >
                  {Math.round(averageScore)}
                </motion.p>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${averageScore}%` }}
                    transition={{ duration: 1, delay: 0.4 }}
                    className="h-full bg-gradient-to-r from-primary-600 to-primary-400 rounded-full"
                  />
                </div>
              </div>
            </Card>
          </motion.div>

          {/* Total Score */}
          <motion.div variants={itemVariants}>
            <Card hover={true}>
              <div className="text-center">
                <p className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3">
                  Total Score
                </p>
                <motion.p
                  initial={{ opacity: 0, scale: 0.5 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5, delay: 0.4 }}
                  className="text-4xl font-bold text-gray-900"
                >
                  {Math.round(totalScore)}
                </motion.p>
                <p className="text-xs text-gray-500 mt-2">
                  Points earned
                </p>
              </div>
            </Card>
          </motion.div>

          {/* Questions */}
          <motion.div variants={itemVariants}>
            <Card hover={true}>
              <div className="text-center">
                <BarChart3 className="w-8 h-8 text-primary-600 mx-auto mb-2" />
                <p className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3">
                  Questions Asked
                </p>
                <p className="text-4xl font-bold text-gray-900">
                  {report.questions_asked || session.questions_asked}
                </p>
              </div>
            </Card>
          </motion.div>

          {/* Readiness Level */}
          <motion.div variants={itemVariants}>
            <Card
              hover={true}
              className={getReadinessBgClass(readinessConfig.color)}
            >
              <div className="text-center">
                <ReadinessIcon className="w-8 h-8 mx-auto mb-2" />
                <p className="text-sm font-semibold uppercase tracking-wide mb-2">
                  Readiness Level
                </p>
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.5 }}
                  className="text-2xl font-bold"
                >
                  <Badge variant={readinessConfig.color}>
                    {readinessConfig.label}
                  </Badge>
                </motion.p>
              </div>
            </Card>
          </motion.div>
        </motion.div>

        {/* Main Content - Strengths, Weaknesses, Recommendations */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Strengths */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card className="h-full">
              <div className="flex items-center gap-2 mb-4">
                <CheckCircle className="w-6 h-6 text-green-600" />
                <h3 className="text-lg font-bold text-gray-900">Strengths</h3>
              </div>

              {report.strengths && report.strengths.length > 0 ? (
                <div className="space-y-3">
                  {report.strengths.map((strength, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.4 + index * 0.1 }}
                      className="flex gap-2 p-3 bg-green-50 rounded-lg"
                    >
                      <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                      <p className="text-sm text-gray-700">{strength}</p>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500 italic">
                  No strengths identified yet
                </p>
              )}
            </Card>
          </motion.div>

          {/* Weaknesses */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Card className="h-full">
              <div className="flex items-center gap-2 mb-4">
                <AlertCircle className="w-6 h-6 text-yellow-600" />
                <h3 className="text-lg font-bold text-gray-900">Areas for Improvement</h3>
              </div>

              {report.weaknesses && report.weaknesses.length > 0 ? (
                <div className="space-y-3">
                  {report.weaknesses.map((weakness, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.5 + index * 0.1 }}
                      className="flex gap-2 p-3 bg-yellow-50 rounded-lg"
                    >
                      <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0" />
                      <p className="text-sm text-gray-700">{weakness}</p>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500 italic">
                  No weaknesses identified
                </p>
              )}
            </Card>
          </motion.div>

          {/* Recommendations */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <Card className="h-full">
              <div className="flex items-center gap-2 mb-4">
                <Lightbulb className="w-6 h-6 text-blue-600" />
                <h3 className="text-lg font-bold text-gray-900">Recommendations</h3>
              </div>

              {report.recommendations && report.recommendations.length > 0 ? (
                <div className="space-y-3">
                  {report.recommendations.map((rec, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.6 + index * 0.1 }}
                      className="flex gap-2 p-3 bg-blue-50 rounded-lg"
                    >
                      <Lightbulb className="w-5 h-5 text-blue-600 flex-shrink-0" />
                      <p className="text-sm text-gray-700">{rec}</p>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500 italic">
                  No recommendations available
                </p>
              )}
            </Card>
          </motion.div>
        </div>

        {/* Transcript Section */}
        {session.transcript && session.transcript.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
          >
            <Card>
              <div className="flex items-center gap-2 mb-6">
                <MessageCircle className="w-6 h-6 text-primary-600" />
                <h3 className="text-xl font-bold text-gray-900">
                  Interview Transcript
                </h3>
              </div>

              <div className="space-y-4 max-h-96 overflow-y-auto">
                {session.transcript.map((item, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.7 + index * 0.05 }}
                    className="border-l-4 border-primary-400 pl-4 py-2"
                  >
                    <p className="text-xs font-semibold text-primary-600 uppercase mb-1">
                      Question {index + 1}
                    </p>
                    <p className="text-sm font-medium text-gray-900 mb-2">
                      {item.question}
                    </p>
                    <p className="text-sm text-gray-700 bg-gray-50 p-2 rounded">
                      {item.answer}
                    </p>
                  </motion.div>
                ))}
              </div>
            </Card>
          </motion.div>
        )}

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.7 }}
          className="flex gap-4 justify-center mt-8"
        >
          <Button
            variant="ghost"
            size="lg"
            onClick={handleStartNew}
            icon={RotateCcw}
          >
            Start New Interview
          </Button>
          <Button
            variant="primary"
            size="lg"
            onClick={() => navigate("/interview")}
            icon={Zap}
          >
            Back to Home
          </Button>
        </motion.div>
      </motion.div>
    </div>
  );
};

// Helper function for readiness bg color
const getReadinessBgClass = (color) => {
  const colors = {
    success: "bg-green-50",
    info: "bg-blue-50",
    warning: "bg-yellow-50",
    error: "bg-red-50",
  };
  return colors[color] || colors.success;
};

export default InterviewReport;