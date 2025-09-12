import { redirect } from "next/navigation";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { db } from "@/lib/db";
import { format } from "date-fns";
import ProjectTabs from "@/components/ProjectTabs";

export default async function ProjectPage({ params }: { params: { id: string } }) {
  const session = await getServerSession(authOptions);
  
  if (!session?.user?.email) {
    redirect("/login");
  }

  // Get current user
  const user = await db.user.findUnique({
    where: {
      email: session.user.email,
    },
  });

  if (!user) {
    redirect("/login");
  }

  // Get project with files and pending modifications
  const project = await db.project.findUnique({
    where: {
      id: params.id,
    },
    include: {
      user: {
        select: {
          name: true,
          email: true,
        },
      },
      files: true,
      modifications: {
        where: {
          status: 'PENDING'
        },
        orderBy: {
          createdAt: 'desc'
        }
      } as any,
    },
  });

  if (!project) {
    return (
      <div className="container mx-auto p-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-500">Project Not Found</h1>
          <p className="mt-2 text-gray-600">The project you're looking for doesn't exist.</p>
        </div>
      </div>
    );
  }

  // Authorization check: Admin can see all projects, clients can only see their own
  const canAccess = (user as any).role === 'ADMIN' || project.userId === user.id;
  
  if (!canAccess) {
    return (
      <div className="container mx-auto p-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-500">Access Denied</h1>
          <p className="mt-2 text-gray-600">You don't have permission to view this project.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">{project.name}</h1>
        <div className="mt-2 space-y-1 text-gray-600">
          <p><strong>Event Date:</strong> {format(project.eventDate, "MMMM d, yyyy")}</p>
          <p><strong>Due Date:</strong> {format(project.dueDate, "MMMM d, yyyy")}</p>
          <p><strong>Status:</strong> {project.status}</p>
          <p><strong>Type:</strong> {project.type}</p>
          {project.city && <p><strong>City:</strong> {project.city}</p>}
          {project.titleVideo && <p><strong>Title:</strong> {project.titleVideo}</p>}
          {(user as any).role === 'ADMIN' && (project as any).user && (
            <p><strong>Client:</strong> {(project as any).user.name || (project as any).user.email}</p>
          )}
        </div>
      </div>

      <ProjectTabs 
        project={project as any} 
        userRole={(user as any).role}
        pendingModifications={(project as any).modifications || []}
      />
    </div>
  );
}
