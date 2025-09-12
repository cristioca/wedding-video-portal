import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { getSession } from "@/lib/auth";

export async function GET(req: NextRequest, { params }: { params: { id: string } }) {
  // Validate session
  const session = await getSession();
  if (!session?.user?.id) {
    return new Response("Unauthorized", { status: 401 });
  }

  // Find the file and its associated project
  const file = await db.file.findUnique({ 
    where: { id: params.id },
    include: {
      project: {
        include: {
          user: true
        }
      }
    }
  });
  
  if (!file) {
    return new Response("Not Found", { status: 404 });
  }

  // Get current user details
  const currentUser = await db.user.findUnique({
    where: { id: session.user.id }
  });

  if (!currentUser) {
    return new Response("Unauthorized", { status: 401 });
  }

  // Authorization check: Admin can access all files, clients can only access their own project files
  const canAccess = currentUser.role === 'ADMIN' || file.project.userId === currentUser.id;
  
  if (!canAccess) {
    return new Response("Forbidden", { status: 403 });
  }

  // Log the download attempt
  await db.fileDownloadEvent.create({
    data: { 
      fileId: file.id, 
      projectId: file.projectId, 
      success: true 
    }
  });

  // TODO: Stream actual file from storage
  return new Response("File download would happen here", { status: 200 });
}
