-- Explicit v7 to v8. Opt-in ServiceNow sandbox Incident linked to one existing
-- simulated ticket intent. Additive only: every existing row is unchanged and the
-- simulated handoff keeps its own tables and state. History is in audit_events.
-- No semicolons inside comments or literals: migration splits statements on them.
CREATE TABLE servicenow_incidents (
    intent_id TEXT PRIMARY KEY REFERENCES ticket_intents(id),
    correlation TEXT NOT NULL UNIQUE,
    business_payload_digest TEXT NOT NULL,
    instance_host TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    state TEXT NOT NULL CHECK (state IN ('unknown', 'delivered', 'failed', 'absent', 'duplicate_review')),
    state_reason TEXT NOT NULL,
    send_count INTEGER NOT NULL CHECK (send_count > 0),
    send_principal_id TEXT NOT NULL,
    send_idempotency_key TEXT NOT NULL,
    send_digest TEXT NOT NULL,
    sent_at TEXT NOT NULL,
    sys_id TEXT UNIQUE,
    number TEXT,
    assignment_group TEXT,
    assigned_to TEXT,
    external_state TEXT,
    observed_at TEXT,
    duplicate_numbers_json TEXT,
    last_error_code TEXT,
    last_error_at TEXT,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(intent_id, correlation, business_payload_digest)
        REFERENCES ticket_intents(id, correlation, business_payload_digest),
    CHECK (state <> 'delivered' OR (sys_id IS NOT NULL AND number IS NOT NULL AND observed_at IS NOT NULL))
);
