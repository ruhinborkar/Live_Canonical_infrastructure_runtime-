# Health Capability

Reports subsystem and dependency health and feeds the readiness score.

- **Inputs:** subsystem self-checks, dependency probes (filesystem, dataset,
  ledger directories), heartbeat liveness.
- **Outputs:** overall health status, dependency health report, contribution to
  readiness scoring.
- **Dependencies:** `observability/health_monitor`,
  `hardening/dependency_monitor`, `runtime/runtime_heartbeat`.
- **Authority boundaries:** assess + report; may signal degradation but takes no
  corrective action.
- **Attachment rules:** read-only endpoints; new dependencies added in
  `DependencyMonitor.DEPENDENCIES`.
- **Future consumers:** Kubernetes liveness/readiness probes, alerting
  integrations.
