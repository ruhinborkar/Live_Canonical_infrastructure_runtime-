# Execution Capability

Continuously executes queued work through the canonical pipeline
(validate → serialize → hash → persist → ledger-record).

- **Inputs:** runtime events from the task queue (`payload`, `event_type`,
  `runtime_state`, `trace_id`, `sequence_id`).
- **Outputs:** appended live-log entries, truth-ledger snapshots, audit-chain
  entries, updated operational counters.
- **Dependencies:** `validation`, `serialization`, `hashing`, `persistence`,
  `ledger`, `runtime/worker_lifecycle`, `runtime/execution_scheduler`.
- **Authority boundaries:** executes and records work; it does not decide what
  to ingest, does not raise business decisions, and does not mutate history.
- **Attachment rules:** consumers attach via engine post-processors; new
  pipeline steps must reuse canonical primitives.
- **Future consumers:** batch backfill workers, multi-tenant execution pools,
  GPU/remote executors via the external adapter framework.
