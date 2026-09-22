"""Immutable, domain-scoped comparison of staged intended inventory.

The caller owns a ``BEGIN IMMEDIATE`` transaction and supplies the freshly
authenticated access context and reviewed configuration. This module never
promotes candidate rows or changes active inventory.
"""

from datetime import datetime, timezone
from hashlib import sha256
import json
from uuid import uuid4

from . import access
from .errors import AppError
from .imports import _normalized
from .workflow import audit_event


_GROUPS = ("scopes", "prefixes", "pools", "allocations")
_ACTION_CREATE = "assessment.create"
_ACTION_SIGNOFF = "assessment.signoff"


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False)


def _digest(value):
    return sha256(_json(value).encode("utf-8")).hexdigest()


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _required_text(value, field, maximum=2000):
    if not isinstance(value, str) or not value.strip() or value != value.strip() or len(value) > maximum:
        raise AppError("INVALID_INPUT", f"{field} must be a nonempty string of at most {maximum} characters.", 422,
                       {"field": field})
    return value


def _positive_version(value, field):
    if type(value) is not int or value < 1:
        raise AppError("INVALID_INPUT", f"{field} must be a positive integer.", 422, {"field": field})
    return value


def _domain(context):
    if context is None or context.is_evidence_coordinator or not context.selected_domain:
        raise AppError("FORBIDDEN", "Select a permitted domain before using migration assessment.", 403)
    return context.selected_domain


def _require_configuration_context(context, configuration):
    if (context is None or context.configuration_revision != configuration.revision
            or context.configuration_digest != configuration.digest
            or context.policy_revision != configuration.policy_revision):
        raise AppError("ACCESS_CONTEXT_STALE", "Access configuration changed. Refresh the authenticated context.", 409)


def _config_lineage(configuration):
    if type(configuration.revision) is not int or configuration.revision < 1:
        raise AppError("ACCESS_CONFIGURATION_INVALID", "Reviewed access configuration is unavailable.", 503)
    return _json({"config_digest": configuration.digest, "config_revision": configuration.revision,
                  "schema": "ipam.authority_revision.v1"})


def _parse_authority_lineage(value):
    def unique_pairs(pairs):
        result = {}
        for key, item in pairs:
            if key in result:
                raise ValueError("duplicate key")
            result[key] = item
        return result

    try:
        item = json.loads(value, object_pairs_hook=unique_pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValueError("invalid constant")))
        if (not isinstance(item, dict) or set(item) != {"config_digest", "config_revision", "schema"}
                or type(item["config_revision"]) is not int or item["config_revision"] < 1
                or not isinstance(item["config_digest"], str)
                or item["schema"] != "ipam.authority_revision.v1"
                or _json(item) != value):
            raise ValueError("invalid authority revision")
        return item
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise AppError("MIGRATION_ASSESSMENT_INTEGRITY", "The saved assessment authority lineage is invalid.", 409) from exc


def _mapping_lineage(configuration, source_id, domain, scope_ids):
    for scope_id in sorted(scope_ids):
        if configuration.source_domains.get((source_id, scope_id)) != domain:
            raise AppError("NOT_FOUND", "Source import was not found in the selected domain.", 404)
    mappings = [{"source_id": source, "scope_id": scope, "domain": mapped_domain}
                for (source, scope), mapped_domain in configuration.source_domains.items()]
    mappings.sort(key=lambda item: (item["source_id"], item["scope_id"], item["domain"]))
    return "sha256:" + _digest({"schema": "ipam.migration_mapping.v1", "mappings": mappings})


