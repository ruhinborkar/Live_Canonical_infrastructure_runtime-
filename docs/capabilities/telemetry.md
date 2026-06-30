# Telemetry Capability

Provides point-in-time and trend telemetry for triage and readiness.

- **Inputs:** runtime metrics, process info, configuration, dependency health,
  audit-chain integrity, degradation mode, heartbeat liveness.
- **Outputs:** diagnostics snapshot and the explainable operational readiness
  score (0–10 with per-signal contributors).
- **Dependencies:** `observability/runtime_metrics`,
  `hardening/runtime_diagnostics`, `hardening/readiness_score`.
- **Authority boundaries:** measure + score only; never gates execution.
- **Attachment rules:** new signals add a contributor to `ReadinessScore`
  without changing existing producers.
- **Future consumers:** capacity planning, autoscaling signals, external
  metrics pipelines.
