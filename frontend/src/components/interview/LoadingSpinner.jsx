import React from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

const LoadingSpinner = ({ size = 'md', variant = 'primary', message = '' }) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  const variants = {
    primary: 'border-primary-300 border-t-primary-600',
    white: 'border-white/30 border-t-white',
    gray: 'border-gray-300 border-t-gray-600',
  };

  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        className={clsx('border-4 rounded-full', sizes[size], variants[variant])}
      />
      {message && <p className="text-gray-600 text-sm">{message}</p>}
    </div>
  );
};

export default LoadingSpinner;
