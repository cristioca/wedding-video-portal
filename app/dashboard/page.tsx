import { getSession } from "@/lib/auth";
import { db } from "@/lib/db";
import { redirect } from "next/navigation";
import Link from "next/link";
import { format } from "date-fns";

export default async function Dashboard() {
  const session = await getSession();

  if (!session?.user?.email) {
    redirect("/login");
  }

  // Fetch the user and their projects
  const user = await db.user.findUnique({
    where: {
      email: session.user.email,
    },
    include: {
      projects: {
        orderBy: {
          eventDate: "desc",
        },
      },
    },
  });

  if (!user) {
    redirect("/login");
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">
          Welcome back, {user.name || "User"}!
        </h1>
      </div>

      <h2 className="text-xl font-semibold mb-4">Your Projects</h2>
      <div className="bg-gray-800 rounded-lg shadow">
        <ul className="divide-y divide-gray-700">
          {user.projects.length > 0 ? (
            user.projects.map((project) => (
              <li key={project.id}>
                <Link
                  href={`/dashboard/projects/${project.id}`}
                  className="block p-4 hover:bg-gray-700"
                >
                  <div className="flex justify-between">
                    <p className="font-semibold">{project.name}</p>
                    <p className="text-sm text-gray-400">
                      {format(project.eventDate, "MMMM d, yyyy")}
                    </p>
                  </div>
                </Link>
              </li>
            ))
          ) : (
            <p className="p-4 text-center text-gray-500">
              You have no projects yet.
            </p>
          )}
        </ul>
      </div>
    </div>
  );
}