import "./globals.css";
import { ReactNode } from "react";
import Link from "next/link";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";

export const metadata = {
  title: "Video Client Portal",
  description: "Colaborare clienți, proiecte, editare, livrare",
};

export default async function RootLayout({ children }: { children: ReactNode }) {
  const session = await getServerSession(authOptions);
  const user = session?.user as any | undefined;
  return (
    <html lang="ro">
      <body>
        <header className="border-b border-[#1e2230]">
          <div className="mx-auto max-w-5xl px-4 py-3 flex items-center justify-between">
            <Link href="/" className="font-semibold">Video Portal</Link>
            <nav className="flex items-center gap-4 text-sm text-[color:var(--muted)]">
              <Link href="/dashboard">{user?.role === "ADMIN" ? "Dashboard" : "Proiectele mele"}</Link>
              {session ? (
                <form action="/api/auth/signout" method="post">
                  <button className="button" type="submit">Logout</button>
                </form>
              ) : (
                <Link className="button" href="/login">Login</Link>
              )}
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-5xl px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
