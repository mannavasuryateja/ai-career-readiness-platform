import React from 'react';
import { motion } from 'framer-motion';

const ProgressRing = ({
  percentage = 0,
  size = 120,
  strokeWidth = 8,
  color = '#4f97ff',
  children,
  label,
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative inline-flex items-center justify-center">
        <svg width={size} height={size} className="transform -rotate-90">
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#e5e7eb"
            strokeWidth={strokeWidth}
            fill="none"
          />
          {/* Progress circle */}
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={strokeWidth}
            fill="none"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            strokeLinecap="round"
          />
        </svg>
        {children && (
          <div className="absolute flex flex-col items-center">
            {children}
          </div>
        )}
      </div>
      {label && <p className="text-sm font-medium text-gray-700">{label}</p>}
    </div>
  );
};

export default ProgressRing;
