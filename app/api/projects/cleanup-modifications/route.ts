import { NextResponse } from "next/server";
import { db } from "@/lib/db";
import { getSession } from "@/lib/auth";

export async function POST(req: Request) {
  const session = await getSession();
  const user = session?.user as any;

  // Ensure only an admin can run this cleanup
  if (user?.role !== 'ADMIN') {
    return NextResponse.json({ error: "Unauthorized" }, { status: 403 });
  }

  try {
    const result = await db.projectModification.updateMany({
      where: {
        fieldName: 'editingPreferences',
        status: 'PENDING',
      },
      data: {
        status: 'REJECTED',
        notes: 'System cleanup: This modification was auto-applied and incorrectly marked as pending.',
      },
    });

    return NextResponse.json({ 
      message: 'Cleanup successful.',
      cleanedCount: result.count 
    });

  } catch (error) {
    console.error("Cleanup failed:", error);
    return NextResponse.json({ error: "Failed to cleanup modifications." }, { status: 500 });
  }
}