def _load_candidate(connection, batch_id, context, configuration):
    domain = _domain(context)
    batch = connection.execute("SELECT * FROM source_batches WHERE id=?", (batch_id,)).fetchone()
    if batch is None or batch["source_kind"] != "inventory_staged":
        raise AppError("NOT_FOUND", "Source import was not found in the selected domain.", 404)
    try:
        envelope = json.loads(batch["envelope_json"])
        receipt = json.loads(batch["receipt_json"])
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise AppError("MIGRATION_SOURCE_INVALID", "The staged source receipt is not usable as a migration candidate.", 409) from exc
    scope_rows = envelope.get("scopes") if isinstance(envelope, dict) else None
    if (not isinstance(scope_rows, list) or not scope_rows
            or any(not isinstance(item, dict) or item.get("domain") != domain for item in scope_rows)):
        raise AppError("NOT_FOUND", "Source import was not found in the selected domain.", 404)
    scope_ids = {item.get("id") for item in scope_rows}
    if any(not isinstance(scope_id, str) for scope_id in scope_ids):
        raise AppError("MIGRATION_SOURCE_INVALID", "The staged source receipt is not usable as a migration candidate.", 409)
    mapping_revision = _mapping_lineage(configuration, batch["source_id"], domain, scope_ids)
    rows = list(connection.execute(
        "SELECT id,status,reason,typed_json FROM source_records WHERE batch_id=? ORDER BY row_number,id", (batch_id,)))
    counts = {status: sum(1 for row in rows if row["status"] == status)
              for status in ("accepted", "rejected", "duplicate")}
    try:
        input_count = receipt["input_rows"]
        receipt_counts = (receipt["accepted_rows"], receipt["rejected_rows"], receipt["duplicate_rows"])
    except (KeyError, TypeError) as exc:
        raise AppError("MIGRATION_SOURCE_INVALID", "The staged source receipt is not usable as a migration candidate.", 409) from exc
    if (receipt.get("application_status") != "staged" or receipt.get("source_kind") != "inventory_staged"
            or type(input_count) is not int or input_count != len(rows)
            or receipt_counts != (counts["accepted"], counts["rejected"], counts["duplicate"])
            or input_count != counts["accepted"] + counts["rejected"] + counts["duplicate"]
            or counts["rejected"] != 0 or counts["duplicate"] != 0
            or counts["accepted"] != input_count):
        raise AppError("MIGRATION_SOURCE_INCOMPLETE", "Only a complete, wholly accepted intended-inventory receipt can be assessed.", 409)

    candidate = {group: [] for group in _GROUPS}
    for row in rows:
        try:
            typed = json.loads(row["typed_json"])
            group = typed["inventory_group"]
            record = typed["record"]
        except (TypeError, ValueError, KeyError, json.JSONDecodeError) as exc:
            raise AppError("MIGRATION_SOURCE_INVALID", "A staged source record is not usable as a migration candidate.", 409) from exc
        if row["status"] != "accepted" or group not in candidate or not isinstance(record, dict):
            raise AppError("MIGRATION_SOURCE_INVALID", "A staged source record is not usable as a migration candidate.", 409)
        normalized = _normalized(record)
        candidate[group].append((row["id"], normalized))
    if sum(len(candidate[group]) for group in _GROUPS) != counts["accepted"]:
        raise AppError("MIGRATION_SOURCE_INVALID", "The staged source contains unsupported intended-inventory rows.", 409)
    return batch, candidate, counts, mapping_revision


def _active_object(connection, group, row):
    item = dict(row)
    if group == "scopes":
        item["managed_cidrs"] = json.loads(item["managed_cidrs"])
        return {key: item[key] for key in ("id", "name", "namespace", "domain", "region", "managed_cidrs")}
    if group == "prefixes":
        for field in ("tags", "custom_fields"):
            item[field] = json.loads(item[field])
        return {key: item[key] for key in ("id", "scope_id", "family", "cidr", "parent_id", "owner", "purpose", "tags", "custom_fields")}
    if group == "pools":
        for field in ("ranges", "exclusions"):
            item[field] = json.loads(item[field])
        return {key: item[key] for key in ("id", "scope_id", "prefix_id", "family", "name", "management_mode", "allocation_authority", "ranges", "exclusions")}
    return {key: item[key] for key in ("id", "scope_id", "prefix_id", "pool_id", "family", "address", "owner", "purpose")}


