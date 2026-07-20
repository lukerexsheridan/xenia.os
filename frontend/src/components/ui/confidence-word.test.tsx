/** The confidence vocabulary renders the API's word verbatim (AP5). */
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ConfidenceWord } from "./confidence-word";

describe("ConfidenceWord", () => {
  it.each(["confident", "likely", "possible", "uncertain"])(
    "renders %s exactly as the API said it",
    (word) => {
      render(<ConfidenceWord word={word} />);
      expect(screen.getByTestId("confidence-word").textContent).toContain(word);
    },
  );

  it("carries an accessible name, not colour alone (Doc 10: AA floor)", () => {
    render(<ConfidenceWord word="possible" />);
    const badge = screen.getByTestId("confidence-word");
    expect(badge.getAttribute("aria-label")).toBe("confidence: possible");
    expect(badge.getAttribute("role")).toBe("status");
  });

  it("never invents a percentage", () => {
    render(<ConfidenceWord word="likely" />);
    expect(screen.getByTestId("confidence-word").textContent).not.toMatch(/%|\d/);
  });
});
