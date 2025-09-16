import { NextRequest, NextResponse } from "next/server";
import { sendMail } from "@/lib/mail";
import { getSession } from "@/lib/auth";

export async function POST(req: NextRequest) {
  try {
    const session = await getSession();
    const user = session?.user as any;

    // Only allow admins to test email
    if (user?.role !== 'ADMIN') {
      return NextResponse.json({ error: "Unauthorized" }, { status: 403 });
    }

    const { to } = await req.json();

    if (!to) {
      return NextResponse.json({ error: "Email address required" }, { status: 400 });
    }

    await sendMail({
      to,
      subject: "Test Email - Wedding Video Portal",
      html: `
        <h2>Test Email</h2>
        <p>This is a test email from the Wedding Video Portal.</p>
        <p>If you received this, the email system is working correctly.</p>
        <p>Sent at: ${new Date().toLocaleString()}</p>
      `,
    });

    return NextResponse.json({ 
      success: true, 
      message: "Test email sent successfully" 
    });

  } catch (error) {
    console.error('Test email failed:', error);
    return NextResponse.json({ 
      error: "Failed to send test email",
      details: error instanceof Error ? error.message : String(error)
    }, { status: 500 });
  }
}
