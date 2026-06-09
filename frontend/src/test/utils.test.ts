import { describe, expect, it } from "vitest";
import { statusTone, badgeClass } from "../lib/utils";

describe("utils", () => {
  it("statusTone returns success for verified", () => {
    expect(statusTone("REPLAY_VERIFIED")).toBe("success");
  });

  it("statusTone returns warning for recovery required", () => {
    expect(statusTone("RECOVERY_REQUIRED")).toBe("warning");
  });

  it("badgeClass maps tones", () => {
    expect(badgeClass("success")).toBe("badge-success");
  });
});
