import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Button } from "./button";

describe("Button", () => {
  it("renders its content", () => {
    render(<Button>Pursue</Button>);
    expect(screen.getByRole("button", { name: "Pursue" })).toBeDefined();
  });

  it("applies variant classes", () => {
    render(<Button variant="outline">Decline</Button>);
    expect(screen.getByRole("button", { name: "Decline" }).className).toContain("border");
  });
});