def _active_snapshot(connection, domain):
    snapshot = {group: [] for group in _GROUPS}
    queries = {
        "scopes": "SELECT s.* FROM scopes s WHERE s.domain=? ORDER BY s.id",
        "prefixes": "SELECT p.* FROM prefixes p JOIN scopes s ON s.id=p.scope_id WHERE s.domain=? ORDER BY p.id",
        "pools": "SELECT p.* FROM pools p JOIN scopes s ON s.id=p.scope_id WHERE s.domain=? ORDER BY p.id",
        "allocations": "SELECT a.* FROM allocations a JOIN scopes s ON s.id=a.scope_id WHERE s.domain=? ORDER BY a.scope_id,a.family,a.address_hex,a.id",
    }
    for group, query in queries.items():
        snapshot[group] = [_active_object(connection, group, row) for row in connection.execute(query, (domain,))]
    approved = {row["allocation_id"] for row in connection.execute(
        "SELECT r.allocation_id FROM allocation_requests r JOIN scopes s ON s.id=r.scope_id "
        "WHERE s.domain=? AND r.state='approved' AND r.allocation_id IS NOT NULL", (domain,))}
    return snapshot, approved


def _key(group, record):
    if group == "scopes":
        value = {"id": record["id"]}
    elif group in ("prefixes", "pools"):
        value = {"id": record["id"], "scope_id": record["scope_id"], "family": record["family"]}
    else:
        from ipaddress import ip_address
        value = {"scope_id": record["scope_id"], "family": record["family"],
                 "address": str(ip_address(record["address"]))}
    return _json({"group": group, **value})


def _comparison_record(group, record):
    # Staging provenance and mutable concurrency counters do not describe
    # intended content and therefore do not turn an otherwise equal row into a change.
    ignored = {"source_record_id", "version", "pool_version"}
    if group == "allocations":
        ignored.add("id")
    return {key: _normalized(value, key) for key, value in record.items() if key not in ignored}


def _compare(connection, domain, candidate):
    active, approved_allocations = _active_snapshot(connection, domain)
    by_key = {group: {_key(group, record): record for record in active[group]} for group in _GROUPS}
    accepted_rows = []
    seen = {group: set() for group in _GROUPS}
    for group in _GROUPS:
        for source_record_id, record in candidate[group]:
            key = _key(group, record)
            current = by_key[group].get(key)
            seen[group].add(key)
            if current is None:
                disposition, reason = "added", "No active object has this stable identity."
            elif (group == "allocations" and current.get("owner") != record.get("owner")
                  and current.get("id") in approved_allocations):
                disposition, reason = "conflicting", "Owner change conflicts with a current approved allocation assignment."
            elif _comparison_record(group, current) == _comparison_record(group, record):
                disposition, reason = "unchanged", "Normalized intended content matches the active object."
            else:
                disposition, reason = "changed", "Normalized intended content differs from the active object."
            accepted_rows.append({"source_record_id": source_record_id, "matching_key": key,
                                  "candidate": record, "active": current, "disposition": disposition,
                                  "reason": reason})
    active_only = []
    for group in _GROUPS:
        for current in active[group]:
            key = _key(group, current)
            if key not in seen[group]:
                active_only.append({"matching_key": key, "active": current,
                                    "reason": "Active object is absent from the candidate; no deletion is proposed."})
    counts = {kind: sum(1 for item in accepted_rows if item["disposition"] == kind)
              for kind in ("added", "changed", "unchanged", "conflicting")}
    return accepted_rows, active_only, counts


def _assessment_rows(connection, assessment_id):
    return [dict(row) for row in connection.execute(
        "SELECT source_record_id,matching_key,candidate_json,active_json,disposition,reason "
        "FROM migration_assessment_rows WHERE assessment_id=? ORDER BY matching_key,source_record_id", (assessment_id,))]


def _active_only_rows(connection, assessment_id):
    return [dict(row) for row in connection.execute(
        "SELECT matching_key,active_json,reason FROM migration_assessment_active_only "
        "WHERE assessment_id=? ORDER BY matching_key", (assessment_id,))]


