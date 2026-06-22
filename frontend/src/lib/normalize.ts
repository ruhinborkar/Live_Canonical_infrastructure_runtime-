import { RunRecord, RuntimeEvent, VerifyResult } from "../api/client";

export interface ValidationStateDiff {
  match: boolean;
  stored_valid: number;
  stored_invalid: number;
  recomputed_valid: number;
  recomputed_invalid: number;
  mismatch_count: number;
  mismatched_events: Array<{
    sequence_id: number;
    stored_status: string;
    recomputed_status: string;
    stored_reason?: string;
    recomputed_reason?: string;
  }>;
}

export interface RecoveryStateDiff {
  match: boolean;
  derived: Record<string, unknown>;
  independent: Record<string, unknown>;
  field_diffs: Record<string, { derived: unknown; independent: unknown }>;
}

export interface VerifyPayload {
  truth_verification: string;
  truth_checks: Record<string, boolean>;
  failure_path_results: VerifyResult[];
  validation_state_diff?: ValidationStateDiff;
  recovery_state_diff?: RecoveryStateDiff;
  original_truth_hash?: string;
  reconstructed_truth_hash?: string;
}

export function safeArray<T>(value: unknown): T[] {
  return Array.isArray(value) ? (value as T[]) : [];
}

export function safeObject(value: unknown): Record<string, unknown> {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return value as Record<string, unknown>;
  }
  return {};
}

function isVerifyResultRow(value: unknown): value is VerifyResult {
  const row = safeObject(value);
  return typeof row.failure_type === "string";
}

export function normalizeVerifyPayload(data: unknown): VerifyPayload | null {
  const root = safeObject(data);
  const nested = root.results ?? root.verify ?? root;

  if (Array.isArray(nested)) {
    const failure_path_results = nested.filter(isVerifyResultRow);
    if (failure_path_results.length === 0) return null;
    return {
      truth_verification: String(root.truth_verification ?? "NOT_RUN"),
      truth_checks: safeObject(root.truth_checks) as Record<string, boolean>,
      failure_path_results,
    };
  }

  const obj = safeObject(nested);
  const failure_path_results = safeArray<unknown>(obj.failure_path_results).filter(
    isVerifyResultRow
  );

  const truth_verification = String(
    obj.truth_verification ?? root.truth_verification ?? "NOT_RUN"
  );
  const truth_checks = safeObject(obj.truth_checks ?? root.truth_checks) as Record<
    string,
    boolean
  >;

  if (
    failure_path_results.length > 0 ||
    truth_verification !== "NOT_RUN" ||
    Object.keys(truth_checks).length > 0
  ) {
    return {
      truth_verification,
      truth_checks,
      failure_path_results,
      validation_state_diff: (obj.validation_state_diff ??
        root.validation_state_diff) as ValidationStateDiff | undefined,
      recovery_state_diff: (obj.recovery_state_diff ??
        root.recovery_state_diff) as RecoveryStateDiff | undefined,
      original_truth_hash: String(
        obj.original_truth_hash ?? root.original_truth_hash ?? ""
      ) || undefined,
      reconstructed_truth_hash: String(
        obj.reconstructed_truth_hash ?? root.reconstructed_truth_hash ?? ""
      ) || undefined,
    };
  }

  const direct = safeArray<unknown>(root.failure_path_results).filter(isVerifyResultRow);
  if (direct.length > 0) {
    return {
      truth_verification,
      truth_checks,
      failure_path_results: direct,
    };
  }

  return null;
}

export function normalizeVerifyResults(data: unknown): VerifyResult[] {
  return normalizeVerifyPayload(data)?.failure_path_results ?? [];
}

export function normalizeEvents(response: unknown): RuntimeEvent[] {
  return safeArray<RuntimeEvent>(safeObject(response).events);
}

export function normalizeRuns(response: unknown): RunRecord[] {
  const root = safeObject(response);
  if (Array.isArray(root.runs)) return root.runs as RunRecord[];
  return safeArray<RunRecord>(response);
}
