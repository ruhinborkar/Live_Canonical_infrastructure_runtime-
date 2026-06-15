import { describe, expect, it } from "vitest";
import { normalizeRuns, normalizeVerifyPayload, normalizeVerifyResults } from "../lib/normalize";

describe("normalizeVerifyPayload", () => {
  it("unwraps nested verify object from stored run result", () => {
    const payload = normalizeVerifyPayload({
      truth_verification: "TRUTH_VERIFIED",
      truth_checks: { replay_verified: true },
      failure_path_results: [
        {
          failure_type: "duplicate_sequence",
          failure_detected: true,
          observable_cause: "duplicate",
        },
      ],
    });
    expect(payload?.truth_verification).toBe("TRUTH_VERIFIED");
    expect(payload?.failure_path_results).toHaveLength(1);
  });

  it("unwraps legacy results array", () => {
    const payload = normalizeVerifyPayload({
      results: [{ failure_type: "x", failure_detected: false, observable_cause: "ok" }],
    });
    expect(payload?.failure_path_results).toHaveLength(1);
  });

  it("unwraps API response with object results", () => {
    const payload = normalizeVerifyPayload({
      run_id: "1",
      status: "completed",
      results: {
        truth_verification: "TRUTH_VERIFIED",
        truth_checks: {},
        failure_path_results: [
          { failure_type: "a", failure_detected: true, observable_cause: "b" },
        ],
      },
    });
    expect(payload?.failure_path_results).toHaveLength(1);
    expect(payload?.truth_verification).toBe("TRUTH_VERIFIED");
  });

  it("returns empty array for invalid verify data", () => {
    expect(normalizeVerifyResults({ results: { truth_verification: "TRUTH_VERIFIED" } })).toEqual(
      []
    );
  });
});

describe("normalizeRuns", () => {
  it("unwraps runs wrapper", () => {
    expect(normalizeRuns({ runs: [{ id: "1", mode: "live", status: "completed", created_at: "" }] })).toHaveLength(1);
  });
});
