-- Explicit v6 -> v7. Durable notice notification history with reviewed recipient binding.
-- Fresh databases start empty. Explicit migration preserves only the known current
-- notification version and one distinct older complete acknowledgement version.
-- No recipient or configuration or issued time is invented for legacy rows.
CREATE TABLE reservation_notice_notifications (
    notice_id TEXT NOT NULL REFERENCES reservation_notices(id),
    notification_version INTEGER NOT NULL CHECK (notification_version > 0),
    recipient_id TEXT,
    configuration_revision INTEGER CHECK (configuration_revision IS NULL OR configuration_revision > 0),
    configuration_digest TEXT,
    routing_status TEXT NOT NULL CHECK (routing_status IN ('assigned', 'unassigned', 'unroutable', 'legacy_unbound')),
    routing_reason TEXT,
    issued_at TEXT,
    acknowledged_by TEXT,
    acknowledged_at TEXT,
    acknowledgement_reason TEXT,
    PRIMARY KEY (notice_id, notification_version),
    CHECK ((configuration_revision IS NULL AND configuration_digest IS NULL) OR (configuration_revision IS NOT NULL AND configuration_digest IS NOT NULL)),
    CHECK ((routing_status = 'assigned' AND routing_reason IS NULL) OR (routing_status IN ('unassigned', 'unroutable', 'legacy_unbound') AND routing_reason IS NOT NULL)),
    CHECK ((acknowledged_by IS NULL AND acknowledged_at IS NULL AND acknowledgement_reason IS NULL) OR (acknowledged_by IS NOT NULL AND acknowledged_at IS NOT NULL AND acknowledgement_reason IS NOT NULL))
);
CREATE INDEX reservation_notice_notifications_recipient ON reservation_notice_notifications(recipient_id, notice_id, notification_version);
SELECT CASE WHEN EXISTS (SELECT 1 FROM reservation_notices WHERE acknowledgement_version > notification_version) THEN RAISE(ABORT, 'legacy notice acknowledgement exceeds current notification version') END;
SELECT CASE WHEN EXISTS (SELECT 1 FROM reservation_notices WHERE (acknowledged_by IS NULL AND (acknowledged_at IS NOT NULL OR acknowledgement_reason IS NOT NULL)) OR (acknowledged_at IS NULL AND (acknowledged_by IS NOT NULL OR acknowledgement_reason IS NOT NULL)) OR (acknowledgement_reason IS NULL AND (acknowledged_by IS NOT NULL OR acknowledged_at IS NOT NULL))) THEN RAISE(ABORT, 'legacy notice acknowledgement is partial and cannot be preserved') END;
INSERT INTO reservation_notice_notifications (notice_id, notification_version, recipient_id, configuration_revision, configuration_digest, routing_status, routing_reason, issued_at, acknowledged_by, acknowledged_at, acknowledgement_reason) SELECT id, notification_version, NULL, NULL, NULL, 'legacy_unbound', 'legacy_unbound', NULL, CASE WHEN acknowledgement_version = notification_version THEN acknowledged_by ELSE NULL END, CASE WHEN acknowledgement_version = notification_version THEN acknowledged_at ELSE NULL END, CASE WHEN acknowledgement_version = notification_version THEN acknowledgement_reason ELSE NULL END FROM reservation_notices;
INSERT INTO reservation_notice_notifications (notice_id, notification_version, recipient_id, configuration_revision, configuration_digest, routing_status, routing_reason, issued_at, acknowledged_by, acknowledged_at, acknowledgement_reason) SELECT id, acknowledgement_version, NULL, NULL, NULL, 'legacy_unbound', 'legacy_unbound', NULL, acknowledged_by, acknowledged_at, acknowledgement_reason FROM reservation_notices WHERE acknowledgement_version < notification_version AND acknowledged_by IS NOT NULL AND acknowledged_at IS NOT NULL AND acknowledgement_reason IS NOT NULL;