def _assessment_content_digest(connection, assessment_id):
    """Hash exact immutable assessment content, excluding mutable decision fields."""
    header = connection.execute("SELECT * FROM migration_assessments WHERE id=?", (assessment_id,)).fetchone()
    if header is None:
        raise AppError("NOT_FOUND", "Migration assessment was not found in the selected domain.", 404)
    fields = ("id", "source_batch_id", "canonical_hash", "domain", "mapping_revision", "authority_revision",
              "policy_revision", "baseline_version", "input_count", "accepted_count", "rejected_count",
              "duplicate_count", "added_count", "changed_count", "unchanged_count", "conflicting_count",
              "created_by", "created_at", "supersedes_id", "supersedes_reason")
    rows = [dict(row) for row in connection.execute(
        "SELECT source_record_id,matching_key,disposition,reason,candidate_json,active_json "
        "FROM migration_assessment_rows WHERE assessment_id=? ORDER BY source_record_id", (assessment_id,))]
    active_only = [dict(row) for row in connection.execute(
        "SELECT matching_key,active_json,reason FROM migration_assessment_active_only "
        "WHERE assessment_id=? ORDER BY matching_key", (assessment_id,))]
    material = {"schema": "ipam.assessment_digest.v1",
                "header": {field: header[field] for field in fields},
                "rows": rows, "active_only": active_only}
    return "sha256:" + sha256(_json(material).encode("utf-8")).hexdigest()


def assessment_digest(connection, assessment_id):
    """Return the digest only when immutable rows still match their create-time anchor."""
    actual = _assessment_content_digest(connection, assessment_id)
    anchor_row = connection.execute(
        "SELECT result_json FROM tier_a_operation_receipts WHERE action='assessment.create' "
        "AND target_kind='migration_assessment' AND target_id=? ORDER BY created_at,id LIMIT 1",
        (assessment_id,)).fetchone()
    if anchor_row is None:
        raise AppError("MIGRATION_ASSESSMENT_INTEGRITY", "The assessment has no create-time integrity anchor.", 409)
    try:
        anchor = json.loads(anchor_row["result_json"])
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise AppError("MIGRATION_ASSESSMENT_INTEGRITY", "The assessment create-time integrity anchor is invalid.", 409) from exc
    if not isinstance(anchor, dict) or anchor.get("assessment_digest") != actual:
        raise AppError("MIGRATION_ASSESSMENT_INTEGRITY", "Saved assessment content differs from its create-time integrity anchor.", 409)
    return actual


def _staleness(connection, header, configuration):
    reasons = []
    baseline = connection.execute("SELECT baseline_version FROM app_meta WHERE singleton=1").fetchone()
    if baseline is None or baseline["baseline_version"] != header["baseline_version"]:
        reasons.append("baseline_changed")
    authority = _parse_authority_lineage(header["authority_revision"])
    if (authority["config_revision"] != configuration.revision
            or authority["config_digest"] != configuration.digest):
        reasons.append("authority_changed")
    if header["policy_revision"] != configuration.policy_revision:
        reasons.append("policy_changed")
    batch = connection.execute("SELECT source_id FROM source_batches WHERE id=?", (header["source_batch_id"],)).fetchone()
    if batch is None:
        reasons.append("source_missing")
    else:
        scopes = []
        for row in connection.execute(
                "SELECT typed_json FROM source_records WHERE batch_id=? ORDER BY row_number",
                (header["source_batch_id"],)):
            try:
                typed = json.loads(row["typed_json"])
            except (TypeError, ValueError, json.JSONDecodeError):
                continue
            if typed.get("inventory_group") == "scopes" and isinstance(typed.get("record"), dict):
                scopes.append(typed["record"].get("id"))
        try:
            current_mapping = _mapping_lineage(configuration, batch["source_id"], header["domain"], scopes)
        except AppError:
            current_mapping = None
        if not scopes or current_mapping != header["mapping_revision"]:
            reasons.append("mapping_changed")
    return reasons


