import React from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';
import { Check } from 'lucide-react';

const SelectionCard = ({
  icon: Icon,
  title,
  description,
  selected = false,
  onClick,
  disabled = false,
  className,
}) => {
  return (
    <motion.button
      onClick={onClick}
      disabled={disabled}
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={clsx(
        'card-base p-6 text-left transition-all duration-300 cursor-pointer relative group',
        selected && 'ring-2 ring-primary-500 bg-primary-50 border-primary-300 shadow-lg',
        !selected && 'hover:shadow-medium hover:border-primary-200',
        disabled && 'opacity-50 cursor-not-allowed',
        className
      )}
    >
      {/* Checkmark indicator */}
      {selected && (
        <motion.div
          layoutId="selection-indicator"
          className="absolute top-4 right-4 w-6 h-6 bg-primary-600 rounded-full flex items-center justify-center"
        >
          <Check className="w-4 h-4 text-white" />
        </motion.div>
      )}

      {/* Icon */}
      {Icon && (
        <motion.div
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className={clsx(
            'w-12 h-12 rounded-lg flex items-center justify-center mb-4 transition-colors',
            selected
              ? 'bg-primary-100 text-primary-600'
              : 'bg-gray-100 text-gray-600 group-hover:bg-primary-100 group-hover:text-primary-600'
          )}
        >
          <Icon size={24} />
        </motion.div>
      )}

      {/* Title */}
      <h3 className={clsx(
        'text-lg font-semibold mb-2 transition-colors',
        selected ? 'text-primary-700' : 'text-gray-900'
      )}>
        {title}
      </h3>

      {/* Description */}
      {description && (
        <p className={clsx(
          'text-sm transition-colors',
          selected ? 'text-primary-600' : 'text-gray-600'
        )}>
          {description}
        </p>
      )}
    </motion.button>
  );
};

export default SelectionCard;
