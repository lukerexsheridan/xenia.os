/**
 * API client seam (AP4/AP5): every server interaction goes through here.
 *
 * Types come from the generated OpenAPI schema (`make openapi` then
 * `npm run generate:api` — ADR-003). Hand-written request code outside this
 * module is a review failure. The client renders what the API says and
 * never derives a rule: confidence words, rank reasons, effect sentences,
 * and lesson narrations are all server-authored strings (AP5).
 */

import type { components } from "@/lib/api/schema";

export const API_BASE_URL: string = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const TOKEN_KEY = "xenia_access_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

/** The plain-voice error (Doc 06 §9): what happened, in words. */
export class ApiError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  });
  if (!response.ok) {
    let code = "error";
    let message = "Something went wrong on our side. Nothing you did caused this.";
    try {
      const body = (await response.json()) as { code?: string; message?: string };
      code = body.code ?? code;
      message = body.message ?? message;
    } catch {
      // A non-JSON failure keeps the plain-voice default.
    }
    throw new ApiError(response.status, code, message);
  }
  return (await response.json()) as T;
}

// ── Types (generated schema, aliased for the features) ──────────────────────

export type MeResponse = components["schemas"]["MeResponse"];
export type QueueResponse = components["schemas"]["QueueResponse"];
export type QueueItem = components["schemas"]["QueueItemResponse"];
export type DecisionResponse = components["schemas"]["DecisionResponse"];
export type CorrectionResponse = components["schemas"]["CorrectionResponse"];
export type OutcomeResponse = components["schemas"]["OutcomeResponse"];
export type DeliveredBrief = components["schemas"]["DeliveredBriefResponse"];
export type DnaResponse = components["schemas"]["DnaResponse"];
export type ProposalSummary = components["schemas"]["ProposalSummaryResponse"];
export type InterviewState = components["schemas"]["InterviewStateResponse"];
export type DecisionKind = components["schemas"]["DecisionKind"];
export type BillingResponse = components["schemas"]["BillingResponse"];
export type DraftResponse = components["schemas"]["DraftResponse"];
export type DeclineChip = components["schemas"]["DeclineChip"];
export type CorrectionTargetKind = components["schemas"]["CorrectionTargetKind"];
export type OutcomeKind = components["schemas"]["OutcomeKind"];

// ── Resources ───────────────────────────────────────────────────────────────

export const api = {
  me: () => request<MeResponse>("/v1/me"),

  queue: () => request<QueueResponse>("/v1/queue"),

  decide: (recommendationId: string, kind: DecisionKind, chip?: DeclineChip, reason?: string) =>
    request<DecisionResponse>(`/v1/recommendations/${recommendationId}/decision`, {
      method: "POST",
      body: JSON.stringify({ kind, chip: chip ?? null, reason: reason ?? null }),
    }),

  correct: (targetKind: CorrectionTargetKind, targetId: string, reason?: string) =>
    request<CorrectionResponse>("/v1/corrections", {
      method: "POST",
      body: JSON.stringify({
        target_kind: targetKind,
        target_id: targetId,
        reason: reason ?? null,
      }),
    }),

  recordOutcome: (prospectId: string, kind: OutcomeKind, occurredAt: string, reason?: string) =>
    request<OutcomeResponse>(`/v1/prospects/${prospectId}/outcomes`, {
      method: "POST",
      body: JSON.stringify({ kind, occurred_at: occurredAt, reason: reason ?? null }),
    }),

  brief: (prospectId: string) => request<DeliveredBrief>(`/v1/prospects/${prospectId}/brief`),

  dna: () => request<DnaResponse>("/v1/dna"),

  endorseDna: () => request<DnaResponse>("/v1/dna/endorse", { method: "POST", body: "{}" }),

  decideProposal: (proposalId: string, endorse: boolean) =>
    request<ProposalSummary>(`/v1/dna/proposals/${proposalId}/decision`, {
      method: "POST",
      body: JSON.stringify({ endorse }),
    }),

  interview: () => request<InterviewState>("/v1/interview"),

  billing: () => request<BillingResponse>("/v1/billing"),

  draft: (prospectId: string) => request<DraftResponse>(`/v1/prospects/${prospectId}/draft`),

  composeDraft: (prospectId: string) =>
    request<DraftResponse>(`/v1/prospects/${prospectId}/draft`, { method: "POST", body: "{}" }),

  editDraft: (prospectId: string, body: string) =>
    request<DraftResponse>(`/v1/prospects/${prospectId}/draft`, {
      method: "PUT",
      body: JSON.stringify({ body }),
    }),

  answerInterview: (questionKey: string, text: string) =>
    request<InterviewState>("/v1/interview/answers", {
      method: "POST",
      body: JSON.stringify({ question_key: questionKey, text }),
    }),

  downloadBriefPdf: (prospectId: string) =>
    download(`/v1/prospects/${prospectId}/brief.pdf`, "brief.pdf"),
  downloadDnaPdf: () => download("/v1/dna/document.pdf", "dna.pdf"),
  downloadProspectsCsv: () => download("/v1/prospects/export.csv", "prospects.csv"),
};

/**
 * Authenticated file download. A bare <a href> carries no Authorization
 * header, so every export 401s in a browser — the file must be fetched with
 * the bearer token and handed to the browser as a blob.
 */
export async function download(path: string, filename: string): Promise<void> {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) {
    throw new ApiError(
      response.status,
      "download_failed",
      "That export didn't come through — nothing you did caused this. Try again.",
    );
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}
