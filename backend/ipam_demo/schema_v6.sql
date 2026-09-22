-- Explicit v5 -> v6. Tier A persistence only. Allocations retain their existing identity and uniqueness.
CREATE TABLE migration_assessments (
    id TEXT PRIMARY KEY,
    source_batch_id TEXT NOT NULL REFERENCES source_batches(id),
    canonical_hash TEXT NOT NULL,
    domain TEXT NOT NULL,
    mapping_revision TEXT NOT NULL,
    authority_revision TEXT NOT NULL,
    policy_revision TEXT NOT NULL,
    baseline_version INTEGER NOT NULL CHECK (baseline_version > 0),
    input_count INTEGER NOT NULL CHECK (input_count >= 0),
    accepted_count INTEGER NOT NULL CHECK (accepted_count >= 0),
    rejected_count INTEGER NOT NULL CHECK (rejected_count >= 0),
    duplicate_count INTEGER NOT NULL CHECK (duplicate_count >= 0),
    added_count INTEGER NOT NULL CHECK (added_count >= 0),
    changed_count INTEGER NOT NULL CHECK (changed_count >= 0),
    unchanged_count INTEGER NOT NULL CHECK (unchanged_count >= 0),
    conflicting_count INTEGER NOT NULL CHECK (conflicting_count >= 0),
    active_only_acknowledged INTEGER NOT NULL DEFAULT 0 CHECK (active_only_acknowledged IN (0, 1)),
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    state TEXT NOT NULL CHECK (state IN ('assessed', 'validated', 'signed', 'stale')),
    signer_id TEXT,
    signed_at TEXT,
    signoff_reason TEXT,
    supersedes_id TEXT REFERENCES migration_assessments(id),
    supersedes_reason TEXT,
    CHECK (input_count = accepted_count + rejected_count + duplicate_count),
    CHECK (accepted_count = added_count + changed_count + unchanged_count + conflicting_count)
);
CREATE INDEX migration_assessments_domain_created ON migration_assessments(domain, created_at DESC, id DESC);

CREATE TABLE migration_assessment_rows (
    id TEXT PRIMARY KEY,
    assessment_id TEXT NOT NULL REFERENCES migration_assessments(id),
    source_record_id TEXT NOT NULL REFERENCES source_records(id),
    matching_key TEXT NOT NULL,
    candidate_json TEXT NOT NULL,
    active_json TEXT,
    disposition TEXT NOT NULL CHECK (disposition IN ('added', 'changed', 'unchanged', 'conflicting')),
    reason TEXT NOT NULL,
    UNIQUE(assessment_id, source_record_id)
);
CREATE INDEX migration_assessment_rows_assessment ON migration_assessment_rows(assessment_id, disposition, id);

CREATE TABLE migration_assessment_active_only (
    id TEXT PRIMARY KEY,
    assessment_id TEXT NOT NULL REFERENCES migration_assessments(id),
    matching_key TEXT NOT NULL,
    active_json TEXT NOT NULL,
    reason TEXT NOT NULL,
    UNIQUE(assessment_id, matching_key)
);

CREATE TABLE reservations (
    id TEXT PRIMARY KEY,
    scope_id TEXT NOT NULL,
    prefix_id TEXT NOT NULL,
    pool_id TEXT NOT NULL,
    family INTEGER NOT NULL CHECK (family = 4),
    address TEXT NOT NULL,
    address_hex TEXT NOT NULL,
    owner_reference TEXT NOT NULL,
    service_reference TEXT NOT NULL,
    created_by TEXT NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    policy_revision TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('reserved', 'converted', 'released')),
    converted_allocation_id TEXT UNIQUE REFERENCES allocations(id),
    released_at TEXT,
    FOREIGN KEY(pool_id, prefix_id, scope_id, family) REFERENCES pools(id, prefix_id, scope_id, family),
    CHECK ((state = 'reserved' AND converted_allocation_id IS NULL AND released_at IS NULL)
        OR (state = 'converted' AND converted_allocation_id IS NOT NULL AND released_at IS NULL)
        OR (state = 'released' AND converted_allocation_id IS NULL AND released_at IS NOT NULL))
);
CREATE UNIQUE INDEX reservations_active_address ON reservations(scope_id, family, address) WHERE state = 'reserved';
CREATE INDEX reservations_pool_state ON reservations(pool_id, state, expires_at, id);

