import { RunRecord, RuntimeEvent, VerifyResult } from "../api/client";

export interface VerifyPayload {
  truth_verification: string;
  truth_checks: Record<string, boolean>;
  failure_path_results: VerifyResult[];
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
    return { truth_verification, truth_checks, failure_path_results };
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
