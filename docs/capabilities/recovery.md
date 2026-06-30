# Recovery Capability

Restores correct operational continuity after interruption, and (with
intelligence) recommends context-aware recovery actions.

- **Inputs:** interrupted/invalid events, persisted operational state, pending
  task queue, anomaly + confidence signals.
- **Outputs:** recovered events, recovery execution proof, restart-recovery
  summary, recovery recommendations.
- **Dependencies:** `recovery/`, `runtime/restart_recovery`,
  `intelligence/context_aware_recovery`, `ledger`.
- **Authority boundaries:** restores and recommends; it supersedes interrupted
  snapshots via the ledger but never deletes history.
- **Attachment rules:** restart recovery runs automatically at engine start;
  context-aware recovery is advisory and attaches as a read view.
- **Future consumers:** automated remediation runbooks, operator-approved
  recovery workflows.
