import { NextRequest, NextResponse } from "next/server";
import { db } from "@/lib/db";
import { getSession } from "@/lib/auth";
import { sendMail } from "@/lib/mail";

export async function POST(req: NextRequest, { params }: { params: { id: string } }) {
  try {
    const session = await getSession();
    const user = session?.user as any;

    // Only admins can send notifications
    if (user?.role !== 'ADMIN') {
      return NextResponse.json({ error: "Unauthorized" }, { status: 403 });
    }

    // Get the project with owner details
    const project = await db.project.findUnique({
      where: { id: params.id },
      include: {
        user: {
          select: {
            name: true,
            email: true
          }
        }
      }
    });

    if (!project) {
      return NextResponse.json({ error: "Project not found" }, { status: 404 });
    }

    if (!project.user.email) {
      return NextResponse.json({ error: "Client email not found" }, { status: 400 });
    }

    if (!project.hasUnsentChanges) {
      return NextResponse.json({ error: "No unsent changes to notify about" }, { status: 400 });
    }

    // Get recent changes since last notification
    const recentChanges = await db.projectModification.findMany({
      where: {
        projectId: params.id,
        status: 'AUTO_APPLIED',
        createdAt: {
          gte: project.lastClientNotificationDate || new Date(0)
        }
      },
      orderBy: {
        createdAt: 'desc'
      }
    });

    const fieldDisplayNames: { [key: string]: string } = {
      'eventDate': 'Data evenimentului',
      'titleVideo': 'Titlul video',
      'city': 'Orașul',
      'civilUnionDetails': 'Detalii căsătorie civilă',
      'prep': 'Pregătiri',
      'church': 'Biserica',
      'session': 'Sesiunea foto',
      'restaurant': 'Restaurantul',
      'detailsExtra': 'Detalii suplimentare',
      'editingPreferences': 'Preferințe editare'
    };

    // Create changes summary
    const changesList = recentChanges.map(change => {
      const fieldName = fieldDisplayNames[change.fieldName] || change.fieldName;
      return `• ${fieldName}: ${change.newValue}`;
    }).join('\n');

    // Send notification email
    await sendMail({
      to: project.user.email,
      subject: `Actualizare proiect: ${project.name}`,
      html: `
        <p>Salut ${project.user.name || 'Client'},</p>
        <p>Proiectul tău <strong>${project.name}</strong> a fost actualizat de către videograf.</p>
        <p><strong>Modificările efectuate:</strong></p>
        <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;">${changesList}</pre>
        <p>Poți vizualiza toate detaliile proiectului accesând:</p>
        <a href="${process.env.NEXTAUTH_URL}/dashboard/projects/${project.id}">Vezi proiectul</a>
        <br><br>
        <p>Cu respect,<br>Creative Image Studio</p>
      `,
    });

    // Update project to mark changes as sent
    await db.project.update({
      where: { id: params.id },
      data: { 
        hasUnsentChanges: false,
        lastClientNotificationDate: new Date()
      }
    });

    return NextResponse.json({ 
      success: true, 
      message: "Notification sent successfully" 
    });

  } catch (error) {
    console.error('Failed to send client notification:', error);
    return NextResponse.json({ 
      error: "Failed to send notification",
      details: error instanceof Error ? error.message : String(error)
    }, { status: 500 });
  }
}
