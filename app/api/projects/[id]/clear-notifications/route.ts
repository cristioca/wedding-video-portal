import { NextRequest, NextResponse } from "next/server";
import { db } from "@/lib/db";
import { getSession } from "@/lib/auth";

export async function POST(req: NextRequest, { params }: { params: { id: string } }) {
  try {
    const session = await getSession();
    const user = session?.user as any;

    // Only admins can clear notifications
    if (user?.role !== 'ADMIN') {
      return NextResponse.json({ error: "Unauthorized" }, { status: 403 });
    }

    // Get the project
    const project = await db.project.findUnique({
      where: { id: params.id }
    });

    if (!project) {
      return NextResponse.json({ error: "Project not found" }, { status: 404 });
    }

    // Clear the unsent changes flag
    await db.project.update({
      where: { id: params.id },
      data: { hasUnsentChanges: false }
    });

    return NextResponse.json({ 
      success: true, 
      message: "Notifications cleared successfully" 
    });

  } catch (error) {
    console.error('Failed to clear notifications:', error);
    return NextResponse.json({ 
      error: "Failed to clear notifications",
      details: error instanceof Error ? error.message : String(error)
    }, { status: 500 });
  }
}
