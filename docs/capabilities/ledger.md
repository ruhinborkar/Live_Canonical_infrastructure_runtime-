# Ledger Capability

Maintains an immutable, reconstructable truth ledger of runtime snapshots.

- **Inputs:** per-event snapshots (sequence id, validation status, payload
  hash, runtime state).
- **Outputs:** ledger-only reconstruction of operational truth and reconstruction
  proof; recovery supersession collapses superseded snapshots.
- **Dependencies:** `ledger/runtime_truth_ledger`, `hashing`, `persistence`.
- **Authority boundaries:** append + reconstruct only; the ledger is the system
  of record and is never edited in place.
- **Attachment rules:** the execution capability records snapshots; all other
  consumers read the reconstruction.
- **Future consumers:** compliance exports, external attestation, cross-runtime
  reconciliation.
