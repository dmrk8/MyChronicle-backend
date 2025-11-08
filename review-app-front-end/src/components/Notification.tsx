import React, { useEffect } from 'react';

export interface NotificationMessage {
  id: number;
  text: string;
  type?: 'error' | 'success' | 'info';
}

interface NotificationProps {
  message: NotificationMessage;
  removeMessage: (id: number) => void;
}

export default function Notification({
  message,
  removeMessage,
}: NotificationProps) {
  useEffect(() => {
    const timer = setTimeout(() => removeMessage(message.id), 5000);
    return () => clearTimeout(timer);
  }, [message, removeMessage]);

  return (
    <div className="fixed bottom-10
     left-6 z-50 flex flex-col gap-2">
      <div
        className={`px-4 py-2 rounded shadow-lg text-white ${
          message.type === 'error'
            ? 'bg-red-500'
            : message.type === 'success'
            ? 'bg-green-500'
            : 'bg-blue-500'
        }`}
      >
        {message.text}
      </div>
    </div>
  );
}
