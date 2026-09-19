-- Additive first-path storage. Existing intended inventory stays unchanged.
CREATE TABLE source_batches (
    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL UNIQUE,
    source_id TEXT NOT NULL,
    source_run_id TEXT NOT NULL,
    source_kind TEXT NOT NULL CHECK (source_kind IN ('routing', 'route_policy')),
    envelope_hash TEXT NOT NULL,
    envelope_json TEXT NOT NULL,
    receipt_json TEXT NOT NULL,
    ingested_at TEXT NOT NULL,
    demo_clock_at TEXT NOT NULL,
    UNIQUE(source_id, source_run_id)
);
CREATE TABLE source_coverage (
    batch_id TEXT NOT NULL REFERENCES source_batches(id),
    scope_id TEXT NOT NULL REFERENCES scopes(id),
    window_start_at TEXT NOT NULL,
    window_end_at TEXT NOT NULL,
    declared_complete INTEGER NOT NULL CHECK (declared_complete IN (0, 1)),
    effective_complete INTEGER NOT NULL CHECK (effective_complete IN (0, 1)),
    PRIMARY KEY(batch_id, scope_id)
);
CREATE TABLE source_records (
    id TEXT PRIMARY KEY,
    batch_id TEXT NOT NULL REFERENCES source_batches(id),
    row_number INTEGER NOT NULL CHECK (row_number > 0),
    source_record_id TEXT,
    status TEXT NOT NULL CHECK (status IN ('accepted', 'rejected', 'duplicate')),
    reason TEXT,
    raw_json TEXT NOT NULL,
    typed_json TEXT,
    UNIQUE(batch_id, row_number)
);
CREATE INDEX source_records_batch_status ON source_records(batch_id, status, row_number);
CREATE TABLE calculation_runs (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    demo_clock_at TEXT NOT NULL,
    result_json TEXT NOT NULL
);
CREATE INDEX calculation_runs_time ON calculation_runs(created_at, id);
