import React from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

const Input = React.forwardRef(({
  label,
  error,
  icon: Icon,
  variant = 'default',
  size = 'md',
  className,
  labelClassName,
  containerClassName,
  ...props
}, ref) => {
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2.5 text-base',
    lg: 'px-5 py-3 text-lg',
  };

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
        {Icon && (
          <Icon className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
        )}
        <input
          ref={ref}
          className={clsx(
            'input-base w-full rounded-lg border border-gray-300 bg-white',
            sizes[size],
            Icon && 'pl-10',
            error && 'border-red-500 focus:ring-red-100 focus:border-red-500',
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

Input.displayName = 'Input';

export default Input;
