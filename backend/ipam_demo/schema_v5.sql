-- Explicit v4 -> v5. Old saved runs and original exception evidence stay intact.
ALTER TABLE pools ADD COLUMN capacity_history_version INTEGER NOT NULL DEFAULT 1
    CHECK (capacity_history_version > 0);
-- Do not restore history that legacy concurrency guards already invalidated.
UPDATE pools SET capacity_history_version = 2
WHERE pool_version != 1 OR EXISTS (
    SELECT 1 FROM prefixes WHERE prefixes.id = pools.prefix_id AND prefixes.version != 1
);

CREATE TABLE correction_requests (
    id TEXT PRIMARY KEY,
    actor_id TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    scope_id TEXT NOT NULL REFERENCES scopes(id),
    source_run_id TEXT NOT NULL REFERENCES calculation_runs(id),
    source_finding_id TEXT NOT NULL,
    baseline_version INTEGER NOT NULL CHECK (baseline_version > 0),
    state TEXT NOT NULL CHECK (state IN ('pending', 'approved', 'rejected')),
    prefix_id TEXT REFERENCES prefixes(id),
    created_at TEXT NOT NULL,
    decided_at TEXT,
    decision_actor_id TEXT,
    decision_hash TEXT,
    decision_reason TEXT,
    approved_baseline_version INTEGER,
    result_run_id TEXT REFERENCES calculation_runs(id),
    UNIQUE(actor_id, idempotency_key)
);

-- NULL latest pointers mean not refreshed since migration, never current health.
ALTER TABLE exceptions ADD COLUMN latest_run_id TEXT REFERENCES calculation_runs(id);
ALTER TABLE exceptions ADD COLUMN latest_finding_id TEXT;
ALTER TABLE exceptions ADD COLUMN last_definitive_state TEXT NOT NULL DEFAULT 'anomalous'
    CHECK (last_definitive_state IN ('anomalous', 'healthy'));
-- First sync derives legacy material identities from the original saved finding.
ALTER TABLE exceptions ADD COLUMN material_keys_json TEXT;
ALTER TABLE exceptions ADD COLUMN notification_version INTEGER NOT NULL DEFAULT 1
    CHECK (notification_version > 0);
ALTER TABLE exceptions ADD COLUMN notification_reason TEXT NOT NULL DEFAULT 'initial';
ALTER TABLE exceptions ADD COLUMN episode_count INTEGER NOT NULL DEFAULT 1
    CHECK (episode_count > 0);
ALTER TABLE exceptions ADD COLUMN closed_at TEXT;
ALTER TABLE exceptions ADD COLUMN last_action_hash TEXT;
