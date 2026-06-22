export interface ValidationStateDiff {
  match: boolean;
  stored_valid: number;
  stored_invalid: number;
  recomputed_valid: number;
  recomputed_invalid: number;
  mismatch_count: number;
}

export interface RecoveryStateDiff {
  match: boolean;
  derived: Record<string, unknown>;
  independent: Record<string, unknown>;
  field_diffs: Record<string, unknown>;
}

export interface RuntimeStatus {
  runtime_status: string;
  runtime_version: string;
  environment: string;
  total_events_processed: number;
  valid_events: number;
  invalid_events: number;
  events_replayed: number;
  events_reconstructed: number;
  recovery_points: number;
  replay_verification_status: string;
  truth_verification_status: string;
  recovery_status: string;
  truth_source?: string;
  truth_checks?: Record<string, boolean>;
  validation_state_diff?: ValidationStateDiff;
  recovery_state_diff?: RecoveryStateDiff;
  original_truth_hash?: string | null;
  reconstructed_truth_hash?: string | null;
  last_verify_run_id?: string | null;
  last_verify_at?: string | null;
  last_execution_timestamp: string | null;
  last_updated: string | null;
  last_run_id: string | null;
  api_online: boolean;
  dataset?: Record<string, number | string>;
}

export interface RuntimeRunRow {
  run_id: string;
  short_id: string;
  mode: string;
  status: string;
  events_processed: number | null;
  replay_result: string;
  truth_result: string;
  recovery_result: string;
  duration_ms: number | null;
  timestamp: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface RuntimeEventRow {
  trace_id?: string;
  sequence_id?: number;
  event_type?: string;
  runtime_state?: string;
  validation_state?: string;
  hash_status: string;
  payload_hash?: string;
  validation_reason?: string;
  event_timestamp?: string;
}

export interface RuntimeMetrics {
  validation_latency_ms: number;
  serialization_time_ms: number;
  hash_computation_time_ms: number;
  persistence_writes: number;
  execution_duration_ms?: number;
  replay_duration_ms: number;
  recovery_duration_ms: number;
  total_pipeline_ms: number;
  processed_events: number;
  events_failed?: number;
  reconstruction_duration_ms?: number;
  memory_consumption_mb?: number;
  persistence_throughput_eps?: number;
  runtime_throughput_eps: number;
  last_updated: string | null;
}

export interface RuntimeHealthStatus {
  overall: string;
  runtime_health: string;
  replay_health: string;
  persistence_health: string;
  recovery_health: string;
}

export interface StartupValidationStatus {
  ready: boolean;
  status: string;
  runtime_version: string;
  checks: Record<string, boolean>;
}

export interface TruthLedgerStatus {
  available: boolean;
  truth_reconstruction?: string;
  source?: string;
  runtime_state?: string;
  snapshots_reconstructed?: number;
}

export interface InjectionProof {
  available: boolean;
  detected_count?: number;
  results?: Array<{
    failure_type: string;
    detected: boolean;
    system_response: string;
  }>;
}

export interface ProofManifestStatus {
  available: boolean;
  overall?: string;
  checks?: Record<string, boolean>;
  artifacts?: Record<string, { path: string; available: boolean }>;
}

export interface RuntimeLogEntry {
  timestamp: string;
  stage: string;
  status: string;
  message: string;
  level: string;
}

export interface RuntimeReportArtifact {
  name: string;
  path: string;
  exists: boolean;
  available: boolean;
  modified_at: string | null;
  size_bytes: number | null;
}

export interface RuntimeReportContent {
  name: string;
  path: string;
  content: string;
  truncated: boolean;
  size_bytes: number | null;
  modified_at: string | null;
}
