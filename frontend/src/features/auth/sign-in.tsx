/**
 * Alpha sign-in: paste a Supabase access token (Doc 10, Sprint 17).
 *
 * The hosted Supabase auth UI arrives with the deployed environment
 * (Epic 11); at alpha, design-partner accounts are seeded and tokens issued
 * directly. Identity verification stays entirely server-side — this screen
 * only stores the bearer token the API will verify.
 */
import { useNavigate } from "@tanstack/react-router";
import { useState } from "react";

import { api, setToken } from "@/lib/api/client";

export function SignIn() {
  const navigate = useNavigate();
  const [value, setValue] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    setToken(value.trim());
    try {
      await api.me();
      await navigate({ to: "/" });
    } catch {
      setError("That token didn't verify. Nothing you did caused this — check it and try again.");
    }
  }

  return (
    <main className="mx-auto max-w-md px-6 py-24">
      <h1 className="font-serif text-2xl">Xenia</h1>
      <p className="mt-2 text-sm text-stone-600">
        Your access token, please — your account team will have sent it.
      </p>
      <textarea
        data-testid="token-input"
        className="mt-4 w-full rounded border border-stone-300 p-2 font-mono text-xs"
        rows={4}
        value={value}
        onChange={(event) => setValue(event.target.value)}
      />
      <button
        data-testid="sign-in"
        className="mt-3 rounded bg-stone-900 px-4 py-2 text-sm text-white"
        onClick={() => void submit()}
      >
        Sign in
      </button>
      {error && <p className="mt-3 text-sm text-red-800">{error}</p>}
    </main>
  );
}
