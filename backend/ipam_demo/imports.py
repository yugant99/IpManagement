"""Bounded synthetic imports with immutable input, receipts and row evidence."""

from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
from ipaddress import ip_network
import json
import math
import re
from uuid import UUID, uuid4

from .errors import AppError

MAX_IMPORT_BYTES = 10 * 1024 * 1024
MAX_IMPORT_ROWS = 10_000
_TIMESTAMP_FIELDS = {"demo_clock_at", "effective_from_at", "window_start_at", "window_end_at",
                     "observed_at", "valid_from_at", "valid_until_at"}
_TIMESTAMP_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)\Z"
)


def _json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def _timestamp(value, field: str) -> str:
    if not isinstance(value, str) or not _TIMESTAMP_PATTERN.fullmatch(value):
        raise ValueError(f"{field} must be an ISO timestamp with an explicit timezone")
    try:
        instant = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except (ValueError, OverflowError) as exc:
        raise ValueError(f"{field} is not a valid timestamp") from exc
    if instant.microsecond % 1000:
        raise ValueError(f"{field} must be exactly representable at millisecond precision")
    return instant.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _normalized(value, field=None):
    """Hash valid timestamps consistently, including rejected rows; retain invalid values."""
    for text in (field, value):
        if isinstance(text, str) and any(0xD800 <= ord(character) <= 0xDFFF for character in text):
            raise ValueError("JSON keys and string values must contain valid Unicode, without lone surrogates")
    if field in _TIMESTAMP_FIELDS:
        try:
            return _timestamp(value, field)
        except ValueError:
            pass
    if isinstance(value, dict):
        return {key: _normalized(item, key) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalized(item) for item in value]
    return value


def _text(value, field: str, maximum=512) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f"{field} must be a nonempty string of at most {maximum} characters")
    if any(ord(character) < 32 or 0xD800 <= ord(character) <= 0xDFFF for character in value):
        raise ValueError(f"{field} must not contain control characters or invalid Unicode")
    return value


