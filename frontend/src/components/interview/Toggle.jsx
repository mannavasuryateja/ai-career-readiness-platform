import React from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

const Toggle = ({
  checked = false,
  onChange,
  label,
  description,
  disabled = false,
  leftLabel = 'Off',
  rightLabel = 'On',
  className,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={clsx('flex items-center justify-between', className)}
    >
      <div className="flex flex-col gap-1">
        {label && <label className="text-sm font-semibold text-gray-700">{label}</label>}
        {description && <p className="text-xs text-gray-500">{description}</p>}
      </div>

      <motion.button
        onClick={() => !disabled && onChange(!checked)}
        disabled={disabled}
        className={clsx(
          'relative inline-flex h-8 w-14 items-center rounded-full transition-colors',
          checked ? 'bg-primary-600' : 'bg-gray-300',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        <motion.div
          layout
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
          className={clsx(
            'inline-block h-6 w-6 transform rounded-full bg-white shadow-md',
            checked ? 'translate-x-7' : 'translate-x-1'
          )}
        />
      </motion.button>
    </motion.div>
  );
};

export default Toggle;