CREATE TABLE reservation_history (
    id TEXT PRIMARY KEY,
    reservation_id TEXT NOT NULL REFERENCES reservations(id),
    version INTEGER NOT NULL CHECK (version > 0),
    action TEXT NOT NULL CHECK (action IN ('created', 'extended', 'converted', 'released')),
    actor_id TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    reason TEXT NOT NULL,
    before_json TEXT,
    after_json TEXT NOT NULL,
    UNIQUE(reservation_id, version)
);

CREATE TABLE reservation_release_requests (
    id TEXT PRIMARY KEY,
    reservation_id TEXT NOT NULL REFERENCES reservations(id),
    reservation_version INTEGER NOT NULL CHECK (reservation_version > 0),
    requester_id TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    payload_digest TEXT NOT NULL,
    reason TEXT NOT NULL,
    expected_pool_version INTEGER NOT NULL CHECK (expected_pool_version > 0),
    expected_baseline_version INTEGER NOT NULL CHECK (expected_baseline_version > 0),
    state TEXT NOT NULL CHECK (state IN ('pending', 'approved', 'rejected')),
    created_at TEXT NOT NULL,
    decided_at TEXT,
    approver_id TEXT,
    decision_reason TEXT,
    FOREIGN KEY(reservation_id, reservation_version) REFERENCES reservation_history(reservation_id, version),
    UNIQUE(requester_id, idempotency_key)
);
CREATE INDEX reservation_release_requests_reservation ON reservation_release_requests(reservation_id, created_at DESC, id DESC);

CREATE TABLE reservation_notices (
    id TEXT PRIMARY KEY,
    reservation_id TEXT NOT NULL REFERENCES reservations(id),
    episode_number INTEGER NOT NULL CHECK (episode_number > 0),
    policy_revision TEXT NOT NULL,
    first_due_at TEXT NOT NULL,
    alert_level TEXT NOT NULL CHECK (alert_level IN ('alert', 'alarm')),
    owner_reference TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('open', 'acknowledged', 'resolved')),
    acknowledgement_version INTEGER NOT NULL DEFAULT 1 CHECK (acknowledgement_version > 0),
    notification_version INTEGER NOT NULL DEFAULT 1 CHECK (notification_version > 0),
    acknowledged_at TEXT,
    acknowledged_by TEXT,
    acknowledgement_reason TEXT,
    resolved_at TEXT,
    resolution_reason TEXT,
    UNIQUE(reservation_id, episode_number)
);

ALTER TABLE allocation_requests ADD COLUMN reservation_id TEXT REFERENCES reservations(id);

CREATE TABLE ticket_intents (
    id TEXT PRIMARY KEY,
    domain TEXT NOT NULL,
    source_request_id TEXT NOT NULL REFERENCES allocation_requests(id),
    action TEXT NOT NULL,
    correlation TEXT NOT NULL UNIQUE,
    business_payload_json TEXT NOT NULL,
    business_payload_digest TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    current_route_assignment_version INTEGER NOT NULL DEFAULT 1 CHECK (current_route_assignment_version > 0),
    contract_version TEXT NOT NULL,
    mode TEXT NOT NULL CHECK (mode = 'simulated'),
    state TEXT NOT NULL CHECK (state IN ('pending', 'routing_blocked', 'delivered', 'failed', 'unknown')),
    created_at TEXT NOT NULL,
    UNIQUE(domain, source_request_id, action),
    UNIQUE(id, correlation, business_payload_digest)
);

