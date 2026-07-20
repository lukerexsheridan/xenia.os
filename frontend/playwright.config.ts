/**
 * The loop-walk E2E (Doc 10, Sprint 19): the one E2E that matters.
 *
 * Boots the real backend (uvicorn + Postgres) and the Vite dev server; the
 * test walks signup -> interview -> endorsement -> queue -> decision ->
 * correction -> outcome as one design partner would.
 */
import { defineConfig } from "@playwright/test";

const DATABASE_URL = process.env.DATABASE_URL ?? "postgresql+psycopg://xenia@localhost:5432/xenia";
export const JWT_SECRET =
  process.env.SUPABASE_JWT_SECRET ?? "e2e-secret-key-with-enough-length-0123456789";
export const EDITOR_SUBJECT = "editor-e2e";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  retries: 0,
  use: { baseURL: "http://localhost:5173" },
  webServer: [
    {
      command: "uv run uvicorn app.main:app --port 8000",
      cwd: "../backend",
      url: "http://localhost:8000/v1/health",
      reuseExistingServer: false,
      env: {
        DATABASE_URL,
        SUPABASE_JWT_SECRET: JWT_SECRET,
        EDITOR_AUTH_SUBJECTS: EDITOR_SUBJECT,
        ENVIRONMENT: "ci",
      },
    },
    {
      command: "npx vite --port 5173 --strictPort",
      url: "http://localhost:5173",
      reuseExistingServer: false,
      env: { VITE_API_URL: "http://localhost:8000" },
    },
  ],
});
