"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface NotifyClientButtonProps {
  projectId: string;
  hasUnsentChanges: boolean;
  size?: 'small' | 'normal';
}

export default function NotifyClientButton({ projectId, hasUnsentChanges, size = 'normal' }: NotifyClientButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const router = useRouter();

  if (!hasUnsentChanges) {
    return null;
  }

  const handleNotify = async () => {
    setIsLoading(true);
    setMessage('');

    try {
      const response = await fetch(`/api/projects/${projectId}/notify-client`, {
        method: 'POST',
      });

      const result = await response.json();

      if (response.ok) {
        setMessage('Email trimis cu succes!');
        router.refresh(); // Refresh to update the UI
      } else {
        setMessage(`Eroare: ${result.error}`);
      }
    } catch (error) {
      setMessage('A apărut o eroare neașteptată.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = async () => {
    setIsLoading(true);
    setMessage('');

    try {
      const response = await fetch(`/api/projects/${projectId}/clear-notifications`, {
        method: 'POST',
      });

      const result = await response.json();

      if (response.ok) {
        setMessage('Notificări șterse!');
        router.refresh(); // Refresh to update the UI
      } else {
        setMessage(`Eroare: ${result.error}`);
      }
    } catch (error) {
      setMessage('A apărut o eroare neașteptată.');
    } finally {
      setIsLoading(false);
    }
  };

  const buttonClasses = size === 'small' 
    ? "px-2 py-1 text-xs"
    : "px-3 py-2 text-sm";

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={handleNotify}
        disabled={isLoading}
        className={`${buttonClasses} bg-blue-600 hover:bg-blue-700 text-white rounded font-medium disabled:bg-gray-500 flex items-center gap-1`}
      >
        {isLoading ? (
          <>
            <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
            Trimite...
          </>
        ) : (
          <>
            📧 Notifică
          </>
        )}
      </button>
      
      <button
        onClick={handleClear}
        disabled={isLoading}
        className={`${buttonClasses} bg-gray-600 hover:bg-gray-700 text-white rounded font-medium disabled:bg-gray-500 flex items-center gap-1`}
      >
        {isLoading ? (
          <>
            <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
            Șterge...
          </>
        ) : (
          <>
            ✕ Șterge notif.
          </>
        )}
      </button>
      
      {message && (
        <span className={`text-xs ${message.includes('succes') || message.includes('șterse') ? 'text-green-400' : 'text-red-400'}`}>
          {message}
        </span>
      )}
    </div>
  );
}
