import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle, Copy, Check } from "lucide-react";
import { useState } from "react";

const TranscriptPanel = ({ transcript }) => {
  const [copiedIndex, setCopiedIndex] = useState(null);

  const handleCopy = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-3 max-h-screen overflow-y-auto pr-2"
    >
      {transcript && transcript.length > 0 ? (
        <AnimatePresence>
          {transcript.map((item, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              transition={{ duration: 0.2, delay: index * 0.05 }}
              className="card-base p-3 hover:shadow-medium transition"
            >
              {/* Question */}
              <div className="flex items-start gap-2 mb-2">
                <div className="w-5 h-5 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs font-bold text-primary-600">Q</span>
                </div>
                <div className="flex-1">
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                    Question {index + 1}
                  </p>
                  <p className="text-sm font-medium text-gray-900">
                    {item.question}
                  </p>
                </div>
              </div>

              {/* Answer */}
              <div className="flex items-start gap-2 ml-8">
                <div className="w-5 h-5 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <CheckCircle className="w-3 h-3 text-green-600" />
                </div>
                <div className="flex-1">
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                    Your Answer
                  </p>
                  <p className="text-sm text-gray-700 bg-gray-50 p-2 rounded leading-relaxed">
                    {item.answer}
                  </p>
                </div>
              </div>

              {/* Copy Button */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => handleCopy(`Q: ${item.question}\nA: ${item.answer}`, index)}
                className="mt-2 ml-8 text-xs text-gray-500 hover:text-primary-600 flex items-center gap-1 transition"
              >
                {copiedIndex === index ? (
                  <>
                    <Check size={14} />
                    Copied
                  </>
                ) : (
                  <>
                    <Copy size={14} />
                    Copy
                  </>
                )}
              </motion.button>
            </motion.div>
          ))}
        </AnimatePresence>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-8"
        >
          <p className="text-gray-500 text-sm">
            No transcript yet. Start answering questions to see your responses here.
          </p>
        </motion.div>
      )}
    </motion.div>
  );
};

export default TranscriptPanel;

