"""Pure, fictional source evolution; scheduling and application writes live elsewhere."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid5


FEED_VERSION = "ipam-evolving-v1"
ANCHOR = datetime(2026, 9, 1, tzinfo=timezone.utc)
STEP = timedelta(hours=6)
DAY = timedelta(days=1)
PERIOD = timedelta(days=2)
HISTORY = timedelta(days=30)
MAX_CYCLE_INDEX = 1460
NAMESPACE = UUID("fed69f72-8aa8-48e5-896e-cc50e06bc004")
REGIONS = ("north", "coastal", "central", "lab")
SOURCE_IDS = ("synthetic-inventory-policy",) + tuple(
    f"synthetic-{kind}-{region}" for kind in ("dhcp", "routing") for region in REGIONS
)


def _stamp(value):
    return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _interval(template, key, start, end, kind):
    row = deepcopy(template)
    row["source_record_id"] = key
    row["id"] = str(uuid5(NAMESPACE, FEED_VERSION + "/" + key))
    start_field, end_field = (("lease_start_at", "lease_end_at") if kind == "dhcp"
                              else ("valid_from_at", "valid_until_at"))
    row.update({start_field: _stamp(start), end_field: _stamp(end), "observed_at": _stamp(start)})
    row["original_timestamps"] = {field: row[field] for field in (start_field, end_field, "observed_at")}
    return row


def _episodes(template, key, first, duration, repeat, start, cutoff, kind):
    """Only intersecting historical/current intervals; never invent future starts."""
    first_index = max(0, (start - first - duration) // repeat + 1)
    final_index = (cutoff - first) // repeat
    return [_interval(template, f"{key}-{number:06d}", first + number * repeat,
                      first + number * repeat + duration, kind)
            for number in range(first_index, final_index + 1)]


def _baseline(envelopes):
    if not isinstance(envelopes, list) or len(envelopes) != len(SOURCE_IDS):
        raise ValueError("Supply the immutable rich-v1 policy and eight observation envelopes.")
    sources = {}
    for envelope in envelopes:
        if not isinstance(envelope, dict) or envelope.get("source_id") not in SOURCE_IDS:
            raise ValueError("Only the nine rich-v1 logical sources are supported.")
        source_id = envelope["source_id"]
        if source_id in sources:
            raise ValueError("Duplicate rich-v1 source: " + source_id)
        policy = source_id == "synthetic-inventory-policy"
        kind = "inventory_policy" if policy else source_id.split("-")[1]
        expected_run = "rich-v1-policy" if policy else "rich-v1-complete"
        if (envelope.get("source_kind") != kind or envelope.get("source_run_id") != expected_run
                or envelope.get("demo_clock_at") != _stamp(ANCHOR)
                or envelope.get("synthetic") is not True
                or type(envelope.get("schema_version")) is not int or envelope["schema_version"] != 1
                or envelope.get("fixture_contract") != "ipam-synthetic-v1"):
            raise ValueError("Feed requires the original rich-v1 baseline, never the latest imported view.")
        coverage = envelope.get("coverage")
        if not isinstance(coverage, list) or len(coverage) != (4 if policy else 1):
            raise ValueError("Unexpected rich-v1 scope coverage.")
        for item in coverage:
            if (not isinstance(item, dict) or item.get("declared_complete") is not True
                    or item.get("window_end_at") != _stamp(ANCHOR)
                    or item.get("window_start_at") != _stamp(ANCHOR if policy else ANCHOR - HISTORY)):
                raise ValueError("Baseline must contain the complete original rich-v1 coverage.")
        if not isinstance(envelope.get("records"), list) or not envelope["records"]:
            raise ValueError("Baseline records are missing.")
        sources[source_id] = envelope
    return sources


def _observations(baseline, clock, cycle_index):
    batch = deepcopy(baseline)
    kind = batch["source_kind"]
    region = batch["source_id"].rsplit("-", 1)[1]
    start_field, end_field = (("lease_start_at", "lease_end_at") if kind == "dhcp"
                              else ("valid_from_at", "valid_until_at"))
    window_start = clock - HISTORY
    phase = (cycle_index - 1) % 8 + 1 if cycle_index else 0
    lag = (timedelta(hours=1) if kind == "dhcp" else timedelta(minutes=10)) \
        if region == "central" and phase == 7 else timedelta(0)
    cutoff = clock - lag
    # Retain original interval facts/IDs verbatim until they leave the rolling window.
    rows = [deepcopy(row) for row in baseline["records"]
            if _instant(row[end_field]) > window_start and _instant(row[start_field]) <= cutoff]
    for template in baseline["records"]:
        if _instant(template[end_field]) != ANCHOR + DAY:
            continue
        if kind == "routing" and region == "north" and template["cidr"] == "10.40.1.0/24":
            # Its original interval really expires at +24h; recover at +36h.
            rows.extend(_episodes(template, "evolving-north-route", ANCHOR + STEP * 6,
                                  STEP * 6, PERIOD, window_start, cutoff, kind))
        else:
            rows.extend(_episodes(template, "evolving-renew-" + template["source_record_id"],
                                  ANCHOR + DAY, DAY, DAY, window_start, cutoff, kind))

    template = baseline["records"][0]
    if kind == "dhcp" and region == "coastal":
        for number in range(10):
            client = {**template, "address": f"10.60.1.{100 + number}",
                      "client_id": f"coastal-evolving-client-{number:02d}"}
            if number < 6:
                # Same principals meet at +12h; renewals are never concurrent claims.
                for segment in (1, 2):
                    rows.extend(_episodes(client, f"evolving-coastal-{number:02d}-renew-{segment}",
                                          ANCHOR + STEP * segment, STEP, PERIOD,
                                          window_start, cutoff, kind))
            rows.extend(_episodes(client, f"evolving-coastal-{number:02d}-burst", ANCHOR + STEP * 5,
                                  STEP * 2, PERIOD, window_start, cutoff, kind))
    if region == "central":
        fields = ({"address": "10.80.243.10", "client_id": "central-evolving-unlisted"}
                  if kind == "dhcp" else {"cidr": "10.80.243.0/24", "router_id": "central-router-01"})
        rows.extend(_episodes({**template, **fields}, f"evolving-central-unlisted-{kind}",
                              ANCHOR + STEP * 6, STEP * 2, PERIOD, window_start, cutoff, kind))
    if region == "lab" and kind == "routing":
        rows.extend(_episodes({**template, "cidr": "10.40.2.0/24"}, "evolving-lab-route-recovery",
                              ANCHOR + STEP * 6, PERIOD, PERIOD, window_start, cutoff, kind))
    if region == "lab" and kind == "dhcp":
        for principal in ("gamma", "delta"):
            rows.extend(_episodes({**template, "address": "10.40.1.101", "client_id": "lab-" + principal},
                                  "evolving-lab-conflict-" + principal, ANCHOR + PERIOD,
                                  STEP, PERIOD, window_start, cutoff, kind))

    coverage = batch["coverage"][0]
    coverage.update(window_start_at=_stamp(window_start), window_end_at=_stamp(cutoff))
    if region == "north" and kind == "routing" and phase == 5:
        # Deliberately incomplete source export. Never present empty as complete absence.
        coverage["declared_complete"] = False
        rows = []
    batch["records"] = sorted(rows, key=lambda row: (row[start_field], row["source_record_id"]))
    return batch


def build_cycle(index: int, baseline_envelopes: list[dict]) -> dict:
    """Return nine new envelopes without changing inputs or reading/writing any state.

    Index zero is a reference snapshot; the scheduler's first advance consumes one.
    The caller loads the unchanged v1 policy + eight observation files, validates
    their pinned assets and rich-store authority, and owns clock/import/run/cursor
    atomicity. Passing a prior cycle as the baseline is refused.
    """
    if type(index) is not int or index < 0:
        raise ValueError("cycle index must be a non-negative integer, not a boolean.")
    if index > MAX_CYCLE_INDEX:
        raise ValueError("Synthetic scenario exhausted after 365 simulated days; do not wrap the cursor.")
    sources = _baseline(baseline_envelopes)
    clock = ANCHOR + STEP * index
    cycle_id = f"evolving-v1-{index:06d}"
    batches = []
    for source_id in SOURCE_IDS:
        baseline = sources[source_id]
        if source_id == "synthetic-inventory-policy":
            batch = deepcopy(baseline)
            for coverage in batch["coverage"]:
                coverage.update(window_start_at=_stamp(clock), window_end_at=_stamp(clock))
        else:
            batch = _observations(baseline, clock, index)
        batch.update(demo_clock_at=_stamp(clock), source_run_id=cycle_id)
        batches.append(batch)
    return {"feed_version": FEED_VERSION, "cycle_id": cycle_id, "cycle_index": index,
            "demo_clock_at": _stamp(clock), "envelopes": batches}
