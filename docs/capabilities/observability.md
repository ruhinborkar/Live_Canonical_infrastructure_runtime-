# Observability Capability

Surfaces what the runtime is doing through metrics, stage events, and proof
manifests.

- **Inputs:** stage events and counters emitted across the pipeline.
- **Outputs:** runtime metrics (durations, memory, throughput, events
  processed/failed), final runtime report, proof manifest.
- **Dependencies:** `observability/`, `services/runtime_service`.
- **Authority boundaries:** observe + report only; never influences execution
  outcomes.
- **Attachment rules:** read-only; new metrics register through
  `runtime_metrics` without changing producers.
- **Future consumers:** Prometheus/OpenTelemetry exporters, SLO dashboards.
