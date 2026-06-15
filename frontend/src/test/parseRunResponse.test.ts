import { describe, expect, it } from "vitest";
import {
  parseLiveResult,
  pickRecoveryOutcome,
  pickReplayStatus,
  pickVerifyResults,
} from "../lib/parseRunResponse";

describe("parseRunResponse", () => {
  it("parses replay status", () => {
    expect(pickReplayStatus({ verification_result: "REPLAY_VERIFIED" })).toBe(
      "REPLAY_VERIFIED"
    );
  });

  it("parses recovery outcome", () => {
    expect(pickRecoveryOutcome({ recovery_outcome: "RECOVERY_REQUIRED" })).toBe(
      "RECOVERY_REQUIRED"
    );
  });

  it("parses verify results array", () => {
    const results = pickVerifyResults({
      results: [{ failure_type: "X", failure_detected: true, observable_cause: "y" }],
    });
    expect(results).toHaveLength(1);
    expect(results[0].failure_type).toBe("X");
  });

  it("parses verify object payload", () => {
    const results = pickVerifyResults({
      failure_path_results: [
        { failure_type: "X", failure_detected: true, observable_cause: "y" },
      ],
      truth_verification: "TRUTH_VERIFIED",
    });
    expect(results).toHaveLength(1);
  });

  it("parses live result from API payload", () => {
    const live = parseLiveResult({
      run_id: "abc",
      status: "completed",
      replay_status: "REPLAY_VERIFIED",
      truth_status: "TRUTH_VERIFIED",
      recovery_status: "RECOVERY_REQUIRED",
      runtime_execution: { processed_events: 100, valid_events: 90, invalid_events: 10 },
      dataset: { total_events: 100, normal_events: 80, corrupted_events: 10, interrupted_events: 10 },
    });
    expect(live.replay_status).toBe("REPLAY_VERIFIED");
    expect(live.runtime_execution.processed_events).toBe(100);
  });
});
