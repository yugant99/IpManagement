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

# Structural identity copied from the immutable fixtures/v1/inventory.json at
# 907f6e7bf32f23f36d270da49c3177b015c8bfae. Supplied seed content is not authority
# for these fields. Keep this small adapter pin independent of metadata and of
# the nine runtime input files; no inventory file or expected labels are loaded.
_NORTH = "7d2075a0-6fd4-4d58-a26c-1e7d8cb0a001"
_LAB = "7d2075a0-6fd4-4d58-a26c-1e7d8cb0a002"
_COASTAL = "6d3bb4b0-ce20-5d83-b609-c09e3468d891"
_CENTRAL = "2c4a5913-e80c-53e9-9ba1-fd6c87ec6f4c"
_RICH_SCOPES = {
    _NORTH: ("vrf-north", ["10.40.0.0/16", "2001:db8:40::/48"]),
    _LAB: ("vrf-lab", ["10.40.0.0/16"]),
    _COASTAL: ("vrf-coastal", ["10.60.0.0/16", "2001:db8:60::/48"]),
    _CENTRAL: ("vrf-central", ["10.80.0.0/16", "2001:db8:80::/48"]),
}
_NORTH_V4 = "41aca2b0-ec1d-4f64-8d21-c5af0ab0b001"
_NORTH_V6 = "41aca2b0-ec1d-4f64-8d21-c5af0ab0b004"
_COASTAL_V4 = "e18e837e-510f-5b09-a851-a51087a87489"
_COASTAL_V6 = "23e6edda-6196-5302-97a6-c19e99d04ef0"
_CENTRAL_V4 = "f0546fd0-2ea3-58dd-830b-cb463de81b60"
_CENTRAL_V6 = "233afa7e-31ca-550e-8dbc-c821303ccace"
# prefix ID -> (scope ID, family, CIDR, parent ID), including original parents.
_RICH_PREFIXES = {
    _NORTH_V4: (_NORTH, 4, "10.40.0.0/16", None),
    "41aca2b0-ec1d-4f64-8d21-c5af0ab0b002": (_NORTH, 4, "10.40.1.0/24", _NORTH_V4),
    "41aca2b0-ec1d-4f64-8d21-c5af0ab0b003": (_NORTH, 4, "10.40.2.0/28", _NORTH_V4),
    _NORTH_V6: (_NORTH, 6, "2001:db8:40::/48", None),
    "41aca2b0-ec1d-4f64-8d21-c5af0ab0b005": (_NORTH, 6, "2001:db8:40:1::/64", _NORTH_V6),
    "41aca2b0-ec1d-4f64-8d21-c5af0ab0b006": (_LAB, 4, "10.40.1.0/24", None),
    "6bb56af5-eb62-53f1-9703-66dce7d33623": (_NORTH, 4, "10.40.3.0/24", _NORTH_V4),
    "06b7ca61-9adc-5865-a142-61fc9f38a00a": (_NORTH, 4, "10.40.4.0/24", _NORTH_V4),
    "b848db8c-200b-56d9-b083-7d2a81d8dda2": (_NORTH, 4, "10.40.5.0/24", _NORTH_V4),
    "3faaa46b-8fff-53c9-b5ad-56c89c455cae": (_NORTH, 4, "10.40.6.0/24", _NORTH_V4),
    "50053b51-2916-5469-8944-b5f32d1b7063": (_NORTH, 4, "10.40.7.0/24", _NORTH_V4),
    "6b5f7933-c2cc-5fd0-ad59-e7d822927058": (_NORTH, 4, "10.40.8.0/24", _NORTH_V4),
    "cec9cbde-44fa-5725-a1a3-45727d4573f7": (_NORTH, 4, "10.40.9.0/24", _NORTH_V4),
    "7897c78f-f727-5bf4-9686-247e1fa6a34e": (_NORTH, 4, "10.40.10.0/24", _NORTH_V4),
    "28508a12-24a9-5681-b33b-237a67a3bff4": (_NORTH, 4, "10.40.11.0/24", _NORTH_V4),
    "fee3c85a-b68e-5100-b57d-d3eeb3e2b1ac": (_NORTH, 6, "2001:db8:40:2::/64", _NORTH_V6),
    "4ab4b10a-db2b-56c2-abac-a99e7a87f1c6": (_LAB, 4, "10.40.2.0/24", None),
    "14b140fe-307e-5365-adaf-bac676e0b6e3": (_LAB, 4, "10.40.3.0/24", None),
    "2af5a941-2902-5f6f-bcfe-e5b97a47515f": (_LAB, 4, "10.40.4.0/24", None),
    "7aa49ec7-4344-51ca-99bd-e5a39fe49947": (_LAB, 4, "10.40.5.0/24", None),
    "c91da1c9-2907-5ea5-8c81-9e70b0f2a82d": (_LAB, 4, "10.40.6.0/24", None),
    "6fd2ea53-99bc-56bb-bc61-32a3247450f7": (_LAB, 4, "10.40.7.0/24", None),
    "09650578-5d3e-522d-86f3-7edfed65607c": (_LAB, 4, "10.40.8.0/24", None),
    "36a12e50-6ab3-5b36-994b-33294d06ab4d": (_LAB, 4, "10.40.9.0/24", None),
    "d24f9864-e836-5d64-aefb-acd93f365feb": (_LAB, 4, "10.40.10.0/24", None),
    "f83eba1b-08b5-52cc-bb77-95385124d6f6": (_LAB, 4, "10.40.11.0/24", None),
    "0d42da3c-f014-5bb5-b479-5b3001121ee4": (_LAB, 4, "10.40.12.0/24", None),
    "7c1c9878-2946-516c-92d5-f58f078563d3": (_LAB, 4, "10.40.13.0/24", None),
    "bc947f6d-6508-5344-ac33-4d2b7ad2708a": (_LAB, 4, "10.40.14.0/24", None),
    "a1526294-9c3c-5588-98b5-c0fa7cae2aa9": (_LAB, 4, "10.40.15.0/24", None),
    _COASTAL_V4: (_COASTAL, 4, "10.60.0.0/20", None),
    "bf2c1be9-80c5-52e1-948d-182bdab92c26": (_COASTAL, 4, "10.60.1.0/24", _COASTAL_V4),
    "60fe3174-a94e-5a5c-9858-8180c49bb697": (_COASTAL, 4, "10.60.2.0/24", _COASTAL_V4),
    "3a642afc-33a8-5d77-974d-dd6d3ce62a1c": (_COASTAL, 4, "10.60.3.0/24", _COASTAL_V4),
    "fdcf07d5-2059-5358-a0a7-8349a3478748": (_COASTAL, 4, "10.60.4.0/24", _COASTAL_V4),
    "6d4ca11a-c17b-52ce-b75f-6ac3023c4e08": (_COASTAL, 4, "10.60.5.0/24", _COASTAL_V4),
    "f541b894-e689-581e-b321-81cb37ce79a4": (_COASTAL, 4, "10.60.6.0/24", _COASTAL_V4),
    "5ef476fa-209d-52d1-b61a-3cff0c60c1bb": (_COASTAL, 4, "10.60.7.0/24", _COASTAL_V4),
    "a6692c89-bff9-56e6-b09f-25b04cf8e997": (_COASTAL, 4, "10.60.8.0/24", _COASTAL_V4),
    "31f48ebb-2f5f-5cbe-8a79-87adac622dc7": (_COASTAL, 4, "10.60.9.0/24", _COASTAL_V4),
    "4369b798-6e2f-5df3-a5fb-29ad14d49b5d": (_COASTAL, 4, "10.60.10.0/24", _COASTAL_V4),
    "3eb2272d-8d3e-5f5e-bb5c-7fc1045e6b48": (_COASTAL, 4, "10.60.11.0/24", _COASTAL_V4),
    _COASTAL_V6: (_COASTAL, 6, "2001:db8:60::/48", None),
    "67d86406-2318-5d3e-9a20-e0643dde85d2": (_COASTAL, 6, "2001:db8:60:1::/64", _COASTAL_V6),
    "8bcce75a-7b7b-56ec-a983-20791d3b10b4": (_COASTAL, 6, "2001:db8:60:2::/64", _COASTAL_V6),
    _CENTRAL_V4: (_CENTRAL, 4, "10.80.0.0/20", None),
    "484db9de-6c03-5998-bb7b-8e1f00381e24": (_CENTRAL, 4, "10.80.1.0/24", _CENTRAL_V4),
    "960382d9-7a52-5e17-bac9-881bd3015fdc": (_CENTRAL, 4, "10.80.2.0/24", _CENTRAL_V4),
    "501c0ce4-d2ac-5891-9cee-ddf1c89715e8": (_CENTRAL, 4, "10.80.3.0/24", _CENTRAL_V4),
    "309785ae-eb3d-5321-817b-beaae08fa67f": (_CENTRAL, 4, "10.80.4.0/24", _CENTRAL_V4),
    "2fc276c3-d7b4-5cff-9762-b8e507bb961a": (_CENTRAL, 4, "10.80.5.0/24", _CENTRAL_V4),
    "b864da07-2a6c-5350-8ded-299deaf916e2": (_CENTRAL, 4, "10.80.6.0/24", _CENTRAL_V4),
    "d5bcfabc-adde-5031-9e22-2e5a6a8bb10f": (_CENTRAL, 4, "10.80.7.0/24", _CENTRAL_V4),
    "110ce1e7-a1b3-5ef8-b861-627fbc91f597": (_CENTRAL, 4, "10.80.8.0/24", _CENTRAL_V4),
    "35eaf4d9-cb15-5679-9d75-0151b01213e1": (_CENTRAL, 4, "10.80.9.0/24", _CENTRAL_V4),
    "04eff3c4-2af3-5410-a013-7c68c8d9613d": (_CENTRAL, 4, "10.80.10.0/24", _CENTRAL_V4),
    "05f85012-e83e-5eed-83e1-2283b45a41a9": (_CENTRAL, 4, "10.80.11.0/24", _CENTRAL_V4),
    _CENTRAL_V6: (_CENTRAL, 6, "2001:db8:80::/48", None),
    "dea2b92f-aa4f-5943-9900-82cf6bf7c638": (_CENTRAL, 6, "2001:db8:80:1::/64", _CENTRAL_V6),
    "09cb9c18-2aad-5ac1-9ba7-cdaa08ae87c8": (_CENTRAL, 6, "2001:db8:80:2::/64", _CENTRAL_V6),
}


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
        if set(seed_scopes) != expected_scopes or set(seed_scopes) != set(_RICH_SCOPES) or len(seed_scopes) != len(seed["scopes"]):
            raise ValueError("Rich seed scopes differ from the pinned feed.")
        current_scopes = {row["id"]: row for row in connection.execute("SELECT * FROM scopes")}
        for scope_id, structure in _RICH_SCOPES.items():
            original = seed_scopes[scope_id]
            current = current_scopes.get(scope_id)
            if ((original["namespace"], original["managed_cidrs"]) != structure or current is None
                    or (current["namespace"], json.loads(current["managed_cidrs"])) != structure):
                raise ValueError("A feed scope or its managed perimeter changed: " + scope_id)
        seed_prefixes = {row["id"]: row for row in seed["prefixes"]}
        if (set(seed_prefixes) != {row["prefix_id"] for row in policy["records"]}
                or set(seed_prefixes) != set(_RICH_PREFIXES)
                or len(seed_prefixes) != len(seed["prefixes"])
                or any(seed_prefixes[row["prefix_id"]]["scope_id"] != row["scope_id"] for row in policy["records"])):
            raise ValueError("Rich seed prefixes differ from the pinned intended-policy coverage.")
        current_prefixes = {row["id"]: row for row in connection.execute("SELECT * FROM prefixes")}
        for prefix_id, structure in _RICH_PREFIXES.items():
            original = seed_prefixes[prefix_id]
            current = current_prefixes.get(prefix_id)
            fields = ("scope_id", "family", "cidr", "parent_id")
            if (tuple(original[field] for field in fields) != structure or current is None
                    or tuple(current[field] for field in fields) != structure):
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
