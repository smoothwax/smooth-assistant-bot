"use client";

import { useState } from "react";

export default function LoginPage() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(false);

    const res = await fetch("/api/auth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });

    if (res.ok) {
      window.location.href = "/";
    } else {
      setError(true);
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f4f5f2] flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <p className="text-xs uppercase tracking-[0.25em] text-[#7d8b6f] font-semibold mb-1">
            Team Smooth
          </p>
          <h1 className="text-3xl font-bold text-[#3c3c3b]">Smooth Assistant</h1>
          <p className="text-sm text-[#777] mt-1">Staff access only</p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-2xl border border-[#d7d8d2] shadow-sm p-6 space-y-4"
        >
          <div>
            <label className="block text-sm font-medium text-[#3c3c3b] mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter staff password"
              className="w-full rounded-full border border-[#cfd3c6] bg-[#fbfbfa] px-4 py-3 text-sm outline-none focus:border-[#7d8b6f]"
              autoFocus
            />
          </div>

          {error && (
            <p className="text-sm text-red-500">Incorrect password. Try again.</p>
          )}

          <button
            type="submit"
            disabled={loading || !password}
            className="w-full rounded-full bg-[#7d8b6f] px-6 py-3 text-sm font-semibold text-white hover:bg-[#6f7f61] disabled:opacity-50"
          >
            {loading ? "Checking..." : "Enter"}
          </button>
        </form>
      </div>
    </main>
  );
}
