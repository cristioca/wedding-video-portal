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

  // Fetch projects based on user role with pending modifications count
  const projects = (user as any).role === 'ADMIN' 
    ? await db.project.findMany({
        include: {
          user: {
            select: {
              name: true,
              email: true,
            },
          },
          modifications: {
            where: {
              status: 'PENDING'
            }
          } as any
        },
        orderBy: {
          eventDate: "desc",
        },
      })
    : await db.project.findMany({
        where: {
          userId: user.id,
        },
        include: {
          modifications: {
            where: {
              status: 'PENDING'
            }
          } as any
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
        {(user as any).role === 'ADMIN' && (
          <Link href="/dashboard/projects/new" className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Create New Project
          </Link>
        )}
      </div>

      <h2 className="text-xl font-semibold mb-4">
        {(user as any).role === 'ADMIN' ? 'All Projects' : 'Your Projects'}
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
                      <div className="flex items-center gap-2">
                        <p className="font-semibold">{project.name}</p>
                        {(project as any).modifications?.length > 0 && (
                          <span className="px-2 py-1 bg-yellow-600 text-yellow-100 text-xs rounded-full">
                            {(project as any).modifications.length} modificări în așteptare
                          </span>
                        )}
                      </div>
                      {(user as any).role === 'ADMIN' && project.user && (
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