CREATE TABLE ticket_route_assignments (
    intent_id TEXT NOT NULL REFERENCES ticket_intents(id),
    assignment_version INTEGER NOT NULL CHECK (assignment_version > 0),
    configuration_revision TEXT NOT NULL,
    route_revision TEXT NOT NULL,
    team TEXT,
    assigned_by TEXT NOT NULL,
    reason TEXT NOT NULL,
    assigned_at TEXT NOT NULL,
    PRIMARY KEY(intent_id, assignment_version),
    CHECK (team IS NULL OR length(trim(team)) > 0)
);

CREATE TABLE ticket_attempts (
    id TEXT PRIMARY KEY,
    intent_id TEXT NOT NULL REFERENCES ticket_intents(id),
    ordinal INTEGER NOT NULL CHECK (ordinal BETWEEN 1 AND 3),
    route_assignment_version INTEGER NOT NULL CHECK (route_assignment_version > 0),
    synthetic_scenario TEXT NOT NULL CHECK (synthetic_scenario IN ('success', 'definitive_failure', 'committed_response_lost', 'no_effect_response_lost')),
    request_digest TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    result TEXT NOT NULL CHECK (result IN ('pending', 'delivered', 'failed', 'unknown')),
    reason TEXT,
    observed_ticket_id TEXT,
    UNIQUE(intent_id, ordinal),
    UNIQUE(id, intent_id, route_assignment_version, synthetic_scenario),
    FOREIGN KEY(intent_id, route_assignment_version) REFERENCES ticket_route_assignments(intent_id, assignment_version)
);
CREATE INDEX ticket_attempts_intent_started ON ticket_attempts(intent_id, started_at, id);

CREATE TABLE ticket_simulator_effects (
    id TEXT PRIMARY KEY,
    intent_id TEXT NOT NULL REFERENCES ticket_intents(id),
    attempt_id TEXT NOT NULL UNIQUE,
    correlation TEXT NOT NULL UNIQUE,
    business_payload_digest TEXT NOT NULL,
    route_assignment_version INTEGER NOT NULL CHECK (route_assignment_version > 0),
    synthetic_scenario TEXT NOT NULL CHECK (synthetic_scenario IN ('success', 'definitive_failure', 'committed_response_lost', 'no_effect_response_lost')),
    synthetic_ticket_id TEXT NOT NULL,
    committed_at TEXT NOT NULL,
    recipient_state TEXT NOT NULL,
    FOREIGN KEY(intent_id, route_assignment_version) REFERENCES ticket_route_assignments(intent_id, assignment_version),
    FOREIGN KEY(intent_id, correlation, business_payload_digest) REFERENCES ticket_intents(id, correlation, business_payload_digest),
    FOREIGN KEY(attempt_id, intent_id, route_assignment_version, synthetic_scenario)
        REFERENCES ticket_attempts(id, intent_id, route_assignment_version, synthetic_scenario)
);

-- Preserve historical singleton content without assigning it to a domain. The retained
-- report_preset table remains empty for legacy callers until T005 moves readers and writers
-- to report_presets. Do not start a schema-6 service before that access transition.
CREATE TABLE report_preset_quarantine (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    name TEXT NOT NULL,
    run_id TEXT NOT NULL REFERENCES calculation_runs(id),
    filters_json TEXT NOT NULL,
    columns_json TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    quarantined_at TEXT NOT NULL,
    quarantine_reason TEXT NOT NULL
);
INSERT INTO report_preset_quarantine(singleton, name, run_id, filters_json, columns_json, updated_at, actor_id, quarantined_at, quarantine_reason)
SELECT singleton, name, run_id, filters_json, columns_json, updated_at, actor_id, CURRENT_TIMESTAMP, 'legacy_scope_unknown'
FROM report_preset;
DELETE FROM report_preset;

CREATE TABLE report_presets (
    id TEXT PRIMARY KEY,
    domain TEXT NOT NULL,
    name TEXT NOT NULL,
    run_id TEXT NOT NULL REFERENCES calculation_runs(id),
    filters_json TEXT NOT NULL,
    columns_json TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    UNIQUE(domain, name)
);
CREATE INDEX report_presets_domain_updated ON report_presets(domain, updated_at DESC, id DESC);
