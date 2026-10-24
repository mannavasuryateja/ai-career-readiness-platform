import React from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

const Badge = ({ children, variant = 'primary', size = 'md', icon: Icon, className }) => {
  const variants = {
    primary: 'bg-primary-100 text-primary-700',
    success: 'bg-green-100 text-green-700',
    warning: 'bg-yellow-100 text-yellow-700',
    danger: 'bg-red-100 text-red-700',
    gray: 'bg-gray-100 text-gray-700',
  };

  const sizes = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  return (
    <motion.span
      initial={{ scale: 0.5, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.3 }}
      className={clsx(
        'inline-flex items-center gap-1.5 rounded-full font-medium',
        variants[variant],
        sizes[size],
        className
      )}
    >
      {Icon && <Icon size={16} />}
      {children}
    </motion.span>
  );
};

export default Badge;
