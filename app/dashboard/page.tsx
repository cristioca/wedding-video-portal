import { getSession } from "@/lib/auth";
import { db } from "@/lib/db";
import { redirect } from "next/navigation";
import Link from "next/link";
import { format } from "date-fns";
import CleanupButton from "@/components/CleanupButton";
import ProjectActions from "@/components/ProjectActions";
import NotifyClientButton from "@/components/NotifyClientButton";

export default async function Dashboard({ searchParams }: { searchParams: { showArchived?: string } }) {
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

  // Check for outdated modifications that need cleanup, only for admins
  let needsCleanup = 0;
  if ((user as any).role === 'ADMIN') {
    needsCleanup = await db.projectModification.count({
      where: {
        fieldName: 'editingPreferences',
        status: 'PENDING',
      },
    });
  }

  const showArchived = searchParams.showArchived === 'true';

  // Base query options
  const queryOptions = {
    where: {
      isArchived: showArchived,
    },
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
  };

  // Fetch projects based on user role with pending modifications count
  const projects = (user as any).role === 'ADMIN' 
    ? await db.project.findMany(queryOptions)
    : await db.project.findMany({
        ...queryOptions,
        where: {
          ...queryOptions.where,
          userId: user.id,
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

      {(user as any).role === 'ADMIN' && <CleanupButton needsCleanup={needsCleanup > 0} />}

      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">
          {(user as any).role === 'ADMIN' ? 'Toate proiectele' : 'Your Projects'}
        </h2>
        {(user as any).role === 'ADMIN' && (
          <Link href={showArchived ? '/dashboard' : '/dashboard?showArchived=true'} className="text-sm text-indigo-400 hover:underline">
            {showArchived ? 'Ascunde arhiva' : 'Arată arhiva'}
          </Link>
        )}
      </div>
      <div className="bg-gray-800 rounded-lg shadow">
        <ul className="divide-y divide-gray-700">
          {projects.length > 0 ? (
            projects.map((project: any) => (
              <li key={project.id} className="p-4 hover:bg-gray-700 flex justify-between items-center">
                <Link
                  href={`/dashboard/projects/${project.id}`}
                  className="flex-grow"
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
                    <div className="flex flex-col items-end gap-2">
                      <p className="text-sm text-gray-400">
                        {format(project.eventDate, "MMMM d, yyyy")}
                      </p>
                    </div>
                  </div>
                </Link>
                <div className="ml-4 flex items-center gap-2">
                  {(user as any).role === 'ADMIN' && <ProjectActions project={project} />}
                  {(user as any).role === 'ADMIN' && (project as any).hasUnsentChanges && (
                    <NotifyClientButton 
                      projectId={project.id} 
                      hasUnsentChanges={(project as any).hasUnsentChanges}
                      size="small"
                    />
                  )}
                </div>
              </li>
            ))
          ) : (
            <p className="p-4 text-center text-gray-500">
              Nu ai proiecte încă.
            </p>
          )}
        </ul>
      </div>
    </div>
  );
}