def _assert_current_domain(context, domain):
    access.require_domain_access(context, domain)


def _receipt(connection, context, domain, action, idempotency_key, request_digest):
    row = connection.execute(
        "SELECT request_digest,result_json FROM tier_a_operation_receipts "
        "WHERE principal_id=? AND domain=? AND action=? AND idempotency_key=?",
        (context.principal_id, domain, action, idempotency_key)).fetchone()
    if row is None:
        return None
    if row["request_digest"] != request_digest:
        raise AppError("IDEMPOTENCY_CONFLICT", "This operation key already identifies different content.", 409)
    try:
        result = json.loads(row["result_json"])
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise AppError("MIGRATION_ASSESSMENT_INTEGRITY", "The saved operation receipt is invalid.", 409) from exc
    if not isinstance(result, dict) or not isinstance(result.get("assessment_id"), str):
        raise AppError("MIGRATION_ASSESSMENT_INTEGRITY", "The saved operation receipt is invalid.", 409)
    return result


def _save_receipt(connection, context, domain, action, idempotency_key, request_digest,
                   target_id, result, now):
    connection.execute(
        "INSERT INTO tier_a_operation_receipts(id,principal_id,domain,action,idempotency_key,request_digest,"
        "target_kind,target_id,result_json,created_at) VALUES (?,?,?,?,?,?,'migration_assessment',?,?,?)",
        (str(uuid4()), context.principal_id, domain, action, idempotency_key, request_digest,
         target_id, _json(result), now))


def _assessment_projection(connection, header, configuration):
    source = connection.execute(
        "SELECT id,source_id,source_run_id,source_kind,envelope_hash,ingested_at FROM source_batches WHERE id=?",
        (header["source_batch_id"],)).fetchone()
    reasons = _staleness(connection, header, configuration)
    return {"id": header["id"], "source_batch_id": header["source_batch_id"],
            "source": dict(source) if source is not None else None,
            "canonical_hash": header["canonical_hash"], "domain": header["domain"],
            "mapping_revision": header["mapping_revision"], "authority_revision": header["authority_revision"],
            "policy_revision": header["policy_revision"], "baseline_version": header["baseline_version"],
            "input_count": header["input_count"], "accepted_count": header["accepted_count"],
            "rejected_count": header["rejected_count"], "duplicate_count": header["duplicate_count"],
            "added_count": header["added_count"], "changed_count": header["changed_count"],
            "unchanged_count": header["unchanged_count"], "conflicting_count": header["conflicting_count"],
            "active_only_acknowledged": bool(header["active_only_acknowledged"]),
            "active_only_count": connection.execute(
                "SELECT count(*) FROM migration_assessment_active_only WHERE assessment_id=?", (header["id"],)).fetchone()[0],
            "created_by": header["created_by"], "created_at": header["created_at"],
            "version": header["version"], "state": header["state"], "signer_id": header["signer_id"],
            "signed_at": header["signed_at"], "signoff_reason": header["signoff_reason"],
            "supersedes_id": header["supersedes_id"], "supersedes_reason": header["supersedes_reason"],
            "digest": assessment_digest(connection, header["id"]),
            "current": not reasons, "staleness_reasons": reasons}


