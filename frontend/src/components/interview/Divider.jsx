import React from 'react';
import clsx from 'clsx';

const Divider = ({ label, className, orientation = 'horizontal' }) => {
  if (orientation === 'vertical') {
    return <div className={clsx('w-px h-full bg-gray-200', className)} />;
  }

  if (label) {
    return (
      <div className={clsx('flex items-center gap-4 my-6', className)}>
        <div className="flex-1 h-px bg-gray-200" />
        <span className="text-sm text-gray-600 font-medium">{label}</span>
        <div className="flex-1 h-px bg-gray-200" />
      </div>
    );
  }

  return <div className={clsx('h-px bg-gray-200 my-6', className)} />;
};

export default Divider;
