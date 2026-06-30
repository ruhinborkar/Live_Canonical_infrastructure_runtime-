# Timeline Capability

Maintains the chronological situation timeline and the operator action log.

- **Inputs:** significant runtime events and operator interventions.
- **Outputs:** time-ordered situation entries and operator action history.
- **Dependencies:** `capabilities/situation_timeline`,
  `capabilities/operator_actions`, `persistence`.
- **Authority boundaries:** append + read only; immutable once written.
- **Attachment rules:** producers call `record`; consumers read the tail via the
  API. No editing of historical entries.
- **Future consumers:** incident reconstruction, audit reporting, replayable
  operator sessions.
