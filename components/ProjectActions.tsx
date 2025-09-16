"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function ProjectActions({ project }: { project: any }) {
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleAction = async (action: 'archive' | 'unarchive' | 'delete') => {
    if (action === 'delete' && !confirm('Are you sure you want to permanently delete this project? This action cannot be undone.')) {
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`/api/projects/${project.id}/actions`, {
        method: action === 'delete' ? 'DELETE' : 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: action !== 'delete' ? JSON.stringify({ action }) : undefined,
      });

      if (response.ok) {
        router.refresh(); // Re-fetches data on the current route
      } else {
        alert(`Failed to ${action} project.`);
      }
    } catch (error) {
      alert(`An error occurred while trying to ${action} the project.`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center gap-2">
      {project.isArchived ? (
        <button 
          onClick={() => handleAction('unarchive')}
          disabled={isLoading}
          className="px-2 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-xs font-medium disabled:bg-gray-500"
        >
          {isLoading ? '...' : 'Unarchive'}
        </button>
      ) : (
        <button 
          onClick={() => handleAction('archive')}
          disabled={isLoading}
          className="px-2 py-1 bg-yellow-600 hover:bg-yellow-700 text-white rounded text-xs font-medium disabled:bg-gray-500"
        >
          {isLoading ? '...' : 'Archive'}
        </button>
      )}
      <button 
        onClick={() => handleAction('delete')}
        disabled={isLoading}
        className="px-2 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-xs font-medium disabled:bg-gray-500"
      >
        {isLoading ? '...' : 'Delete'}
      </button>
    </div>
  );
}
