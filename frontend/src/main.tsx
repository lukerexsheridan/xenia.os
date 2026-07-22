import { QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "@tanstack/react-router";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { BlackHoleMark } from "@/components/brand/black-hole-mark";
import { initAuth } from "@/lib/auth/client";
import { queryClient } from "@/lib/query";
import { router } from "@/router";
import "@/styles/globals.css";

const rootElement = document.getElementById("root");
if (!rootElement) throw new Error("Root element missing");

const root = createRoot(rootElement);

// The router's auth guard reads a synchronous cache (lib/auth/client.ts);
// it must be primed — including a magic-link session detected from the
// URL — before the router evaluates its first route. No spinner: the mark
// itself, at rest, is the brand's one sanctioned loading moment.
root.render(
  <div className="bg-paper flex min-h-screen items-center justify-center">
    <BlackHoleMark size={40} />
  </div>,
);

void initAuth().then(() => {
  root.render(
    <StrictMode>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </StrictMode>,
  );
});
