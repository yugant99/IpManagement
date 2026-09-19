"""Pinned rich-v1 assets and read-only eligibility for scheduled synthetic input."""

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import os
from pathlib import Path

from ipam_synthetic_feed import build_cycle

from .errors import AppError
from .imports import (MAX_IMPORT_BYTES, MAX_IMPORT_ROWS, _coverage, _fields,
                      _identities, _json, _normalized, _object_pairs, _typed_record)


FEED_VERSION = "ipam-evolving-v1"
BASELINE_CLOCK = "2026-09-01T00:00:00.000Z"
MAX_CYCLE_INDEX = 1460
_ANCHOR = datetime(2026, 9, 1, tzinfo=timezone.utc)
# Exact committed rich-v1 bytes, not pack.json or expected-outcomes.json input.
_ASSETS = (
    ("inventory-policy.json", "synthetic-inventory-policy", "e9ed225610214409a436b8985080d732985f0bc08624dc42bbb9789b0afcf8a4"),
    ("observations/dhcp-north.json", "synthetic-dhcp-north", "f24f12d1bf6cd7c5461012255de58839222b1f7ad5687e0b0c98a93402945e59"),
    ("observations/dhcp-coastal.json", "synthetic-dhcp-coastal", "3a67e9f16167fb83e669b8869d01422718b53a2241abdaad0f6491de84020007"),
    ("observations/dhcp-central.json", "synthetic-dhcp-central", "43e1b8e0458180e165559766de2f75552003464d46590460643edca5db88f012"),
    ("observations/dhcp-lab.json", "synthetic-dhcp-lab", "e5f3bf9cbb371bf07a92da48c49919106e3cc8511efbd4e69a104da24d17b018"),
    ("observations/routing-north.json", "synthetic-routing-north", "b7a4e3b9befcc8f90408c80b06118f957bdd95cf49af90ad17a086c7a17f7420"),
    ("observations/routing-coastal.json", "synthetic-routing-coastal", "24d0f252e4fde9fe8ca7089688d10c2d03a3f707e58e68de6954e51d934e1df2"),
    ("observations/routing-central.json", "synthetic-routing-central", "c286fad37e99187cefe525e9bc65bf51bb317d895e91dcb289b7c09d9b2c242b"),
    ("observations/routing-lab.json", "synthetic-routing-lab", "ed6b7bdfb7dffc811c75871f431fad7a5439a399045efb2d1c142ab0c14cd050"),
)


