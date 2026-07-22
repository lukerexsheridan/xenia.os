/**
 * Seamless onboarding, one field: enter an email, get a link, done. No
 * password anywhere in this flow.
 */
import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { MagicLinkSignIn } from "./magic-link-sign-in";

vi.mock("@/lib/auth/client", () => ({ signInWithMagicLink: vi.fn() }));

afterEach(() => vi.clearAllMocks());

describe("MagicLinkSignIn", () => {
  it("sends the link and confirms in plain language", async () => {
    const auth = await import("@/lib/auth/client");
    vi.mocked(auth.signInWithMagicLink).mockResolvedValue(undefined);
    render(<MagicLinkSignIn />);

    fireEvent.change(screen.getByTestId("email-input"), {
      target: { value: "founder@agency.example" },
    });
    fireEvent.click(screen.getByTestId("send-magic-link"));

    const confirmation = await screen.findByTestId("magic-link-sent");
    expect(confirmation.textContent).toContain("founder@agency.example");
    expect(auth.signInWithMagicLink).toHaveBeenCalledWith("founder@agency.example");
  });

  it("surfaces a plain-voice error without blaming the founder", async () => {
    const auth = await import("@/lib/auth/client");
    vi.mocked(auth.signInWithMagicLink).mockRejectedValue(new Error("network down"));
    render(<MagicLinkSignIn />);

    fireEvent.change(screen.getByTestId("email-input"), {
      target: { value: "founder@agency.example" },
    });
    fireEvent.click(screen.getByTestId("send-magic-link"));

    const error = await screen.findByText(/nothing you did caused this/i);
    expect(error).toBeDefined();
  });
});
