from persistence.append_only_store import AppendOnlyStore
from recovery.persistence_helpers import analyze_recovery_state, persist_recovery_log


class RuntimeRecovery:
    RECOVERY_LOG = AppendOnlyStore.RECOVERY_LOG

    @staticmethod
    def analyze(events):
        return analyze_recovery_state(events, include_duplicates=False)

    @classmethod
    def persist_recovery_log(cls, events, recovery_result, *, clear_log: bool = True):
        persist_recovery_log(events, recovery_result, clear_log=clear_log)
