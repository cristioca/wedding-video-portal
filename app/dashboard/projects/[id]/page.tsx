import { redirect } from "next/navigation";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { db } from "@/lib/db";
import { format } from "date-fns";
import ProjectTabs from "@/components/ProjectTabs";
import ResendWelcomeButton from "@/components/ResendWelcomeButton";
import NotifyClientButton from "@/components/NotifyClientButton";

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
    select: {
      id: true,
      name: true,
      status: true,
      eventDate: true,
      type: true,
      city: true,
      titleVideo: true,
      civilUnionDetails: true,
      prep: true,
      church: true,
      session: true,
      restaurant: true,
      detailsExtra: true,
      editStatus: true,
      editingPreferences: true,
      userId: true,
      hasUnsentChanges: true,
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
      },
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
  const canAccess = user.role === 'ADMIN' || project.userId === user.id;
  
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
        <div className="flex items-center gap-4 mb-2">
          <h1 className="text-3xl font-bold">{project.name}</h1>
          {user.role === 'ADMIN' && project.hasUnsentChanges && (
            <NotifyClientButton 
              projectId={project.id} 
              hasUnsentChanges={project.hasUnsentChanges}
              size="small"
            />
          )}
        </div>
        <div className="mt-2 space-y-1 text-gray-600">
          <p><strong>Data eveniment:</strong> {format(project.eventDate, "MMMM d, yyyy")}</p>
          <p><strong>Status:</strong> {project.status}</p>
          <p><strong>Tip:</strong> {project.type}</p>
          {project.city && <p><strong>Oraș:</strong> {project.city}</p>}
          {project.titleVideo && <p><strong>Titlu:</strong> {project.titleVideo}</p>}
          {user.role === 'ADMIN' && project.user && (
            <div className="flex items-center gap-4 mt-1">
              <p><strong>Client:</strong> {project.user.name} ({project.user.email})</p>
              <ResendWelcomeButton userId={project.userId} />
            </div>
          )}
        </div>
      </div>

      <ProjectTabs 
        project={project} 
        userRole={user.role}
        pendingModifications={project.modifications || []}
      />
    </div>
  );
}
