import { getSession } from '@/lib/auth';
import { db } from '@/lib/db';
import { NextResponse } from 'next/server';
import bcrypt from 'bcryptjs';
import { randomBytes } from 'crypto';

export async function POST(req: Request) {
  try {
    const session = await getSession();

    if (!session?.user?.email) {
      return new NextResponse('Unauthorized', { status: 401 });
    }

    const adminUser = await db.user.findUnique({
      where: { email: session.user.email },
    });

    if (!adminUser || adminUser.role !== 'ADMIN') {
      return new NextResponse('Forbidden', { status: 403 });
    }

    const body = await req.json();
    const {
      projectName,
      eventDate,
      projectType,
      clientName,
      clientEmail,
    } = body;

    if (!projectName || !eventDate || !projectType || !clientName || !clientEmail) {
      return new NextResponse('Missing required fields', { status: 400 });
    }

    // Check if client user already exists
    let clientUser = await db.user.findUnique({
      where: { email: clientEmail },
    });

    // If client doesn't exist, create a new one
    if (!clientUser) {
      const randomPassword = randomBytes(12).toString('hex');
      const hashedPassword = await bcrypt.hash(randomPassword, 10);

      clientUser = await db.user.create({
        data: {
          email: clientEmail,
          name: clientName,
          password: hashedPassword,
          role: 'CLIENT',
        },
      });
    }

    // Create the project
    const newProject = await db.project.create({
      data: {
        name: projectName,
        eventDate: new Date(eventDate),
        type: projectType,
        status: 'Planning',
        userId: clientUser.id,
      },
    });

    return NextResponse.json(newProject, { status: 201 });

  } catch (error) {
    console.error('[PROJECT_CREATE_ERROR]', error);
    return new NextResponse('Internal Server Error', { status: 500 });
  }
}
