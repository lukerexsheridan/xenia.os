/**
 * The loop walk (Doc 10, Epic 10 exit): signup → interview → endorsement →
 * queue → decision → correction (named effect) → outcome — unassisted.
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

const SUBJECT = `e2e-partner-${Date.now()}`;

const ANSWERS: Record<string, string> = {
  homework: "We run paid social for DTC brands.",
  business_attributes: "DTC e-commerce brands, one to twenty million revenue",
  service_need_evidence: "Running ads with weak creative",
  buying_signals: "Hiring their first marketing manager",
  disqualifiers: "No franchise businesses\nNo in-house marketing teams",
};

test("the loop walk: interview to outcome, unassisted", async ({ page, request }) => {
  // The world a design partner arrives to: seeded businesses with signals.
  const workspaceId = execSync(`uv run python -m app.scripts.seed_e2e --subject ${SUBJECT}`, {
    cwd: "../backend",
    env: {
      ...process.env,
      DATABASE_URL: process.env.DATABASE_URL ?? "postgresql+psycopg://xenia@localhost:5432/xenia",
    },
  })
    .toString()
    .trim();

  // 1. Sign in.
  await page.goto("/signin");
  await page.getByTestId("token-input").fill(mintToken(SUBJECT));
  await page.getByTestId("sign-in").click();
  await page.waitForURL("**/");

  // 2. The interview — conversational, five questions, resumable.
  await page.getByRole("link", { name: "Interview" }).click();
  for (let i = 0; i < 5; i += 1) {
    const prompt = await page.getByTestId("interview-prompt").textContent();
    expect(prompt).toBeTruthy();
    const state = await page.evaluate(async () => {
      const token = localStorage.getItem("xenia_access_token");
      const response = await fetch("http://localhost:8000/v1/interview", {
        headers: { Authorization: `Bearer ${token}` },
      });
      return (await response.json()) as { question_key: string };
    });
    await page.getByTestId("interview-answer").fill(ANSWERS[state.question_key]);
    await page.getByTestId("interview-send").click();
    await page.waitForTimeout(200);
  }

  // 3. Endorsement — the DNA becomes a shared agreement.
  await page.waitForURL("**/dna");
  await page.getByTestId("endorse").click();
  await expect(page.getByTestId("endorsed")).toBeVisible();

  // 4. Monday: the queue assembles (the Editor triggers it here; the
  // scheduled job runs the identical service).
  const assembled = await request.post(
    `http://localhost:8000/internal/workbench/workspaces/${workspaceId}/assemble-queue`,
    { headers: { Authorization: `Bearer ${mintToken(EDITOR_SUBJECT)}` } },
  );
  expect(assembled.ok()).toBeTruthy();

  // 5. The queue: verdict-first card + the visible exclusion. A reload
  // stands in for "opening the app on Monday" — fresh data, no cache.
  await page.goto("/");
  await expect(page.getByTestId("queue-card")).toHaveCount(1);
  await expect(page.getByTestId("queue-card")).toContainText("Brightpath Ltd");
  await expect(page.getByTestId("visible-exclusions")).toContainText("your disqualifier");

  // 6. Decision: pursue — acknowledged within the ten-second budget.
  const started = Date.now();
  await page.getByTestId("pursue").click();
  await expect(page.getByTestId("resolution")).toBeVisible();
  expect(Date.now() - started).toBeLessThan(10_000);

  // 7. Outcome: ground truth, one tap, and the win narrates its lesson.
  await page.getByRole("link", { name: "Brightpath Ltd" }).click();
  await expect(page.getByTestId("outcome-form")).toBeVisible();
  await page.getByTestId("outcome-won").click();
  await expect(page.getByTestId("outcome-note")).toContainText("learned");

  // 8. Correction: ten seconds, applied first, the effect named.
  await page.getByRole("link", { name: "Your DNA" }).click();
  await page.locator('[data-testid^="withdraw-"]').first().click();
  await expect(page.getByTestId("named-effect")).toBeVisible();
});