def create_assessment(connection, *, source_batch_id, expected_baseline_version, idempotency_key,
                      reason, context, configuration, supersedes_id=None, supersedes_reason=None, now=None):
    """Compare one complete staged candidate. Caller must hold BEGIN IMMEDIATE.

    The source envelope and parser receipt are reused verbatim; the only writes
    are immutable comparison rows, the assessment header and its operation receipt.
    """
    access.require_role(context, "operator")
    _require_configuration_context(context, configuration)
    domain = _domain(context)
    source_batch_id = _required_text(source_batch_id, "source_batch_id", 64)
    expected_baseline_version = _positive_version(expected_baseline_version, "expected_baseline_version")
    idempotency_key = _required_text(idempotency_key, "idempotency_key", 200)
    reason = _required_text(reason, "reason")
    if supersedes_id is not None:
        supersedes_id = _required_text(supersedes_id, "supersedes_id", 64)
        supersedes_reason = _required_text(supersedes_reason, "supersedes_reason")
    elif supersedes_reason is not None:
        raise AppError("INVALID_INPUT", "supersedes_reason requires supersedes_id.", 422,
                       {"field": "supersedes_reason"})
    request_digest = _digest({"source_batch_id": source_batch_id,
                              "expected_baseline_version": expected_baseline_version, "reason": reason,
                              "supersedes_id": supersedes_id, "supersedes_reason": supersedes_reason,
                              "authority_revision": _config_lineage(configuration),
                              "policy_revision": configuration.policy_revision})
    replay = _receipt(connection, context, domain, _ACTION_CREATE, idempotency_key, request_digest)
    if replay is not None:
        header = connection.execute("SELECT * FROM migration_assessments WHERE id=? AND domain=?",
                                    (replay["assessment_id"], domain)).fetchone()
        if header is None:
            raise AppError("NOT_FOUND", "Migration assessment was not found in the selected domain.", 404)
        return {**_assessment_projection(connection, header, configuration), "replayed": True}

    batch, candidate, receipt_counts, mapping_revision = _load_candidate(
        connection, source_batch_id, context, configuration)
    if supersedes_id is not None and connection.execute(
            "SELECT 1 FROM migration_assessments WHERE id=? AND domain=?", (supersedes_id, domain)).fetchone() is None:
        raise AppError("NOT_FOUND", "Migration assessment was not found in the selected domain.", 404)
    meta = connection.execute("SELECT baseline_version FROM app_meta WHERE singleton=1").fetchone()
    if meta is None or meta["baseline_version"] != expected_baseline_version:
        raise AppError("STALE_INVENTORY", "Active inventory changed after review. Reload and assess again.", 409,
                       {"baseline_version": meta["baseline_version"] if meta else None})
    accepted_rows, active_only, compare_counts = _compare(connection, domain, candidate)
    input_count = receipt_counts["accepted"] + receipt_counts["rejected"] + receipt_counts["duplicate"]
    if (input_count != receipt_counts["accepted"] + receipt_counts["rejected"] + receipt_counts["duplicate"]
            or receipt_counts["accepted"] != sum(compare_counts.values())):
        raise AppError("MIGRATION_ACCOUNTING_INVALID", "The migration comparison did not reconcile every accepted source row.", 409)

    assessment_id = str(uuid4())
    created_at = now or _now()
    state = "validated" if compare_counts["conflicting"] == 0 else "assessed"
    connection.execute(
        "INSERT INTO migration_assessments(id,source_batch_id,canonical_hash,domain,mapping_revision,authority_revision,"
        "policy_revision,baseline_version,input_count,accepted_count,rejected_count,duplicate_count,added_count,changed_count,"
        "unchanged_count,conflicting_count,created_by,created_at,state,supersedes_id,supersedes_reason) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (assessment_id, batch["id"], batch["envelope_hash"], domain, mapping_revision,
         _config_lineage(configuration), configuration.policy_revision, expected_baseline_version,
         input_count, receipt_counts["accepted"], receipt_counts["rejected"], receipt_counts["duplicate"],
         compare_counts["added"], compare_counts["changed"], compare_counts["unchanged"],
         compare_counts["conflicting"], context.principal_id, created_at, state, supersedes_id, supersedes_reason))
    for item in accepted_rows:
        connection.execute(
            "INSERT INTO migration_assessment_rows(id,assessment_id,source_record_id,matching_key,candidate_json,active_json,disposition,reason) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (str(uuid4()), assessment_id, item["source_record_id"], item["matching_key"],
             _json(item["candidate"]), _json(item["active"]) if item["active"] is not None else None,
             item["disposition"], item["reason"]))
    for item in active_only:
        connection.execute(
            "INSERT INTO migration_assessment_active_only(id,assessment_id,matching_key,active_json,reason) VALUES (?,?,?,?,?)",
            (str(uuid4()), assessment_id, item["matching_key"], _json(item["active"]), item["reason"]))
    header = connection.execute("SELECT * FROM migration_assessments WHERE id=?", (assessment_id,)).fetchone()
    create_digest = _assessment_content_digest(connection, assessment_id)
    _save_receipt(connection, context, domain, _ACTION_CREATE, idempotency_key, request_digest,
                  assessment_id, {"assessment_id": assessment_id,
                                  "assessment_digest": create_digest}, created_at)
    result = _assessment_projection(connection, header, configuration)
    audit_event(connection, actor_id=context.principal_id, action="migration.assessment.created", outcome="succeeded",
                reason=reason, subject_id=assessment_id,
                details={"assessment_id": assessment_id, "source_batch_id": batch["id"],
                         "baseline_version": expected_baseline_version, "digest": result["digest"],
                         "input_count": input_count, "accepted_count": receipt_counts["accepted"],
                         "rejected_count": receipt_counts["rejected"], "duplicate_count": receipt_counts["duplicate"],
                         **compare_counts})
    return result


