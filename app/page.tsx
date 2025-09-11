import Link from "next/link";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-4xl font-bold mb-4">Wedding Video Portal</h1>
      <p className="text-lg mb-8">Your central hub for managing wedding video projects.</p>
      <Link href="/dashboard" className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-md font-medium">
        Go to Dashboard
      </Link>
    </div>
  );
}