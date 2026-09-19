import { ApiError, request } from "./api";

export interface ScheduleError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ScheduleStatus {
  enabled: boolean;
  interval_hours: number;
  config_version: number;
  next_due_at: string | null;
  last_attempt_at: string | null;
  last_success_at: string | null;
  last_outcome: "complete" | "partial" | "failed" | "busy" | null;
  last_error: ScheduleError | null;
  feed_version: string;
  cycle_index: number;
  cycle_id: string | null;
  demo_clock_at: string;
  run_id: string | null;
  in_progress: boolean;
  eligibility: { eligible: boolean; error: ScheduleError | null };
  timer_error: ScheduleError | null;
}

export interface ScheduleConfiguration {
  actor_id: string;
  reason: string;
  expected_config_version: number;
  enabled: boolean;
  interval_hours: number;
}

export interface ManualScheduleRun {
  actor_id: string;
  reason: string;
  idempotency_key: string;
}

export interface ScheduleRunResult {
  operation_id: string;
  cycle_index: number;
  cycle_id: string;
  feed_version: string;
  demo_clock_at: string;
  run_id: string;
  outcome: "complete" | "partial";
  completed_at: string;
  replay: boolean;
}

export function loadSchedule(signal: AbortSignal) {
  return request<ScheduleStatus>("/api/schedule", signal);
}

export function saveSchedule(payload: ScheduleConfiguration, signal: AbortSignal) {
  return request<ScheduleStatus>("/api/schedule", signal, false,
    { method: "POST", body: JSON.stringify(payload) });
}

export async function runSchedule(payload: ManualScheduleRun, signal: AbortSignal) {
  let status = 0;
  const result = await request<ScheduleRunResult>("/api/schedule/run", signal, false,
    { method: "POST", body: JSON.stringify(payload), onResponse: response => { status = response.status; } });
  // An unreadable success must retain its key just like a lost response.
  if (!result || ![200, 201].includes(status) || typeof result.replay !== "boolean"
    || result.replay !== (status === 200)
    || !Number.isInteger(result.cycle_index) || result.cycle_index < 1
    || !["complete", "partial"].includes(result.outcome)
    || [result.operation_id, result.cycle_id, result.feed_version, result.demo_clock_at,
      result.run_id, result.completed_at].some(value => typeof value !== "string" || !value)) {
    throw new ApiError("The run response did not confirm a saved result. Retry the same operation.", "INVALID_RESPONSE");
  }
  return result;
}
