# Alert Capability

Raises, routes, tracks, and acknowledges operational alerts.

- **Inputs:** alert signals (source, reason, severity, context) from engine,
  intelligence, and hardening layers.
- **Outputs:** active alert set, severity summary, alert history, acknowledgement
  records.
- **Dependencies:** `capabilities/alert_pipeline`, `persistence`.
- **Authority boundaries:** classify + track only; performs no remediation.
- **Attachment rules:** any module may `raise_alert`; the dashboard
  acknowledges via the API. No direct state access.
- **Future consumers:** paging/on-call integrations, escalation policies,
  notification adapters via `external_adapter`.
