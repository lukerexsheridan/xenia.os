/** The UX-state primitives (Design System §5): accessible, in-voice. */
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { EmptyState } from "./empty-state";
import { ErrorNotice } from "./error-notice";
import { CardSkeleton, TextSkeleton } from "./skeleton";

describe("UX state primitives", () => {
  it("skeletons announce themselves to screen readers, not just eyes", () => {
    render(<TextSkeleton />);
    expect(screen.getByRole("status", { name: "loading" })).toBeDefined();
  });

  it("card skeletons are shape-true, never spinners", () => {
    const { container } = render(<CardSkeleton />);
    expect(container.querySelector(".animate-skeleton")).not.toBeNull();
    expect(container.textContent).toBe(""); // no fake text, no spinner glyphs
  });

  it("empty states carry a voice, not a blank", () => {
    render(
      <EmptyState title="A quiet week — deliberately." testId="empty-week">
        Nothing met the bar.
      </EmptyState>,
    );
    expect(screen.getByTestId("empty-week").textContent).toContain("deliberately");
  });

  it("errors are alerts in plain voice", () => {
    render(<ErrorNotice message="Something broke on our side. Nothing you did caused this." />);
    expect(screen.getByRole("alert").textContent).toContain("Nothing you did");
  });
});
