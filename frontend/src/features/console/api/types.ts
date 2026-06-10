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
  replay_duration_ms: number;
  recovery_duration_ms: number;
  total_pipeline_ms: number;
  processed_events: number;
  runtime_throughput_eps: number;
  last_updated: string | null;
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