def _authorized_assessment(connection, assessment_id, context):
    domain = _domain(context)
    row = connection.execute("SELECT * FROM migration_assessments WHERE id=?", (assessment_id,)).fetchone()
    if row is None:
        raise AppError("NOT_FOUND", "Migration assessment was not found in the selected domain.", 404)
    _assert_current_domain(context, row["domain"])
    return row


def get_assessment(connection, assessment_id, *, context, configuration):
    """Return one domain-owned immutable assessment with current staleness derived."""
    access.require_role(context, "viewer")
    _require_configuration_context(context, configuration)
    header = _authorized_assessment(connection, assessment_id, context)
    projection = _assessment_projection(connection, header, configuration)
    projection["rows"] = [{"source_record_id": row["source_record_id"], "matching_key": row["matching_key"],
                            "candidate": json.loads(row["candidate_json"]),
                            "active": json.loads(row["active_json"]) if row["active_json"] is not None else None,
                            "disposition": row["disposition"], "reason": row["reason"]}
                           for row in _assessment_rows(connection, assessment_id)]
    projection["active_only"] = [{"matching_key": row["matching_key"],
                                  "active": json.loads(row["active_json"]), "reason": row["reason"]}
                                 for row in _active_only_rows(connection, assessment_id)]
    return projection


def list_assessments(connection, *, context, configuration):
    """List only selected-domain assessment summaries; never return foreign totals."""
    access.require_role(context, "viewer")
    _require_configuration_context(context, configuration)
    domain = _domain(context)
    return [_assessment_projection(connection, row, configuration) for row in connection.execute(
        "SELECT * FROM migration_assessments WHERE domain=? ORDER BY created_at DESC,id DESC", (domain,))]


