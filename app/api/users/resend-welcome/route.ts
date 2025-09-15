import { getSession } from '@/lib/auth';
import { db } from '@/lib/db';
import { NextResponse } from 'next/server';
import bcrypt from 'bcryptjs';
import { randomBytes } from 'crypto';
import { sendMail } from '@/lib/mail';

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

    const { userId } = await req.json();

    if (!userId) {
      return new NextResponse('User ID is required', { status: 400 });
    }

    const clientUser = await db.user.findUnique({
      where: { id: userId },
    });

    if (!clientUser) {
      return new NextResponse('User not found', { status: 404 });
    }

    const newPassword = randomBytes(12).toString('hex');
    const hashedPassword = await bcrypt.hash(newPassword, 10);

    await db.user.update({
      where: { id: userId },
      data: { password: hashedPassword },
    });

    await sendMail({
      to: clientUser.email!,
      subject: 'Your New Account Credentials for the Wedding Video Portal',
      html: `
        <h1>Hello, ${clientUser.name}!</h1>
        <p>Your password has been reset. You can now log in using the following credentials:</p>
        <ul>
          <li><strong>Email:</strong> ${clientUser.email}</li>
          <li><strong>Password:</strong> ${newPassword}</li>
        </ul>
        <p>You can log in at <a href="${process.env.NEXTAUTH_URL}">${process.env.NEXTAUTH_URL}</a></p>
        <p>We recommend changing your password after your first login.</p>
      `,
    });

    return NextResponse.json({ message: 'Welcome email resent successfully' });

  } catch (error) {
    console.error('[RESEND_WELCOME_ERROR]', error);
    return new NextResponse('Internal Server Error', { status: 500 });
  }
}
