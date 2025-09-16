import { NextRequest, NextResponse } from "next/server";
import { db } from "@/lib/db";
import { getSession } from "@/lib/auth";

export async function GET(req: NextRequest, { params }: { params: { id: string } }) {
  try {
    const session = await getSession();
    const user = session?.user as any;

    // Only admins can debug
    if (user?.role !== 'ADMIN') {
      return NextResponse.json({ error: "Unauthorized" }, { status: 403 });
    }

    // Get the project with hasUnsentChanges field
    const project = await db.project.findUnique({
      where: { id: params.id },
      select: {
        id: true,
        name: true,
        hasUnsentChanges: true,
        lastClientNotificationDate: true,
      }
    });

    if (!project) {
      return NextResponse.json({ error: "Project not found" }, { status: 404 });
    }

    return NextResponse.json({ 
      project,
      debug: {
        hasUnsentChanges: project.hasUnsentChanges,
        lastNotificationDate: project.lastClientNotificationDate,
        shouldShowButton: project.hasUnsentChanges === true
      }
    });

  } catch (error) {
    console.error('Debug endpoint failed:', error);
    return NextResponse.json({ 
      error: "Debug failed",
      details: error instanceof Error ? error.message : String(error)
    }, { status: 500 });
  }
}
