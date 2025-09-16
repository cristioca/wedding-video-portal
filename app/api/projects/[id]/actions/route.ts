import { NextRequest, NextResponse } from "next/server";
import { db } from "@/lib/db";
import { getSession } from "@/lib/auth";

// PATCH handler for archiving/unarchiving a project
export async function PATCH(req: NextRequest, { params }: { params: { id: string } }) {
  const session = await getSession();
  const user = session?.user as any;

  if (user?.role !== 'ADMIN') {
    return NextResponse.json({ error: "Unauthorized" }, { status: 403 });
  }

  const { action } = await req.json();

  if (!['archive', 'unarchive'].includes(action)) {
    return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
  }

  try {
    const updatedProject = await db.project.update({
      where: { id: params.id },
      data: { isArchived: action === 'archive' },
    });
    return NextResponse.json(updatedProject);
  } catch (error) {
    console.error(`Failed to ${action} project:`, error);
    return NextResponse.json({ error: `Failed to ${action} project` }, { status: 500 });
  }
}

// DELETE handler for permanently deleting a project
export async function DELETE(req: NextRequest, { params }: { params: { id: string } }) {
  const session = await getSession();
  const user = session?.user as any;

  if (user?.role !== 'ADMIN') {
    return NextResponse.json({ error: "Unauthorized" }, { status: 403 });
  }

  try {
    await db.project.delete({ where: { id: params.id } });
    return NextResponse.json({ message: 'Project deleted successfully' });
  } catch (error) {
    console.error('Failed to delete project:', error);
    return NextResponse.json({ error: 'Failed to delete project' }, { status: 500 });
  }
}
