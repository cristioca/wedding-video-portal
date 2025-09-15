import { NextRequest, NextResponse } from "next/server";
import { db } from "@/lib/db";
import { getSession } from "@/lib/auth";
import { sendMail } from "@/lib/mail";

// Get modifications for a project
export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const session = await getSession();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const currentUser = await db.user.findUnique({
      where: { id: session.user.id }
    });

    if (!currentUser) {
      return NextResponse.json({ error: "User not found" }, { status: 401 });
    }

    const project = await db.project.findUnique({
      where: { id: params.id }
    });

    if (!project) {
      return NextResponse.json({ error: "Project not found" }, { status: 404 });
    }

    // Authorization check
    const canView = (currentUser as any).role === 'ADMIN' || project.userId === currentUser.id;
    
    if (!canView) {
      return NextResponse.json({ error: "Forbidden" }, { status: 403 });
    }

    const modifications = await (db as any).projectModification.findMany({
      where: { projectId: params.id },
      orderBy: { createdAt: 'desc' },
      include: {
        project: {
          select: { name: true }
        }
      }
    });

    return NextResponse.json({ modifications });

  } catch (error) {
    console.error('Error fetching modifications:', error);
    return NextResponse.json(
      { error: "Internal server error" }, 
      { status: 500 }
    );
  }
}

// Approve or reject a modification (admin only)
export async function PATCH(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const session = await getSession();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const currentUser = await db.user.findUnique({
      where: { id: session.user.id }
    });

    if (!currentUser || (currentUser as any).role !== 'ADMIN') {
      return NextResponse.json({ error: "Admin access required" }, { status: 403 });
    }

    const body = await req.json();
    const { modificationId, action, notes } = body;

    if (!['approve', 'reject'].includes(action)) {
      return NextResponse.json({ error: "Invalid action" }, { status: 400 });
    }

    const modification = await (db as any).projectModification.findUnique({
      where: { id: modificationId },
      include: { project: true }
    });

    if (!modification) {
      return NextResponse.json({ error: "Modification not found" }, { status: 404 });
    }

    if (modification.status !== 'PENDING') {
      return NextResponse.json({ error: "Modification already processed" }, { status: 400 });
    }

    if (action === 'approve') {
      // Apply the modification to the project
      const updateData: any = {};
      const field = modification.fieldName;
      const value = modification.newValue;

      if (field === 'eventDate') {
        updateData[field] = new Date(value);
      } else {
        updateData[field] = value;
      }

      await db.project.update({
        where: { id: modification.projectId },
        data: updateData
      });

      // Update modification status
      await (db as any).projectModification.update({
        where: { id: modificationId },
        data: {
          status: 'APPROVED',
          approvedBy: currentUser.id,
          approvedAt: new Date(),
          notes
        }
      });

      // Check if there are any remaining pending modifications
      const remainingPending = await (db as any).projectModification.count({
        where: {
          projectId: modification.projectId,
          status: 'PENDING',
        },
      });

      if (remainingPending === 0) {
        await db.project.update({
          where: { id: modification.projectId },
          data: { adminNotifiedOfChanges: false },
        });
      }

      return NextResponse.json({ 
        success: true, 
        message: "Modification approved and applied" 
      });

    } else {
      // Reject the modification
      await (db as any).projectModification.update({
        where: { id: modificationId },
        data: {
          status: 'REJECTED',
          approvedBy: currentUser.id,
          approvedAt: new Date(),
          notes
        }
      });

      // Send email notification to client if reason is provided
      if (notes && notes.trim()) {
        const clientUser = await db.user.findUnique({
          where: { id: modification.project.userId },
        });

        if (clientUser?.email) {
          await sendMail({
            to: clientUser.email,
            subject: `Modificare respinsă pentru proiectul: ${modification.project.name}`,
            html: `
              <p>Salut, ${clientUser.name || clientUser.email}!</p>
              <p>Modificarea ta pentru proiectul <strong>${modification.project.name}</strong> a fost respinsă.</p>
              <p><strong>Motiv:</strong> ${notes}</p>
              <p>Poți face modificări noi dacă este necesar.</p>
              <a href="${process.env.NEXTAUTH_URL}/dashboard/projects/${modification.projectId}">Vezi proiectul</a>
            `,
          });
        }
      }

      // Check if there are any remaining pending modifications
      const remainingPendingAfterReject = await (db as any).projectModification.count({
        where: {
          projectId: modification.projectId,
          status: 'PENDING',
        },
      });

      if (remainingPendingAfterReject === 0) {
        await db.project.update({
          where: { id: modification.projectId },
          data: { adminNotifiedOfChanges: false },
        });
      }

      return NextResponse.json({ 
        success: true, 
        message: "Modification rejected" 
      });
    }

  } catch (error) {
    console.error('Error processing modification:', error);
    return NextResponse.json(
      { error: "Internal server error" }, 
      { status: 500 }
    );
  }
}
