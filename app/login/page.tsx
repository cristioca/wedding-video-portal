"use client";
import { useState } from "react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [email, setEmail] = useState("admin@admin.com");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const res = await signIn("credentials", { email, password, redirect: false });
    if (res?.error) setError("Autentificare eșuată");
    else router.push("/dashboard");
  }

  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-2xl font-semibold mb-4">Autentificare</h1>
      <form onSubmit={onSubmit} className="card space-y-3">
        <div>
          <label className="block text-sm text-[color:var(--muted)] mb-1">Email</label>
          <input className="input" type="email" value={email} onChange={e=>setEmail(e.target.value)} />
        </div>
        <div>
          <label className="block text-sm text-[color:var(--muted)] mb-1">Parolă</label>
          <input className="input" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        </div>
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <button className="button w-full" type="submit">Login</button>
        <p className="text-xs text-[color:var(--muted)]">Demo: admin@admin.com / password123 sau client@client.com / password123</p>
      </form>
    </div>
  );
}