def signoff_assessment(connection, assessment_id, *, expected_version, expected_digest,
                       active_only_acknowledged, idempotency_key, reason, context,
                       configuration, now=None):
    """Independently sign an exact, current, fully reconciled assessment.

    Caller must hold BEGIN IMMEDIATE. The approval and operation receipt are atomic.
    """
    access.require_role(context, "approver")
    _require_configuration_context(context, configuration)
    header = _authorized_assessment(connection, assessment_id, context)
    expected_version = _positive_version(expected_version, "expected_version")
    expected_digest = _required_text(expected_digest, "expected_digest", 64)
    idempotency_key = _required_text(idempotency_key, "idempotency_key", 200)
    reason = _required_text(reason, "reason")
    if type(active_only_acknowledged) is not bool:
        raise AppError("INVALID_INPUT", "active_only_acknowledged must be a boolean.", 422,
                       {"field": "active_only_acknowledged"})
    request_digest = _digest({"assessment_id": assessment_id, "expected_version": expected_version,
                              "expected_digest": expected_digest,
                              "active_only_acknowledged": active_only_acknowledged, "reason": reason})
    domain = header["domain"]
    replay = _receipt(connection, context, domain, _ACTION_SIGNOFF, idempotency_key, request_digest)
    if replay is not None:
        current = _authorized_assessment(connection, replay["assessment_id"], context)
        original = {key: replay[key] for key in ("assessment_id", "assessment_digest", "signer_id", "signed_at", "signed_version")
                    if key in replay}
        return {"assessment": _assessment_projection(connection, current, configuration),
                "original_signoff": original, "replayed": True}
    if header["created_by"] == context.principal_id:
        raise AppError("SELF_APPROVAL_FORBIDDEN", "A different authenticated principal must sign this assessment.", 403)
    if header["version"] != expected_version or assessment_digest(connection, assessment_id) != expected_digest:
        raise AppError("STALE_ASSESSMENT", "The assessment changed after review. Reload it before signing.", 409)
    stale = _staleness(connection, header, configuration)
    if stale:
        raise AppError("STALE_ASSESSMENT", "The assessment is no longer current. Reassess against current inventory and configuration.", 409,
                       {"reasons": stale})
    if header["state"] == "signed":
        raise AppError("ASSESSMENT_ALREADY_SIGNED", "This assessment already has an immutable sign-off.", 409)
    if header["rejected_count"] != 0 or header["conflicting_count"] != 0:
        raise AppError("ASSESSMENT_NOT_SIGNABLE", "This assessment has rejected input or unresolved conflicts.", 409)
    if header["input_count"] != header["accepted_count"] + header["rejected_count"] + header["duplicate_count"]:
        raise AppError("MIGRATION_ACCOUNTING_INVALID", "The assessment receipt counts do not reconcile.", 409)
    if header["accepted_count"] != header["added_count"] + header["changed_count"] + header["unchanged_count"] + header["conflicting_count"]:
        raise AppError("MIGRATION_ACCOUNTING_INVALID", "The comparison counts do not reconcile.", 409)
    if not active_only_acknowledged:
        raise AppError("ACTIVE_ONLY_ACK_REQUIRED", "Review and acknowledge the separate active-only inventory list before signing.", 422)
    if header["duplicate_count"]:
        raise AppError("DUPLICATE_EXPLANATION_REQUIRED", "Duplicate source rows require an explained review before sign-off.", 409)
    now = now or _now()
    updated_cursor = connection.execute(
        "UPDATE migration_assessments SET active_only_acknowledged=1,state='signed',signer_id=?,signed_at=?,"
        "signoff_reason=?,version=version+1 WHERE id=? AND version=? AND state IN ('assessed','validated')",
        (context.principal_id, now, reason, assessment_id, expected_version))
    if updated_cursor.rowcount != 1:
        raise AppError("STALE_ASSESSMENT", "The assessment changed before sign-off could be recorded.", 409)
    updated = _authorized_assessment(connection, assessment_id, context)
    if updated["signer_id"] != context.principal_id or updated["state"] != "signed":
        raise AppError("STALE_ASSESSMENT", "The assessment changed before sign-off could be recorded.", 409)
    projection = _assessment_projection(connection, updated, configuration)
    _save_receipt(connection, context, domain, _ACTION_SIGNOFF, idempotency_key, request_digest,
                  assessment_id, {"assessment_id": assessment_id, "assessment_digest": expected_digest,
                                  "signer_id": context.principal_id, "signed_at": now,
                                  "signed_version": updated["version"]}, now)
    audit_event(connection, actor_id=context.principal_id, action="migration.assessment.signed", outcome="succeeded",
                reason=reason, subject_id=assessment_id,
                details={"assessment_id": assessment_id, "digest": expected_digest,
                         "baseline_version": updated["baseline_version"], "version": updated["version"],
                         "active_only_acknowledged": True})
    return projection


def assessment_export(connection, assessment_id, *, context, configuration):
    """Return the same sanitized, selected-domain assessment detail as the UI read."""
    return get_assessment(connection, assessment_id, context=context, configuration=configuration)