def _clock(index):
    if type(index) is not int or not 0 <= index <= MAX_CYCLE_INDEX:
        raise ValueError("Cycle index must be an integer from 0 through 1460; the scenario never wraps.")
    return (_ANCHOR + timedelta(hours=6 * index)).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _sources(baseline):
    if not isinstance(baseline, list) or len(baseline) != len(_ASSETS):
        raise ValueError("Supply the nine pinned rich-v1 baseline envelopes.")
    sources = {}
    for envelope, (_, source_id, fingerprint) in zip(baseline, _ASSETS):
        # The original generator's serialization preserves parsed key order.
        body = (json.dumps(envelope, indent=2, ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")
        if sha256(body).hexdigest() != fingerprint:
            raise ValueError("Baseline content changed or is out of order: " + source_id)
        sources[source_id] = envelope
    return sources


def load_baseline() -> list[dict]:
    """Read exactly the named files from the explicitly configured read-only asset root."""
    configured = os.environ.get("IPAM_SYNTHETIC_FEED_DIR")
    if not configured or not configured.strip():
        raise AppError("SYNTHETIC_FEED_UNAVAILABLE", "Set IPAM_SYNTHETIC_FEED_DIR to the immutable rich-v1 asset directory.")
    try:
        directory = Path(configured).expanduser().resolve(strict=True)
        baseline = []
        for relative, source_id, fingerprint in _ASSETS:
            with (directory / relative).open("rb") as source:
                body = source.read(MAX_IMPORT_BYTES + 1)
            if len(body) > MAX_IMPORT_BYTES or sha256(body).hexdigest() != fingerprint:
                raise ValueError("Missing or changed pinned rich-v1 asset: " + relative)
            envelope = json.loads(body, object_pairs_hook=_object_pairs)
            if not isinstance(envelope, dict) or envelope.get("source_id") != source_id:
                raise ValueError("Unexpected logical source in " + relative)
            baseline.append(envelope)
        return baseline
    except (OSError, ValueError, UnicodeError, RecursionError) as exc:
        raise AppError("SYNTHETIC_FEED_UNAVAILABLE", "The pinned synthetic feed assets could not be loaded.",
                       details={"reason": str(exc)}) from exc


def prepare_cycle(index: int, baseline: list[dict]) -> dict:
    """Build and validate a complete bundle before the scheduler's write transaction."""
    try:
        clock = _clock(index)
        sources = _sources(baseline)
        bundle = build_cycle(index, baseline)
        _sources(baseline)  # A producer must not change caller-owned baseline content.
        _fields(bundle, {"feed_version", "cycle_index", "cycle_id", "demo_clock_at", "envelopes"}, "cycle")
        cycle_id = f"evolving-v1-{index:06d}"
        if (bundle["feed_version"] != FEED_VERSION or type(bundle["cycle_index"]) is not int
                or bundle["cycle_index"] != index or bundle["cycle_id"] != cycle_id
                or bundle["demo_clock_at"] != clock):
            raise ValueError("Producer returned an incompatible cycle identity or scenario clock.")
        envelopes = bundle["envelopes"]
        if not isinstance(envelopes, list) or len(envelopes) != len(sources):
            raise ValueError("A cycle must contain all nine source envelopes.")
        scopes = {row["scope_id"] for row in baseline[0]["coverage"]}
        prefixes = {row["prefix_id"]: row["scope_id"] for row in baseline[0]["records"]}
        history_start = (_ANCHOR + timedelta(hours=6 * index, days=-30)).isoformat(
            timespec="milliseconds").replace("+00:00", "Z")
        seen = set()
        for envelope in envelopes:
            if not isinstance(envelope, dict) or envelope.get("source_id") not in sources:
                raise ValueError("Unexpected synthetic logical source.")
            source_id = envelope["source_id"]
            if source_id in seen:
                raise ValueError("A cycle contains duplicate logical sources.")
            seen.add(source_id)
            original = sources[source_id]
            _fields(envelope, set(original), "envelope")
            mutable = {"demo_clock_at", "source_run_id", "coverage", "records"}
            if any(envelope[key] != value for key, value in original.items() if key not in mutable):
                raise ValueError("The producer changed immutable source declarations: " + source_id)
            if envelope["source_run_id"] != cycle_id or envelope["demo_clock_at"] != clock:
                raise ValueError("Every envelope must use the cycle identity and scenario clock.")
            kind = "route_policy" if envelope["source_kind"] == "inventory_policy" else envelope["source_kind"]
            coverage = _coverage(envelope, kind, scopes, clock)
            if {row["scope_id"] for row in coverage} != {row["scope_id"] for row in original["coverage"]}:
                raise ValueError("A cycle changed logical source scope coverage.")
            if kind == "route_policy":
                if envelope["records"] != original["records"] or not all(row["declared_complete"] for row in coverage):
                    raise ValueError("The cycle must reassert the complete unchanged intended policy.")
            elif any(row["window_start_at"] != history_start or row["window_end_at"] > clock for row in coverage):
                raise ValueError("Observation coverage must retain the rolling 30-day window without future evidence.")
            records = envelope["records"]
            if not isinstance(records, list) or len(records) > MAX_IMPORT_ROWS:
                raise ValueError("The cycle exceeds the importer record limit.")
            if len(_json(envelope).encode("utf-8")) > MAX_IMPORT_BYTES:
                raise ValueError("The cycle exceeds the importer byte limit.")
            declared = {row["scope_id"] for row in coverage}
            identities = set()
            for record in records:
                _typed_record(record, kind, declared, prefixes, clock, envelope.get("effective_from_at"))
                for identity in _identities(record, kind):
                    if identity in identities:
                        raise ValueError("A cycle contains duplicate or conflicting record identities.")
                    identities.add(identity)
        return bundle
    except (ValueError, KeyError, TypeError, AttributeError, UnicodeError, RecursionError) as exc:
        raise AppError("INVALID_SYNTHETIC_CYCLE", "The synthetic cycle could not be prepared; no data was changed.", 422,
                       {"reason": str(exc)}) from exc


def require_compatible(connection, baseline: list[dict], cycle_index: int) -> None:
    """Check the committed cursor and authority without altering any stored evidence.

    Scope/perimeter and original prefix identities/bounds must remain compatible.
    Metadata edits, additional prefixes and local allocation changes are retained.
    The scheduler calls this again under BEGIN IMMEDIATE before changing the clock.
    """
    try:
        expected_clock = _clock(cycle_index)
        sources = _sources(baseline)
        meta = connection.execute("SELECT initialized,scenario,demo_clock_at,seed_envelope FROM app_meta WHERE singleton=1").fetchone()
        if meta is None or not meta["initialized"]:
            raise ValueError("Initialize the explicit rich intended inventory before scheduling.")
        seed = json.loads(meta["seed_envelope"])
        if (seed.get("source_id") != "synthetic-inventory-rich" or seed.get("source_run_id") != "rich-v1-inventory"
                or seed.get("demo_clock_at") != BASELINE_CLOCK or seed.get("scenario") != "baseline"
                or type(seed.get("schema_version")) is not int or seed["schema_version"] != 1
                or meta["scenario"] != "baseline"):
            raise ValueError("Scheduling requires the original rich-v1 seed identity and baseline clock.")
        if meta["demo_clock_at"] != expected_clock:
            raise ValueError("Stored scenario clock differs from the committed synthetic cycle cursor.")
        policy = sources["synthetic-inventory-policy"]
        expected_scopes = {row["scope_id"] for row in policy["coverage"]}
        seed_scopes = {row["id"]: row for row in seed["scopes"]}
        if set(seed_scopes) != expected_scopes or len(seed_scopes) != len(seed["scopes"]):
            raise ValueError("Rich seed scopes differ from the pinned feed.")
        current_scopes = {row["id"]: row for row in connection.execute("SELECT * FROM scopes")}
        for scope_id, original in seed_scopes.items():
            current = current_scopes.get(scope_id)
            if (current is None or current["namespace"] != original["namespace"]
                    or json.loads(current["managed_cidrs"]) != original["managed_cidrs"]):
                raise ValueError("A feed scope or its managed perimeter changed: " + scope_id)
        seed_prefixes = {row["id"]: row for row in seed["prefixes"]}
        if (set(seed_prefixes) != {row["prefix_id"] for row in policy["records"]}
                or len(seed_prefixes) != len(seed["prefixes"])
                or any(seed_prefixes[row["prefix_id"]]["scope_id"] != row["scope_id"] for row in policy["records"])):
            raise ValueError("Rich seed prefixes differ from the pinned intended-policy coverage.")
        current_prefixes = {row["id"]: row for row in connection.execute("SELECT * FROM prefixes")}
        for prefix_id, original in seed_prefixes.items():
            current = current_prefixes.get(prefix_id)
            if current is None or any(current[field] != original[field] for field in ("scope_id", "family", "cidr", "parent_id")):
                raise ValueError("An original feed prefix changed identity, scope, bounds or hierarchy: " + prefix_id)

        # Only transactionally committed scheduler operations can authorize later runs.
        committed = {}
        cycles = set()
        for row in connection.execute("SELECT result_json FROM schedule_operations"):
            result = json.loads(row["result_json"])
            index = result["cycle_index"]
            if (type(index) is not int or not 1 <= index <= cycle_index or index in cycles
                    or result["feed_version"] != FEED_VERSION or result["demo_clock_at"] != _clock(index)
                    or result["cycle_id"] != f"evolving-v1-{index:06d}"):
                raise ValueError("Committed scheduling provenance differs from the current feed cursor.")
            batch_ids = result["batch_ids"]
            if (not isinstance(batch_ids, list) or len(batch_ids) != len(sources)
                    or any(not isinstance(value, str) for value in batch_ids)
                    or len(set(batch_ids)) != len(batch_ids)):
                raise ValueError("A committed cycle does not identify all nine source batches.")
            cycles.add(index)
            for batch_id in batch_ids:
                if batch_id in committed:
                    raise ValueError("A source batch is claimed by multiple cycles.")
                committed[batch_id] = result
        if cycles != set(range(1, cycle_index + 1)):
            raise ValueError("The synthetic cursor has missing committed acquisition provenance.")
        baseline_hashes = {source_id: sha256(_json(_normalized(envelope)).encode("utf-8")).hexdigest()
                           for source_id, envelope in sources.items()}
        found = set()
        cycle_sources = {index: set() for index in cycles}
        coverage_scopes = {}
        for row in connection.execute("SELECT batch_id,scope_id FROM source_coverage"):
            coverage_scopes.setdefault(row["batch_id"], set()).add(row["scope_id"])
        for row in connection.execute(
                "SELECT id,source_id,source_run_id,source_kind,envelope_hash,demo_clock_at FROM source_batches"):
            source_id = row["source_id"]
            if row["source_kind"] == "inventory_staged" and source_id not in sources:
                continue
            if source_id not in sources:
                raise ValueError("Competing source authority must be resolved before scheduling: " + source_id)
            original = sources[source_id]
            kind = "route_policy" if original["source_kind"] == "inventory_policy" else original["source_kind"]
            declared = coverage_scopes.get(row["id"], set())
            if row["source_kind"] != kind or declared != {coverage["scope_id"] for coverage in original["coverage"]}:
                raise ValueError("An existing logical source has incompatible kind or coverage: " + source_id)
            operation = committed.get(row["id"])
            if operation is not None:
                if row["source_run_id"] != operation["cycle_id"] or row["demo_clock_at"] != operation["demo_clock_at"]:
                    raise ValueError("An acquired source differs from its committed scheduling provenance.")
                if source_id in cycle_sources[operation["cycle_index"]]:
                    raise ValueError("A committed cycle repeats a source instead of acquiring all nine.")
                cycle_sources[operation["cycle_index"]].add(source_id)
                found.add(row["id"])
            elif (row["source_run_id"] != original["source_run_id"] or row["envelope_hash"] != baseline_hashes[source_id]
                  or row["demo_clock_at"] != BASELINE_CLOCK):
                raise ValueError("An unowned source run competes with the synthetic feed: " + source_id + "/" + row["source_run_id"])
        if found != set(committed):
            raise ValueError("Committed acquisition provenance references missing source evidence.")
    except (ValueError, KeyError, TypeError, AttributeError, UnicodeError, RecursionError) as exc:
        raise AppError("SYNTHETIC_FEED_INCOMPATIBLE", "Scheduling refused incompatible inventory, clock or source authority.",
                       409, {"reason": str(exc)}) from exc
