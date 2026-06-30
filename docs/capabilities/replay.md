# Replay Capability

Deterministically re-executes persisted events to verify reproducibility.

- **Inputs:** persisted live-execution log entries.
- **Outputs:** replay log + replay validation verdicts (hash equality).
- **Dependencies:** `replay/`, `serialization`, `hashing`, `persistence`.
- **Authority boundaries:** read + recompute only; never alters the source log
  or the truth ledger.
- **Attachment rules:** invoked on demand (`run_system.py --mode replay`) or via
  API; consumers read replay results, they do not drive replay internals.
- **Future consumers:** regression diffing, deterministic CI gates,
  time-travel debugging surfaces.
