import { describe, expect, it } from "vitest";

import { cn } from "./utils";

describe("cn", () => {
  it("merges conflicting tailwind classes, last one winning", () => {
    expect(cn("p-2", "p-4")).toBe("p-4");
  });

  it("handles conditional classes", () => {
    const isHidden = [].length > 0;
    expect(cn("base", isHidden && "hidden", "extra")).toBe("base extra");
  });
});
