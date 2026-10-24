import React from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

const ChatBubble = ({
  message,
  sender = 'user', // 'user' or 'ai'
  timestamp,
  typing = false,
}) => {
  const isAI = sender === 'ai';

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={clsx('flex mb-4', isAI ? 'justify-start' : 'justify-end')}
    >
      <div
        className={clsx(
          'max-w-xs px-4 py-3 rounded-2xl',
          isAI
            ? 'bg-gray-100 text-gray-900 rounded-bl-none'
            : 'bg-gradient-to-r from-primary-600 to-primary-500 text-white rounded-br-none'
        )}
      >
        {typing ? (
          <div className="flex gap-1">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                animate={{ y: [0, -8, 0] }}
                transition={{
                  duration: 0.6,
                  delay: i * 0.1,
                  repeat: Infinity,
                }}
                className={clsx(
                  'w-2 h-2 rounded-full',
                  isAI ? 'bg-gray-400' : 'bg-white'
                )}
              />
            ))}
          </div>
        ) : (
          <>
            <p className="text-sm leading-relaxed break-words">{message}</p>
            {timestamp && (
              <p className={clsx(
                'text-xs mt-2',
                isAI ? 'text-gray-500' : 'text-white/70'
              )}>
                {timestamp}
              </p>
            )}
          </>
        )}
      </div>
    </motion.div>
  );
};

export default ChatBubble;
