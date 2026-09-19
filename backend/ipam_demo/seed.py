"""Install the packaged, deterministic intended ledger in a single transaction."""

from datetime import datetime, timezone
from importlib.resources import files
from ipaddress import ip_address, ip_network
import json
from uuid import UUID

from .errors import AppError
from .store import connect, exclusive_data_access, initialize_schema, require_schema


def _ranges(values, network):
    intervals = []
    for value in values:
        start, end = ip_address(value["start"]), ip_address(value["end"])
        if start.version != network.version or end.version != network.version:
            raise ValueError("Range family differs from prefix")
        if start not in network or end not in network or int(start) > int(end):
            raise ValueError("Range must be ordered and contained in its prefix")
        intervals.append((int(start), int(end)))
    intervals.sort()
    if any(left[1] >= right[0] for left, right in zip(intervals, intervals[1:])):
        raise ValueError("Ranges/exclusions must be disjoint")
    return intervals


def _validate(envelope: dict) -> None:
    """Validate this packaged format; this is not the Stage 2 import endpoint."""
    if envelope["schema_version"] != 1 or envelope["scenario"] != "baseline":
        raise ValueError("Unsupported baseline envelope")
    clock = datetime.fromisoformat(envelope["demo_clock_at"].replace("Z", "+00:00"))
    if clock.utcoffset() is None:
        raise ValueError("Demo clock must include a timezone")
    for group in ("scopes", "prefixes", "pools", "allocations"):
        ids = [record["id"] for record in envelope[group]]
        if len(set(ids)) != len(ids):
            raise ValueError(f"Duplicate IDs in {group}")
        for object_id in ids:
            UUID(object_id)
    scopes = {record["id"]: record for record in envelope["scopes"]}
    networks = {record["id"]: ip_network(record["cidr"], strict=True) for record in envelope["prefixes"]}
    prefixes = {record["id"]: record for record in envelope["prefixes"]}
    for record in prefixes.values():
        network = networks[record["id"]]
        managed = [ip_network(cidr, strict=True) for cidr in scopes[record["scope_id"]]["managed_cidrs"]]
        if record["family"] != network.version or not any(
            network.version == boundary.version and network.subnet_of(boundary) for boundary in managed
        ):
            raise ValueError("Prefix must match its family and declared managed perimeter")
        parent_id = record["parent_id"]
        if parent_id:
            parent = prefixes[parent_id]
            parent_network = networks[parent_id]
            if (parent["scope_id"] != record["scope_id"] or parent_network.version != network.version
                    or not network.subnet_of(parent_network) or network.prefixlen <= parent_network.prefixlen):
                raise ValueError("Parent must strictly contain its child in the same scope/family")
        if record["version"] < 1 or not all(isinstance(t, str) for t in record["tags"]):
            raise ValueError("Invalid prefix version/tags")
        if not isinstance(record["custom_fields"], dict) or not all(
            isinstance(key, str) and isinstance(value, str) and key not in record
            for key, value in record["custom_fields"].items()
        ):
            raise ValueError("Custom fields must be string metadata, not reserved fields")
    # Only explicitly declared hierarchy explains same-scope overlapping prefixes.
    def ancestors(record):
        result = set()
        parent_id = record["parent_id"]
        while parent_id:
            result.add(parent_id)
            parent_id = prefixes[parent_id]["parent_id"]
        return result
    records = list(prefixes.values())
    for index, left in enumerate(records):
        for right in records[index + 1:]:
            if left["scope_id"] == right["scope_id"] and left["family"] == right["family"]:
                if networks[left["id"]].overlaps(networks[right["id"]]):
                    if left["id"] not in ancestors(right) and right["id"] not in ancestors(left):
                        raise ValueError("Overlapping prefixes need an explicit ancestor relationship")
    pools = {record["id"]: record for record in envelope["pools"]}
    intervals = {}
    for record in pools.values():
        prefix = prefixes[record["prefix_id"]]
        network = networks[prefix["id"]]
        if record["scope_id"] != prefix["scope_id"]:
            raise ValueError("Pool scope differs from prefix")
        ranges = _ranges(record["ranges"], network)
        exclusions = _ranges(record["exclusions"], network)
        if not ranges or any(not any(a <= x <= y <= b for a, b in ranges) for x, y in exclusions):
            raise ValueError("Pool exclusions must be within assignable ranges")
        if sum(b-a+1 for a, b in ranges) <= sum(b-a+1 for a, b in exclusions):
            raise ValueError("Pool capacity must be positive")
        if record["allocation_authority"] == "local" and (network.version != 4 or record["management_mode"] != "static"):
            raise ValueError("Local authority is limited to a static IPv4 pool")
        intervals[record["id"]] = ranges, exclusions
    for record in envelope["allocations"]:
        prefix = prefixes[record["prefix_id"]]
        address = ip_address(record["address"])
        if (record["scope_id"] != prefix["scope_id"] or record["family"] != address.version
                or address.version != prefix["family"] or address not in networks[prefix["id"]]):
            raise ValueError("Allocation must match its scoped prefix and family")
        if record["pool_id"]:
            pool = pools[record["pool_id"]]
            ranges, exclusions = intervals[pool["id"]]
            if pool["prefix_id"] != prefix["id"] or not any(a <= int(address) <= b for a, b in ranges):
                raise ValueError("Allocation is outside its pool")
            if any(a <= int(address) <= b for a, b in exclusions):
                raise ValueError("Allocation is excluded from its pool")


