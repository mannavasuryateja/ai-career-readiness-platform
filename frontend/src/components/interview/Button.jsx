import React from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

const Button = React.forwardRef(({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  icon: Icon,
  className,
  ...props
}, ref) => {
  const baseStyles = 'button-base font-semibold transition-all duration-300';
  
  const variants = {
    primary: 'bg-gradient-to-r from-primary-600 to-primary-500 text-white hover:from-primary-700 hover:to-primary-600 hover:shadow-glow active:scale-95 disabled:opacity-50',
    secondary: 'bg-gray-100 text-gray-700 hover:bg-gray-200 active:scale-95 disabled:opacity-50',
    ghost: 'text-gray-700 hover:bg-gray-100 active:scale-95',
    success: 'bg-green-600 text-white hover:bg-green-700 active:scale-95',
    danger: 'bg-red-600 text-white hover:bg-red-700 active:scale-95',
    outline: 'border-2 border-primary-600 text-primary-600 hover:bg-primary-50 active:scale-95',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2.5 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <motion.button
      ref={ref}
      disabled={disabled || loading}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={clsx(
        baseStyles,
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      <div className="flex items-center justify-center gap-2">
        {loading ? (
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            className="w-4 h-4 border-2 border-current border-t-transparent rounded-full"
          />
        ) : Icon ? (
          <Icon size={20} />
        ) : null}
        {children}
      </div>
    </motion.button>
  );
});

Button.displayName = 'Button';

export default Button;
