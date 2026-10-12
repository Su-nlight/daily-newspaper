import { describe, expect, it } from "vitest";

import { linkifyCitations } from "../citations";

describe("linkifyCitations", () => {
  it("turns [n] markers into anchor links", () => {
    expect(linkifyCitations("Audits are coming [1] and [2].")).toBe(
      "Audits are coming [[1]](#cite-1) and [[2]](#cite-2).",
    );
  });

  it("leaves code and real markdown links alone", () => {
    const text = "Use `arr[1]` or [docs](https://x.example) and\n```\nlet a = b[2];\n```";
    expect(linkifyCitations(text)).toBe(text);
  });
});
