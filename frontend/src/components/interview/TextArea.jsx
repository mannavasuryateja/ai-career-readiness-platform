import React from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

const TextArea = React.forwardRef(({
  label,
  error,
  placeholder,
  rows = 4,
  value,
  onChange,
  disabled = false,
  className,
  labelClassName,
  containerClassName,
  ...props
}, ref) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={containerClassName}
    >
      {label && (
        <label className={clsx(
          'block text-sm font-semibold text-gray-700 mb-2',
          labelClassName
        )}>
          {label}
        </label>
      )}
      <div className="relative">
        <textarea
          ref={ref}
          rows={rows}
          value={value}
          onChange={onChange}
          disabled={disabled}
          placeholder={placeholder}
          className={clsx(
            'input-base w-full rounded-lg border border-gray-300 bg-white resize-none',
            'px-4 py-3 text-base font-normal',
            error && 'border-red-500 focus:ring-red-100 focus:border-red-500',
            disabled && 'bg-gray-50 text-gray-500 cursor-not-allowed opacity-60',
            className
          )}
          {...props}
        />
      </div>
      {error && (
        <motion.p
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-1 text-sm text-red-600"
        >
          {error}
        </motion.p>
      )}
    </motion.div>
  );
});

TextArea.displayName = 'TextArea';

export default TextArea;