def _uuid(value, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a UUID string")
    try:
        return str(UUID(value))
    except ValueError as exc:
        raise ValueError(f"{field} must be a UUID string") from exc


def _fields(value, expected: set[str], label: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    missing, extra = expected - value.keys(), value.keys() - expected
    if missing or extra:
        details = []
        if missing:
            details.append("missing fields: " + ", ".join(sorted(missing)))
        if extra:
            details.append("unsupported fields: " + _json(sorted(extra)))
        raise ValueError(f"{label}: {'; '.join(details)}")


def _boolean(value, field: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{field} must be a boolean")
    return value


def _object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {ascii(key)}")
        result[key] = value
    return result


def _finite_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("JSON numbers must be finite")
    return result


def _reject_constant(value):
    raise ValueError(f"Unsupported JSON constant: {value}")


def _coverage(envelope, kind, scopes, clock) -> list[dict]:
    values = envelope["coverage"]
    if not isinstance(values, list) or not values:
        raise ValueError("coverage must explicitly declare at least one scope")
    result, seen = [], set()
    for value in values:
        _fields(value, {"scope_id", "kind", "window_start_at", "window_end_at", "declared_complete"}, "coverage")
        scope_id = _uuid(value["scope_id"], "coverage.scope_id")
        if scope_id not in scopes:
            raise ValueError("coverage.scope_id is not registered in the intended inventory")
        if scope_id in seen:
            raise ValueError("coverage must declare each scope exactly once")
        seen.add(scope_id)
        start = _timestamp(value["window_start_at"], "coverage.window_start_at")
        end = _timestamp(value["window_end_at"], "coverage.window_end_at")
        if kind == "routing":
            if value["kind"] != "interval" or start >= end:
                raise ValueError("Routing coverage must be an interval with start before end")
        elif value["kind"] != "snapshot" or start != clock or end != clock:
            raise ValueError("Policy coverage must be a snapshot with both bounds at the demo clock")
        complete = _boolean(value["declared_complete"], "coverage.declared_complete")
        result.append({"scope_id": scope_id, "kind": value["kind"], "window_start_at": start,
                       "window_end_at": end, "declared_complete": complete, "effective_complete": complete})
    return result


def _typed_record(record, kind, declared_scopes, prefixes, clock, effective_from_at):
    common = {"source_record_id", "scope_id"}
    if kind == "routing":
        expected = common | {"id", "family", "cidr", "router_id", "valid_from_at", "valid_until_at",
                             "observed_at", "original_timestamps"}
    else:
        expected = common | {"prefix_id", "expects_announcement", "route_match_policy"}
    _fields(record, expected, "record")
    source_record_id = _text(record["source_record_id"], "source_record_id")
    scope_id = _uuid(record["scope_id"], "scope_id")
    if scope_id not in declared_scopes:
        raise ValueError("scope_id is not in this batch's registered coverage")
    result = {**record, "source_record_id": source_record_id, "scope_id": scope_id}
    if kind == "route_policy":
        prefix_id = _uuid(record["prefix_id"], "prefix_id")
        if prefixes.get(prefix_id) != scope_id:
            raise ValueError("prefix_id does not identify an existing prefix in this scope")
        result["prefix_id"] = prefix_id
        result["expects_announcement"] = _boolean(record["expects_announcement"], "expects_announcement")
        if record["route_match_policy"] not in ("exact", "covering"):
            raise ValueError("route_match_policy must be exact or covering")
        result["effective_from_at"] = effective_from_at
        return result
    result["id"] = _uuid(record["id"], "id")
    result["router_id"] = _text(record["router_id"], "router_id")
    if type(record["family"]) is not int or record["family"] not in (4, 6):
        raise ValueError("family must be integer 4 or 6")
    if not isinstance(record["cidr"], str) or "/" not in record["cidr"]:
        raise ValueError("cidr must explicitly include a prefix length")
    try:
        network = ip_network(record["cidr"], strict=True)
    except ValueError as exc:
        raise ValueError("cidr must be a strict network address with no host bits") from exc
    if network.version != record["family"]:
        raise ValueError("family differs from cidr")
    result["cidr"] = str(network)
    time_fields = {"valid_from_at", "valid_until_at", "observed_at"}
    _fields(record["original_timestamps"], time_fields, "original_timestamps")
    for field in time_fields:
        if record["original_timestamps"][field] != record[field]:
            raise ValueError(f"original_timestamps.{field} must retain the input value exactly")
        result[field] = _timestamp(record[field], field)
    if result["valid_from_at"] >= result["valid_until_at"]:
        raise ValueError("Route validity must have start before end")
    if result["valid_from_at"] > clock or result["observed_at"] > clock:
        raise ValueError("Route start and observed_at must not be after the demo clock")
    return result


def _identities(record, kind):
    if not isinstance(record, dict):
        return []
    result = []
    for field in ("source_record_id", "id") if kind == "routing" else ("source_record_id",):
        value = record.get(field)
        if isinstance(value, str) and value:
            if field == "id":
                try:
                    value = _uuid(value, field)
                except ValueError:
                    pass
            result.append((field, value))
    if kind == "route_policy":
        try:
            result.append(("prefix_id", _uuid(record.get("prefix_id"), "prefix_id")))
        except ValueError:
            pass
    return result


def import_envelope(connection, body: bytes) -> tuple[dict, bool]:
    """Caller owns BEGIN IMMEDIATE and commit/rollback; no partial commit occurs here."""
    if len(body) > MAX_IMPORT_BYTES:
        raise AppError("IMPORT_TOO_LARGE", "Import exceeds the 10 MiB limit.", 413)
    try:
        raw_envelope = body.decode("utf-8")
        envelope = json.loads(raw_envelope, object_pairs_hook=_object_pairs,
                              parse_float=_finite_float, parse_constant=_reject_constant)
        if not isinstance(envelope, dict):
            raise ValueError("Import envelope must be an object")
        input_kind = envelope.get("source_kind")
        if input_kind not in ("routing", "inventory_policy"):
            raise ValueError("Only routing and inventory_policy envelopes are supported; inventory, DHCP and expected outcomes are not imported")
        kind = "routing" if input_kind == "routing" else "route_policy"
        expected = {"schema_version", "fixture_contract", "synthetic", "demo_clock_at", "source_id",
                    "source_run_id", "source_kind", "source", "coverage", "records"}
        if kind == "route_policy":
            expected.add("effective_from_at")
        _fields(envelope, expected, "envelope")
        if type(envelope["schema_version"]) is not int or envelope["schema_version"] != 1:
            raise ValueError("schema_version must be integer 1")
        if envelope["fixture_contract"] != "ipam-synthetic-v1" or envelope["synthetic"] is not True:
            raise ValueError("Import must declare the ipam-synthetic-v1 contract and synthetic: true")
        records = envelope["records"]
        if not isinstance(records, list):
            raise ValueError("records must be an array")
        if len(records) > MAX_IMPORT_ROWS:
            raise AppError("IMPORT_TOO_LARGE", "Import exceeds the 10,000 record limit.", 413)
        source_id = _text(envelope["source_id"], "source_id", 200)
        source_run_id = _text(envelope["source_run_id"], "source_run_id", 200)
        fingerprint = sha256(_json(_normalized(envelope)).encode("utf-8")).hexdigest()
        previous = connection.execute(
            "SELECT envelope_hash, receipt_json FROM source_batches WHERE source_id=? AND source_run_id=?",
            (source_id, source_run_id),
        ).fetchone()
        if previous is not None:
            if previous["envelope_hash"] != fingerprint:
                raise AppError("IMPORT_IDENTITY_CONFLICT", "This source/run identity already contains different content.", 409)
            return json.loads(previous["receipt_json"]), True
        previous_kind = connection.execute("SELECT source_kind FROM source_batches WHERE source_id=? LIMIT 1", (source_id,)).fetchone()
        if previous_kind is not None and previous_kind["source_kind"] != kind:
            raise AppError("SOURCE_KIND_CONFLICT", "A source_id cannot change its source kind.", 409)
        meta = connection.execute("SELECT initialized, demo_clock_at FROM app_meta WHERE singleton=1").fetchone()
        if meta is None or not meta["initialized"]:
            raise AppError("SETUP_NEEDED", "Initialize the intended inventory before importing sources.", 503)
        clock = _timestamp(envelope["demo_clock_at"], "demo_clock_at")
        if clock != _timestamp(meta["demo_clock_at"], "seeded demo_clock_at"):
            raise ValueError("demo_clock_at must equal the seeded inventory clock")
        source = envelope["source"]
        _fields(source, {"name", "owner", "authority", "required_for"}, "source")
        _text(source["name"], "source.name", 200)
        _text(source["owner"], "source.owner", 200)
        authority, requirement = (("observed", "routing_view") if kind == "routing" else
                                  ("intended_policy", "route_policy"))
        if source["authority"] != authority or source["required_for"] != [requirement]:
            raise ValueError(f"source must declare authority {authority} and required_for [{requirement}]")
        scopes = {row["id"] for row in connection.execute("SELECT id FROM scopes")}
        coverage = _coverage(envelope, kind, scopes, clock)
        prefixes = {row["id"]: row["scope_id"] for row in connection.execute("SELECT id, scope_id FROM prefixes")}
        normalized_rows = [_json(_normalized(record)) for record in records]
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise AppError("INVALID_IMPORT", "Import envelope is invalid.", 422, {"reason": str(exc)}) from exc

    # A structurally valid replacement policy with unusable effective time must
    # supersede its predecessor, including when it contains zero rows.
    effective_from_at, policy_error = None, None
    if kind == "route_policy":
        try:
            effective_from_at = _timestamp(envelope["effective_from_at"], "effective_from_at")
            if effective_from_at > clock:
                raise ValueError("effective_from_at is after the demo clock")
        except ValueError as exc:
            policy_error = str(exc)

    declared_scopes = {value["scope_id"] for value in coverage}
    groups = defaultdict(list)
    for index, record in enumerate(records):
        for identity in _identities(record, kind):
            groups[identity].append(index)
    conflicts = set()
    for indices in groups.values():
        if len({normalized_rows[index] for index in indices}) > 1:
            conflicts.update(indices)

    rows, seen, incomplete_scopes = [], {}, set()
    counts = {"accepted": 0, "rejected": 0, "duplicate": 0}
    for index, record in enumerate(records):
        typed, reason, status = None, None, "accepted"
        try:
            if policy_error:
                raise ValueError(policy_error)
            if index in conflicts:
                raise ValueError("Conflicting rows share a row ID, source record reference or policy prefix identity; all ambiguous rows are rejected")
            typed = _typed_record(record, kind, declared_scopes, prefixes, clock, effective_from_at)
        except ValueError as exc:
            status, reason = "rejected", str(exc)
            try:
                scope_id = _uuid(record.get("scope_id"), "scope_id") if isinstance(record, dict) else None
            except ValueError:
                scope_id = None
            if kind == "route_policy" or scope_id not in declared_scopes:
                incomplete_scopes.update(declared_scopes)
            else:
                incomplete_scopes.add(scope_id)
        if status == "accepted":
            row_key = normalized_rows[index]
            if row_key in seen:
                status, typed = "duplicate", None
                reason = f"Identical row identity and normalized payload already appears at row {seen[row_key]}"
            else:
                seen[row_key] = index + 1
        reference = record.get("source_record_id") if isinstance(record, dict) else None
        try:
            reference = _text(reference, "source_record_id")
        except ValueError:
            # Invalid references remain exact in raw_json, never coerced into a
            # misleading lookup key or passed as invalid Unicode to SQLite.
            reference = None
        counts[status] += 1
        rows.append({"id": str(uuid4()), "row_number": index + 1,
                     "source_record_id": reference,
                     "status": status, "reason": reason, "raw": record, "typed": typed})
    if policy_error:
        incomplete_scopes.update(declared_scopes)
    for value in coverage:
        if value["scope_id"] in incomplete_scopes:
            value["effective_complete"] = False

    limitations = ["Synthetic source evidence only; this import does not change intended inventory or allocations."]
    if counts["rejected"]:
        limitations.append("Rejected rows are retained; affected declared coverage is incomplete.")
    if policy_error:
        limitations.append("Policy snapshot is unusable: " + policy_error + "; older policy is not a fallback.")
    if any(not value["declared_complete"] for value in coverage):
        limitations.append("The source declared incomplete coverage.")
    batch_id = str(uuid4())
    ingested_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    cursor = connection.execute(
        "INSERT INTO source_batches (id, source_id, source_run_id, source_kind, envelope_hash, envelope_json, receipt_json, ingested_at, demo_clock_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (batch_id, source_id, source_run_id, kind, fingerprint, raw_envelope, "{}", ingested_at, clock),
    )
    receipt = {"id": batch_id, "sequence": cursor.lastrowid, "source_id": source_id, "source_run_id": source_run_id,
               "source_kind": kind, "ingested_at": ingested_at, "demo_clock_at": clock,
               "application_status": "complete" if all(value["effective_complete"] for value in coverage) else "partial",
               "input_rows": len(records), "accepted_rows": counts["accepted"], "rejected_rows": counts["rejected"],
               "duplicate_rows": counts["duplicate"], "synthetic": True, "coverage": coverage, "limitations": limitations}
    connection.execute("UPDATE source_batches SET receipt_json=? WHERE id=?", (_json(receipt), batch_id))
    connection.executemany(
        "INSERT INTO source_coverage (batch_id, scope_id, window_start_at, window_end_at, declared_complete, effective_complete) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [(batch_id, value["scope_id"], value["window_start_at"], value["window_end_at"],
          value["declared_complete"], value["effective_complete"]) for value in coverage],
    )
    connection.executemany(
        "INSERT INTO source_records (id, batch_id, row_number, source_record_id, status, reason, raw_json, typed_json) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [(row["id"], batch_id, row["row_number"], row["source_record_id"], row["status"], row["reason"],
          _json(row["raw"]), _json(row["typed"]) if row["typed"] is not None else None) for row in rows],
    )
    return receipt, False


def record_payload(row) -> dict:
    result = dict(row)
    result["raw"] = json.loads(result.pop("raw_json"))
    typed = result.pop("typed_json")
    result["typed"] = json.loads(typed) if typed is not None else None
    return result
