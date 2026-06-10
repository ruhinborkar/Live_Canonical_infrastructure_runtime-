import { describe, expect, it } from "vitest";
import { formatEventRange } from "../lib/eventLog";

describe("eventLog", () => {
  it("formats empty range", () => {
    expect(formatEventRange(0, 25, 0)).toBe("0 events");
  });

  it("formats partial page", () => {
    expect(formatEventRange(0, 25, 10)).toBe("1–10 of 10");
  });

  it("formats middle page", () => {
    expect(formatEventRange(25, 25, 101)).toBe("26–50 of 101");
  });
});
