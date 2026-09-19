-- Explicit v2 -> v3. Caller disables FK enforcement before its transaction,
-- then checks all references before commit and restores FK enforcement.
CREATE TABLE source_batches_v3 (
    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL UNIQUE,
    source_id TEXT NOT NULL,
    source_run_id TEXT NOT NULL,
    source_kind TEXT NOT NULL CHECK (source_kind IN ('routing', 'route_policy', 'dhcp', 'inventory_staged')),
    envelope_hash TEXT NOT NULL,
    envelope_json TEXT NOT NULL,
    receipt_json TEXT NOT NULL,
    ingested_at TEXT NOT NULL,
    demo_clock_at TEXT NOT NULL,
    UNIQUE(source_id, source_run_id)
);
INSERT INTO source_batches_v3 SELECT * FROM source_batches;
DROP TABLE source_batches;
ALTER TABLE source_batches_v3 RENAME TO source_batches;

CREATE TABLE allocation_requests (
    id TEXT PRIMARY KEY,
    actor_id TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    pool_id TEXT NOT NULL REFERENCES pools(id),
    scope_id TEXT NOT NULL REFERENCES scopes(id),
    candidate TEXT NOT NULL,
    pool_version INTEGER NOT NULL,
    baseline_version INTEGER NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('pending', 'approved', 'rejected')),
    allocation_id TEXT REFERENCES allocations(id),
    created_at TEXT NOT NULL,
    decided_at TEXT,
    decision_actor_id TEXT,
    decision_hash TEXT,
    decision_reason TEXT,
    downstream_status TEXT,
    UNIQUE(actor_id, idempotency_key)
);
CREATE TABLE audit_events (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    actor_role TEXT NOT NULL,
    action TEXT NOT NULL,
    outcome TEXT NOT NULL,
    reason TEXT NOT NULL,
    request_id TEXT,
    subject_id TEXT,
    scope_id TEXT,
    pool_id TEXT,
    address TEXT,
    details_json TEXT NOT NULL
);
CREATE INDEX audit_events_time ON audit_events(created_at, id);
CREATE TABLE exceptions (
    id TEXT PRIMARY KEY,
    subject_key TEXT NOT NULL UNIQUE,
    run_id TEXT NOT NULL REFERENCES calculation_runs(id),
    finding_id TEXT NOT NULL,
    owner_actor_id TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('open', 'acknowledged', 'escalated')),
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    handoff_from_actor_id TEXT,
    handoff_at TEXT,
    acknowledged_at TEXT
);
CREATE TABLE report_preset (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    name TEXT NOT NULL,
    run_id TEXT NOT NULL REFERENCES calculation_runs(id),
    filters_json TEXT NOT NULL,
    columns_json TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    actor_id TEXT NOT NULL
);
