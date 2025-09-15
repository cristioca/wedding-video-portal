'use client';

import { useState } from 'react';

export default function ResendWelcomeButton({ userId }: { userId: string }) {
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleClick = async () => {
    setIsLoading(true);
    setMessage('');

    try {
      const response = await fetch('/api/users/resend-welcome',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ userId }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to resend welcome email');
      }

      setMessage('Welcome email resent successfully!');
    } catch (err: any) {
      setMessage(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <button
        onClick={handleClick}
        disabled={isLoading}
        className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded text-xs disabled:bg-gray-500"
      >
        {isLoading ? 'Sending...' : 'Resend Welcome Email'}
      </button>
      {message && <p className="text-sm mt-2 text-green-400">{message}</p>}
    </div>
  );
}
