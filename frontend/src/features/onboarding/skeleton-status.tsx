/**
 * Temporary index screen for the repository skeleton (Epic 0).
 * Replaced by the real onboarding flow in Epic 10. Its one job: prove the
 * SPA ↔ API handshake end-to-end.
 */
import { useQuery } from "@tanstack/react-query";

import { fetchHealth } from "@/lib/api/client";

export function SkeletonStatus() {
  const health = useQuery({ queryKey: ["health"], queryFn: fetchHealth });

  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col justify-center gap-4 p-8">
      <h1 className="text-2xl font-semibold tracking-tight">Xenia</h1>
      <p className="text-muted-foreground">
        Repository skeleton (Epic 0). The product arrives with the build plan; nothing here is
        customer-facing yet.
      </p>
      <p className="text-sm">
        API:{" "}
        {health.isPending
          ? "checking…"
          : health.isError
            ? "unreachable"
            : `ok (${health.data.status})`}
      </p>
    </main>
  );
}
