import { useRuntime } from "../hooks/useRuntime";
import ActionBar from "./ActionBar";

export default function VerifyResults() {
  const { lastVerifyResults } = useRuntime();

  return (
    <div>
      <ActionBar />
      <div className="panel glass">
        <h2>Failure-Path Verification</h2>
        <p className="panel-desc">
          Hostile validation checks: duplicate packets, sequence corruption, trace
          mutation, invalid schema, partial replay corruption.
        </p>

        {!lastVerifyResults ? (
          <p className="loading">Click Verify to run failure-path tests</p>
        ) : (
          <div className="verify-grid">
            {lastVerifyResults.map((result) => (
              <div
                key={result.failure_type}
                className={`verify-card ${result.failure_detected ? "detected" : "clear"}`}
              >
                <div className="verify-header">
                  <span className="verify-type">{result.failure_type}</span>
                  <span
                    className={`badge ${result.failure_detected ? "invalid" : "valid"}`}
                  >
                    {result.failure_detected ? "DETECTED" : "CLEAR"}
                  </span>
                </div>
                <p className="verify-cause">{result.observable_cause}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
