import React from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

const Card = ({ children, className, hover = false, animated = true, ...props }) => {
  const cardClass = clsx(
    'card-base p-6 w-full',
    hover && 'card-hover',
    className
  );

  const content = <div className={cardClass} {...props}>{children}</div>;

  if (!animated) return content;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className={cardClass}
      {...props}
    >
      {children}
    </motion.div>
  );
};

export default Card;
