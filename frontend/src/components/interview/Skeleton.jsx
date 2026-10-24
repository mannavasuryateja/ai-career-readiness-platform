import React from 'react';
import clsx from 'clsx';

const Skeleton = ({
  variant = 'text',
  width = 'w-full',
  height = 'h-4',
  count = 1,
  circle = false,
  className,
}) => {
  const variants = {
    text: 'h-4 rounded',
    heading: 'h-8 rounded-md',
    avatar: 'rounded-full',
    card: 'rounded-lg',
  };

  const skeletons = Array.from({ length: count });

  return (
    <div className="space-y-2">
      {skeletons.map((_, index) => (
        <div
          key={index}
          className={clsx(
            'animate-shimmer bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200',
            width,
            height,
            circle ? 'rounded-full' : variants[variant],
            className
          )}
        />
      ))}
    </div>
  );
};

export default Skeleton;
