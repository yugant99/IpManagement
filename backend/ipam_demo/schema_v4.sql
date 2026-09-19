-- Explicit v3 -> v4. Legacy stores start disabled without acquiring evidence.
CREATE TABLE schedule_status (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    enabled INTEGER NOT NULL DEFAULT 0 CHECK (enabled IN (0, 1)),
    interval_hours INTEGER NOT NULL DEFAULT 6 CHECK (interval_hours BETWEEN 1 AND 168),
    config_version INTEGER NOT NULL DEFAULT 1 CHECK (config_version > 0),
    next_due_at TEXT,
    last_attempt_at TEXT,
    last_success_at TEXT,
    last_outcome TEXT CHECK (last_outcome IN ('complete', 'partial', 'failed', 'busy')),
    last_error_json TEXT,
    feed_version TEXT NOT NULL DEFAULT 'ipam-evolving-v1',
    cycle_index INTEGER NOT NULL DEFAULT 0 CHECK (cycle_index BETWEEN 0 AND 1460),
    cycle_id TEXT,
    run_id TEXT REFERENCES calculation_runs(id),
    CHECK ((enabled = 0 AND next_due_at IS NULL) OR (enabled = 1 AND next_due_at IS NOT NULL))
);
INSERT INTO schedule_status(singleton) VALUES (1);

-- Only committed cycles enter this table, in the same transaction as their run.
CREATE TABLE schedule_operations (
    operation_id TEXT PRIMARY KEY,
    actor_id TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    result_json TEXT NOT NULL,
    UNIQUE(actor_id, idempotency_key)
);
