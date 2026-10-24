import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  Mic,
  MicOff,
  Send,
  Menu,
  X,
  Volume2,
  VolumeX,
  ChevronLeft,
  ChevronRight,
  Clock,
  Zap,
} from "lucide-react";
import { useInterview } from "../../context/InterviewContext";
import { interviewApi } from "../../services/interviewApi";
import { Button, Card, ChatBubble, LoadingSpinner, Badge, Divider } from "../../components/interview";
import ProgressBar from "../../components/interview/ProgressBar";
import TranscriptPanel from "../../components/interview/TranscriptPanel";

const InterviewSession = () => {
  const navigate = useNavigate();
  const { session, setSessionData, setErrorMessage, error } = useInterview();

  const [answer, setAnswer] = useState("");
  const [currentTranscript, setCurrentTranscript] = useState("");
  const [loading, setLoading] = useState(false);
  const [showTranscript, setShowTranscript] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [conversationHistory, setConversationHistory] = useState([]);

  const recognitionRef = useRef(null);
  const chatEndRef = useRef(null);
  const messageCountRef = useRef(0);

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>No active session</p>
      </div>
    );
  }

  useEffect(() => {
    if (session.mode !== "voice") return;

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech Recognition not supported");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    let finalTranscript = "";

    recognition.onstart = () => {
      setIsListening(true);
      finalTranscript = "";
    };

    recognition.onresult = (event) => {
      let interimTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;

        if (event.results[i].isFinal) {
          finalTranscript += transcript + " ";
        } else {
          interimTranscript += transcript;
        }
      }

      setAnswer(finalTranscript + interimTranscript);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.onerror = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
  }, [session.mode]);

  const startRecording = () => {
    if (recognitionRef.current && !isListening) {
      recognitionRef.current.start();
    }
  };

  const stopRecording = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversationHistory]);

  // Initialize AI first question in conversation
  useEffect(() => {
    if (session?.current_question && messageCountRef.current === 0) {
      setConversationHistory([
        {
          type: "ai",
          content: session.current_question,
          timestamp: new Date(),
        },
      ]);
      messageCountRef.current = 1;
      if (session.mode === "voice" && soundEnabled) {
        speak(session.current_question);
      }
    }
  }, [session?.current_question, session?.mode, soundEnabled]);

  const speak = (text) => {
    if (!text || !soundEnabled) return;
    speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    speechSynthesis.speak(utterance);
  };

  const handleSubmitAnswer = async () => {
    if (!answer.trim()) {
      setErrorMessage("Please provide an answer");
      return;
    }

    setLoading(true);
    setErrorMessage(null);

    // Add user message to conversation history
    setConversationHistory((prev) => [
      ...prev,
      {
        type: "user",
        content: answer,
        timestamp: new Date(),
      },
    ]);

    try {
      setIsThinking(true);
      const response = await interviewApi.submitAnswer(session.session_id, answer);
      setSessionData(response.session);

      // Add AI response
      setConversationHistory((prev) => [
        ...prev,
        {
          type: "ai",
          content: response.session.current_question,
          timestamp: new Date(),
        },
      ]);

      setAnswer("");
      setCurrentTranscript("");

      if (session.mode === "voice" && soundEnabled) {
        speak(response.session.current_question);
      }
    } catch (err) {
      setErrorMessage(err.message);
    } finally {
      setLoading(false);
      setIsThinking(false);
    }
  };

  const handleEndInterview = async () => {
    if (window.confirm("Are you sure you want to end the interview?")) {
      setLoading(true);
      setErrorMessage(null);

      try {
        const response = await interviewApi.endInterview(session.session_id);
        setSessionData(response.session);

        if (session.mode === "voice" && soundEnabled) {
          speak("Interview ended. Thank you!");
        }

        navigate("/interview/report");
      } catch (err) {
        setErrorMessage(err.message);
      } finally {
        setLoading(false);
      }
    }
  };

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-white">
        <LoadingSpinner message="Loading session..." />
      </div>
    );
  }

  const progressPercentage = (session.questions_asked / session.max_questions) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-50 flex flex-col">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-gray-100 shadow-soft"
      >
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Badge variant="primary">
                Question {session.questions_asked} of {session.max_questions}
              </Badge>
              <Badge variant={session.status === "ongoing" ? "success" : "warning"}>
                {session.status.charAt(0).toUpperCase() + session.status.slice(1)}
              </Badge>
            </div>

            <div className="flex items-center gap-4">
              {session.mode === "voice" && (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setSoundEnabled(!soundEnabled)}
                  className={`p-2 rounded-lg transition ${
                    soundEnabled
                      ? "bg-primary-100 text-primary-600"
                      : "bg-gray-100 text-gray-600"
                  }`}
                >
                  {soundEnabled ? <Volume2 size={20} /> : <VolumeX size={20} />}
                </motion.button>
              )}

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowTranscript(!showTranscript)}
                className="px-3 py-2 rounded-lg bg-gray-100 text-gray-700 text-sm font-medium hover:bg-gray-200 transition"
              >
                {showTranscript ? "Hide Transcript" : "Show Transcript"}
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleEndInterview}
                disabled={loading}
                className="px-4 py-2 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 transition font-medium disabled:opacity-50"
              >
                End
              </motion.button>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="flex items-center gap-2">
            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${progressPercentage}%` }}
                transition={{ duration: 0.6, ease: "easeOut" }}
                className="h-full bg-gradient-to-r from-primary-600 to-primary-400"
              />
            </div>
            <span className="text-sm font-medium text-gray-600">
              {Math.round(progressPercentage)}%
            </span>
          </div>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto px-4 py-6">
            <div className="max-w-3xl mx-auto space-y-4">
              <AnimatePresence>
                {conversationHistory.map((msg, index) => (
                  <ChatBubble
                    key={index}
                    message={msg.content}
                    sender={msg.type}
                    timestamp={msg.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  />
                ))}
              </AnimatePresence>

              {/* Thinking indicator */}
              {isThinking && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  className="flex justify-start mb-4"
                >
                  <div className="bg-gray-100 px-4 py-3 rounded-2xl rounded-bl-none">
                    <div className="flex gap-1">
                      {[0, 1, 2].map((i) => (
                        <motion.div
                          key={i}
                          animate={{ y: [0, -8, 0] }}
                          transition={{
                            duration: 0.6,
                            delay: i * 0.1,
                            repeat: Infinity,
                          }}
                          className="w-2 h-2 rounded-full bg-gray-400"
                        />
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Voice mode indicators */}
              {session.mode === "voice" && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex gap-2 justify-center text-sm"
                >
                  {isSpeaking && (
                    <Badge variant="info">
                      <Zap size={14} />
                      AI Speaking
                    </Badge>
                  )}
                  {isListening && (
                    <Badge variant="success">
                      <Mic size={14} />
                      Listening
                    </Badge>
                  )}
                </motion.div>
              )}

              <div ref={chatEndRef} />
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mx-4 mb-4 p-3 bg-red-50 border border-red-300 text-red-700 rounded-lg text-sm flex justify-between items-center"
            >
              <span>{error}</span>
              <button
                onClick={() => setErrorMessage(null)}
                className="text-red-600 hover:text-red-700"
              >
                <X size={18} />
              </button>
            </motion.div>
          )}

          {/* Answer Input Area */}
          <div className="border-t border-gray-100 bg-white/50 backdrop-blur-sm p-4">
            <div className="max-w-3xl mx-auto">
              {session.mode === "voice" ? (
                // Voice Mode
                <div className="space-y-4">
                  {/* Transcription Display */}
                  {(answer || currentTranscript) && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="p-3 bg-primary-50 border border-primary-200 rounded-lg"
                    >
                      <p className="text-xs font-medium text-primary-600 mb-1">
                        Your Response
                      </p>
                      <p className="text-sm text-gray-900">
                        {answer || currentTranscript}
                      </p>
                    </motion.div>
                  )}

                  {/* Mic Button */}
                  <div className="flex flex-col items-center gap-4">
                    {/* Animated Mic Button */}
                    <motion.button
                      onClick={isListening ? stopRecording : startRecording}
                      disabled={loading || isSpeaking}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className={`relative w-20 h-20 rounded-full flex items-center justify-center transition ${
                        isListening
                          ? "bg-red-500 text-white shadow-lg shadow-red-500/50"
                          : "bg-gradient-to-br from-primary-600 to-primary-500 text-white hover:shadow-lg"
                      }`}
                    >
                      {isListening && (
                        <motion.div
                          animate={{ scale: [1, 1.2, 1] }}
                          transition={{
                            duration: 0.6,
                            repeat: Infinity,
                          }}
                          className="absolute inset-0 rounded-full border-4 border-red-400 opacity-30"
                        />
                      )}
                      {isListening ? (
                        <MicOff size={32} />
                      ) : (
                        <Mic size={32} />
                      )}
                    </motion.button>

                    <div className="text-center">
                      <p className="text-sm font-medium text-gray-900">
                        {isListening ? "Stop Recording" : "Start Speaking"}
                      </p>
                      {answer && (
                        <Button
                          onClick={handleSubmitAnswer}
                          disabled={loading}
                          loading={loading}
                          size="sm"
                          className="mt-3"
                        >
                          <Send size={16} />
                          Send Response
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                // Text Mode
                <div className="space-y-3">
                  <div className="relative">
                    <textarea
                      value={answer}
                      onChange={(e) => setAnswer(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === "Enter" && e.ctrlKey && !loading) {
                          handleSubmitAnswer();
                        }
                      }}
                      placeholder="Type your answer here... (Ctrl+Enter to submit)"
                      disabled={loading}
                      rows={3}
                      className="input-base w-full resize-none disabled:opacity-60"
                    />
                  </div>
                  <div className="flex gap-2 justify-between">
                    <p className="text-xs text-gray-500">
                      Tip: Press Ctrl+Enter to submit
                    </p>
                    <Button
                      onClick={handleSubmitAnswer}
                      disabled={loading || !answer.trim()}
                      loading={loading}
                      size="sm"
                      icon={Send}
                    >
                      Submit Answer
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Transcript Sidebar */}
        <AnimatePresence>
          {showTranscript && (
            <motion.div
              initial={{ opacity: 0, x: 300, width: 0 }}
              animate={{
                opacity: 1,
                x: 0,
                width: "auto",
              }}
              exit={{ opacity: 0, x: 300, width: 0 }}
              transition={{ duration: 0.3 }}
              className="w-96 border-l border-gray-100 bg-white/80 backdrop-blur-sm overflow-hidden"
            >
              <div className="h-full overflow-y-auto p-4">
                <h3 className="text-lg font-bold text-gray-900 mb-4 sticky top-0 bg-white pb-2">
                  Interview Transcript
                </h3>
                <TranscriptPanel transcript={session.transcript} />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default InterviewSession;