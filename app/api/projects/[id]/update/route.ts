import { NextRequest, NextResponse } from "next/server";
import { db } from "@/lib/db";
import { getSession } from "@/lib/auth";
import { sendMail } from "@/lib/mail";

export async function PATCH(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // Validate session
    const session = await getSession();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Get current user
    const currentUser = await db.user.findUnique({
      where: { id: session.user.id }
    });

    if (!currentUser) {
      return NextResponse.json({ error: "User not found" }, { status: 401 });
    }

    // Get the project
    const project = await db.project.findUnique({
      where: { id: params.id }
    });

    if (!project) {
      return NextResponse.json({ error: "Project not found" }, { status: 404 });
    }

    // Authorization check: Admin can edit all projects, clients can only edit their own
    const canEdit = (currentUser as any).role === 'ADMIN' || project.userId === currentUser.id;
    
    if (!canEdit) {
      return NextResponse.json({ error: "Forbidden" }, { status: 403 });
    }

    // Parse request body
    const body = await req.json();
    const { field, value } = body;

    // Validate field name (only allow specific fields to be updated)
    const allowedFields = [
      'eventDate',
      'titleVideo', 
      'city',
      'civilDate',
      'civilSameDay',
      'prep',
      'church',
      'session',
      'restaurant',
      'detailsExtra',
      'editingPreferences'
    ];

    if (!allowedFields.includes(field)) {
      return NextResponse.json({ error: "Invalid field" }, { status: 400 });
    }

    // Get current field value for tracking
    const currentValue = (project as any)[field];
    const currentValueStr = currentValue instanceof Date 
      ? currentValue.toISOString() 
      : String(currentValue || '');

    const isAdmin = (currentUser as any).role === 'ADMIN';

    // Special handling for editingPreferences - clients can update this directly
    if (field === 'editingPreferences') {
      const updateData: any = { editingPreferences: value };

      const updatedProject = await db.project.update({
        where: { id: params.id },
        data: updateData
      });

      // Create modification record for history
      await db.projectModification.create({
        data: {
          projectId: params.id,
          fieldName: field,
          oldValue: currentValueStr,
          newValue: String(value),
          status: 'AUTO_APPLIED',
          createdBy: currentUser.id,
          approvedBy: currentUser.id,
          approvedAt: new Date()
        }
      });

      return NextResponse.json({ 
        success: true, 
        applied: true,
        project: updatedProject 
      });
    }

    if (isAdmin) {
      // Admin changes are applied immediately
      const updateData: any = {};
      
      // Handle special field types
      if (field === 'eventDate' || field === 'civilDate') {
        updateData[field] = new Date(value);
      } else if (field === 'civilSameDay') {
        updateData[field] = Boolean(value);
      } else {
        updateData[field] = value;
      }

      // Update the project
      const updatedProject = await db.project.update({
        where: { id: params.id },
        data: updateData
      });

      // Create modification record for history
      await db.projectModification.create({
        data: {
          projectId: params.id,
          fieldName: field,
          oldValue: currentValueStr,
          newValue: String(value),
          status: 'AUTO_APPLIED',
          createdBy: currentUser.id,
          approvedBy: currentUser.id,
          approvedAt: new Date()
        }
      });

      return NextResponse.json({ 
        success: true, 
        applied: true,
        project: updatedProject 
      });

    } else {
      // Client changes require approval
      await db.projectModification.create({
        data: {
          projectId: params.id,
          fieldName: field,
          oldValue: currentValueStr,
          newValue: String(value),
          status: 'PENDING',
          createdBy: currentUser.id
        }
      });

      // --- Send notification email to admin if not already sent ---
      if (!project.adminNotifiedOfChanges) {
        const adminEmail = process.env.ADMIN_EMAIL;
        if (adminEmail) {
          await sendMail({
            to: adminEmail,
            subject: `Modificări în așteptare pentru proiectul: ${project.name}`,
            html: `
              <p>Clientul <strong>${currentUser.name || currentUser.email}</strong> a propus modificări pentru proiectul <strong>${project.name}</strong>.</p>
              <p>Te rugăm să revizuiești modificările în panoul de administrare.</p>
              <a href="${process.env.NEXTAUTH_URL}/dashboard/projects/${project.id}">Vezi proiectul</a>
            `,
          });

          // Mark that the admin has been notified
          await db.project.update({
            where: { id: params.id },
            data: { adminNotifiedOfChanges: true },
          });
        }
      }

      return NextResponse.json({ 
        success: true, 
        applied: false,
        message: "Modificarea a fost trimisă pentru aprobare de către Videograf."
      });
    }

  } catch (error) {
    console.error('Error updating project:', error);
    return NextResponse.json(
      { error: "Internal server error" }, 
      { status: 500 }
    );
  }
}
