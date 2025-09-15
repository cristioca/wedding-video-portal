import nodemailer from 'nodemailer';

const smtpConfig = {
  host: process.env.SMTP_HOST,
  port: Number(process.env.SMTP_PORT),
  secure: process.env.SMTP_SECURE === 'true', // true for 465, false for other ports
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS,
  },
};

const transporter = nodemailer.createTransport(smtpConfig);

interface MailOptions {
  to: string;
  subject: string;
  html: string;
}

export const sendMail = async ({ to, subject, html }: MailOptions) => {
  try {
    await transporter.sendMail({
      from: `"Wedding Video Portal" <${process.env.SMTP_FROM_EMAIL}>`,
      to,
      subject,
      html,
    });
    console.log('Email sent successfully to:', to);
  } catch (error) {
    console.error('Error sending email:', error);
    // Depending on the use case, you might want to throw the error
    // to be handled by the calling function.
    throw new Error('Failed to send email.');
  }
};
