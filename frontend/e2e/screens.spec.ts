/**
 * The screen review harness (Phase 2 exit bar: "nothing feels unfinished,
 * in either theme"). Env-gated: set SCREENS=1 to capture every core screen
 * in both colour schemes at desktop/tablet/mobile widths for human review.
 * Not an assertion suite - it exists so the review actually happens.
 */
import { execSync } from "node:child_process";
import { createHmac } from "node:crypto";

import { expect, test } from "@playwright/test";

import { EDITOR_SUBJECT, JWT_SECRET } from "../playwright.config";

function b64url(input: Buffer | string): string {
  return Buffer.from(input).toString("base64url");
}

function mintToken(subject: string): string {
  const header = b64url(JSON.stringify({ alg: "HS256", typ: "JWT" }));
  const payload = b64url(
    JSON.stringify({
      sub: subject,
      aud: "authenticated",
      exp: Math.floor(Date.now() / 1000) + 3600,
    }),
  );
  const signature = createHmac("sha256", JWT_SECRET)
    .update(`${header}.${payload}`)
    .digest("base64url");
  return `${header}.${payload}.${signature}`;
}

const SUBJECT = `screens-${Date.now()}`;

test("capture the core screens in both themes and three widths", async ({ page, request }) => {
  test.skip(!process.env.SCREENS, "screenshot review runs only when SCREENS=1");

  const workspaceId = execSync(`uv run python -m app.scripts.seed_e2e --subject ${SUBJECT}`, {
    cwd: "../backend",
    env: {
      ...process.env,
      DATABASE_URL: process.env.DATABASE_URL ?? "postgresql+psycopg://xenia@localhost:5432/xenia",
    },
  })
    .toString()
    .trim();

  await page.goto("/signin");
  await page.evaluate(
    (token) => localStorage.setItem("xenia_access_token", token),
    mintToken(SUBJECT),
  );

  // Found a DNA quickly through the API so the DNA screen has content.
  const answers: Record<string, string> = {
    homework: "We run paid social for DTC brands.",
    business_attributes: "DTC e-commerce brands, one to twenty million revenue",
    service_need_evidence: "Running ads with weak creative",
    buying_signals: "Hiring their first marketing manager",
    disqualifiers: "No franchise businesses\nNo in-house marketing teams",
  };
  for (const [key, text] of Object.entries(answers)) {
    await request.post("http://localhost:8000/v1/interview/answers", {
      headers: { Authorization: `Bearer ${mintToken(SUBJECT)}` },
      data: { question_key: key, text },
    });
  }
  const assembled = await request.post(
    `http://localhost:8000/internal/workbench/workspaces/${workspaceId}/assemble-queue`,
    { headers: { Authorization: `Bearer ${mintToken(EDITOR_SUBJECT)}` } },
  );
  expect(assembled.ok()).toBeTruthy();

  const widths = [
    ["desktop", 1280, 900],
    ["tablet", 768, 1000],
    ["mobile", 375, 800],
  ] as const;
  const screens = [
    ["queue", "/"],
    ["dna", "/dna"],
    ["interview", "/interview"],
  ] as const;

  for (const scheme of ["light", "dark"] as const) {
    await page.emulateMedia({ colorScheme: scheme });
    for (const [device, width, height] of widths) {
      await page.setViewportSize({ width, height });
      for (const [name, path] of screens) {
        await page.goto(path);
        await page.waitForTimeout(400); // let settle-in finish for the still
        await page.screenshot({
          path: `test-results/screens/${name}-${scheme}-${device}.png`,
          fullPage: true,
        });
      }
    }
  }
});
