"use client";

import { useState } from 'react';

export default function CleanupButton({ needsCleanup }: { needsCleanup: boolean }) {
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  if (!needsCleanup) {
    return null;
  }

  const handleCleanup = async () => {
    setIsLoading(true);
    setMessage('');
    try {
      const response = await fetch('/api/projects/cleanup-modifications', {
        method: 'POST',
      });
      const result = await response.json();

      if (response.ok) {
        setMessage(`Success! Cleaned up ${result.cleanedCount} modifications. Please refresh the page.`);
      } else {
        setMessage(`Error: ${result.error}`);
      }
    } catch (error) {
      setMessage('An unexpected error occurred.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="my-4 p-4 border border-yellow-600 bg-yellow-900/30 rounded-lg">
      <p className="text-yellow-300 text-sm">There are outdated pending modifications in the system that need to be cleaned up.</p>
      <button
        onClick={handleCleanup}
        disabled={isLoading}
        className="mt-2 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-md text-sm font-medium disabled:bg-gray-500"
      >
        {isLoading ? 'Cleaning up...' : 'Run Cleanup'}
      </button>
      {message && <p className="mt-2 text-sm text-white">{message}</p>}
    </div>
  );
}