def seed_baseline(directory) -> dict:
    try:
        envelope = json.loads(files("ipam_demo").joinpath("data/baseline.json").read_text(encoding="utf-8"))
        _validate(envelope)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        raise AppError("INVALID_BASELINE", "Packaged baseline could not be loaded or validated.", status=500,
                       details={"reason": str(exc)}) from exc
    ingested_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    def origin(record):
        return json.dumps({"source_id": envelope["source_id"], "source_run_id": envelope["source_run_id"],
                           "source_record_id": record["source_record_id"], "observed_at": envelope["demo_clock_at"],
                           "ingested_at": ingested_at, "synthetic": True})
    with exclusive_data_access(directory) as path:
        initialize_schema(path)
        with connect(path) as connection, connection:
            connection.execute("BEGIN IMMEDIATE")
            require_schema(connection)
            if connection.execute("SELECT initialized FROM app_meta WHERE singleton=1").fetchone()[0]:
                raise AppError("ALREADY_INITIALIZED", "Seed refused: initialized inventory will not be overwritten.", status=409)
            for record in envelope["scopes"]:
                connection.execute("INSERT INTO scopes VALUES (?, ?, ?, ?, ?, ?)",
                                   (record["id"], record["name"], record["namespace"], record["domain"], record["region"], json.dumps(record["managed_cidrs"])))
            for record in sorted(envelope["prefixes"], key=lambda r: networks_key(r["cidr"])):
                network = ip_network(record["cidr"])
                connection.execute("INSERT INTO prefixes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                   (record["id"], record["scope_id"], network.version, str(network),
                                    f"{int(network.network_address):032x}", network.prefixlen, record["parent_id"],
                                    record["owner"], record["purpose"], json.dumps(record["tags"]),
                                    json.dumps(record["custom_fields"]), record["version"], origin(record)))
            for record in envelope["pools"]:
                family = next(p["family"] for p in envelope["prefixes"] if p["id"] == record["prefix_id"])
                connection.execute("INSERT INTO pools VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                   (record["id"], record["scope_id"], record["prefix_id"], family, record["name"],
                                    record["management_mode"], record["allocation_authority"], json.dumps(record["ranges"]),
                                    json.dumps(record["exclusions"]), record["pool_version"], origin(record)))
            for record in envelope["allocations"]:
                address = ip_address(record["address"])
                connection.execute("INSERT INTO allocations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                   (record["id"], record["scope_id"], record["prefix_id"], record["pool_id"], address.version,
                                    str(address), f"{int(address):032x}", record["owner"], record["purpose"], origin(record)))
            connection.execute(
                "UPDATE app_meta SET initialized=1, baseline_version=1, scenario=?, demo_clock_at=?, seeded_at=?, seed_envelope=? WHERE singleton=1",
                (envelope["scenario"], envelope["demo_clock_at"], ingested_at, json.dumps(envelope, sort_keys=True)),
            )
    return {"status": "seeded", "scenario": "baseline", "synthetic": True, "database": str(path),
            "demo_clock_at": envelope["demo_clock_at"], "ingested_at": ingested_at,
            "counts": {group: len(envelope[group]) for group in ("scopes", "prefixes", "pools", "allocations")}}


def networks_key(cidr: str) -> tuple:
    network = ip_network(cidr)
    return network.version, network.prefixlen, int(network.network_address)
