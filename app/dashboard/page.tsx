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

  // Fetch the user
  const user = await db.user.findUnique({
    where: {
      email: session.user.email,
    },
  });

  if (!user) {
    redirect("/login");
  }

  // Fetch projects based on user role
  const projects = user.role === 'ADMIN' 
    ? await db.project.findMany({
        include: {
          user: {
            select: {
              name: true,
              email: true,
            },
          },
        },
        orderBy: {
          eventDate: "desc",
        },
      })
    : await db.project.findMany({
        where: {
          userId: user.id,
        },
        orderBy: {
          eventDate: "desc",
        },
      });

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">
          Welcome back, {user.name || "User"}!
        </h1>
      </div>

      <h2 className="text-xl font-semibold mb-4">
        {user.role === 'ADMIN' ? 'All Projects' : 'Your Projects'}
      </h2>
      <div className="bg-gray-800 rounded-lg shadow">
        <ul className="divide-y divide-gray-700">
          {projects.length > 0 ? (
            projects.map((project: any) => (
              <li key={project.id}>
                <Link
                  href={`/dashboard/projects/${project.id}`}
                  className="block p-4 hover:bg-gray-700"
                >
                  <div className="flex justify-between">
                    <div>
                      <p className="font-semibold">{project.name}</p>
                      {user.role === 'ADMIN' && project.user && (
                        <p className="text-sm text-gray-500">
                          Client: {project.user.name || project.user.email}
                        </p>
                      )}
                    </div>
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