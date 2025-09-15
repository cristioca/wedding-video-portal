'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function NewProjectPage() {
  const router = useRouter();
  const [projectName, setProjectName] = useState('');
  const [eventDate, setEventDate] = useState('');
  const [projectType, setProjectType] = useState('NUNTA');
  const [clientName, setClientName] = useState('');
  const [clientEmail, setClientEmail] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      const response = await fetch('/api/projects/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          projectName,
          eventDate,
          projectType,
          clientName,
          clientEmail,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.message || 'Failed to create project');
      }

      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-8">Create New Project</h1>
      <form onSubmit={handleSubmit} className="max-w-lg mx-auto bg-gray-800 p-8 rounded-lg shadow-lg">
        {error && <p className="text-red-500 mb-4">{error}</p>}
        
        <div className="mb-4">
          <label htmlFor="projectName" className="block text-sm font-medium text-gray-300">Project Name</label>
          <input
            id="projectName"
            type="text"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            required
            className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div className="mb-4">
          <label htmlFor="eventDate" className="block text-sm font-medium text-gray-300">Event Date</label>
          <input
            id="eventDate"
            type="date"
            value={eventDate}
            onChange={(e) => setEventDate(e.target.value)}
            required
            className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div className="mb-4">
          <label htmlFor="projectType" className="block text-sm font-medium text-gray-300">Project Type</label>
          <select
            id="projectType"
            value={projectType}
            onChange={(e) => setProjectType(e.target.value)}
            required
            className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="NUNTA">Nunta</option>
            <option value="BOTEZ">Botez</option>
          </select>
        </div>

        <h2 className="text-xl font-semibold mb-4 mt-8 border-t border-gray-700 pt-4">Client Details</h2>

        <div className="mb-4">
          <label htmlFor="clientName" className="block text-sm font-medium text-gray-300">Client Name</label>
          <input
            id="clientName"
            type="text"
            value={clientName}
            onChange={(e) => setClientName(e.target.value)}
            required
            className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div className="mb-4">
          <label htmlFor="clientEmail" className="block text-sm font-medium text-gray-300">Client Email</label>
          <input
            id="clientEmail"
            type="email"
            value={clientEmail}
            onChange={(e) => setClientEmail(e.target.value)}
            required
            className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div className="mt-8">
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:bg-gray-500"
          >
            {isSubmitting ? 'Creating...' : 'Create Project'}
          </button>
        </div>
      </form>
    </div>
  );
}
