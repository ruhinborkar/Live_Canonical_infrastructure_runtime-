# Scheduling Capability

Orders pending work and dispatches it to workers.

- **Inputs:** enqueued tasks with priority; worker availability.
- **Outputs:** next-task selection, dispatch statistics, queue snapshot.
- **Dependencies:** `runtime/execution_scheduler`, `capabilities/task_queue`,
  `capabilities/execution_priority`.
- **Authority boundaries:** ordering authority only; does not execute work or
  define business priority semantics.
- **Attachment rules:** alternative scheduling policies replace
  `ExecutionScheduler.next_task` without touching workers or the engine.
- **Future consumers:** fairness/quota schedulers, deadline-aware scheduling,
  multi-queue topologies.
