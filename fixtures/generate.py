#!/usr/bin/env python3
"""Generate fictional source artifacts only; never import or evaluate IPAM rules."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from ipaddress import ip_network
import json
from pathlib import Path
from uuid import UUID, uuid5


ROOT = Path(__file__).resolve().parent / "v1"
NAMESPACE = UUID("fed69f72-8aa8-48e5-896e-cc50e06bc004")
CLOCK = datetime(2026, 9, 1, tzinfo=timezone.utc)
START = CLOCK - timedelta(days=30)
FOUNDATION = "ea51aa64b1780fa5c171e95ae59a619bf0109d52"
FILES = {}


def stamp(value):
    return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def uid(key):
    return str(uuid5(NAMESPACE, "ipam-synthetic-v1/" + key))


def write(name, value):
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, indent=2, ensure_ascii=True) + "\n").encode("utf-8")
    path.write_bytes(payload)
    FILES[name] = {"bytes": len(payload), "sha256": sha256(payload).hexdigest()}
    if "records" in value:
        FILES[name]["records"] = len(value["records"])
    print(f"wrote {name}: {len(payload)} bytes"
          + (f", {len(value['records'])} records" if "records" in value else ""))


def inventory():
    data = json.loads((ROOT / "foundation-baseline.json").read_text(encoding="utf-8"))
    data.update(source_id="synthetic-inventory-rich", source_run_id="rich-v1-inventory")
    for name, octet in (("Coastal", 60), ("Central", 80)):
        data["scopes"].append({
            "id": uid(f"scope-{name.lower()}"), "name": name,
            "namespace": f"vrf-{name.lower()}", "domain": "demo-core", "region": name,
            "managed_cidrs": [f"10.{octet}.0.0/16", f"2001:db8:{octet}::/48"],
            "source_record_id": f"scope-{name.lower()}",
        })
    scopes = {s["name"]: s["id"] for s in data["scopes"]}

    def prefix(name, cidr, parent=None, missing=False):
        key = f"prefix-{name.lower()}-{cidr}"
        row = {
            "id": uid(key), "scope_id": scopes[name], "family": ip_network(cidr).version,
            "cidr": cidr, "parent_id": parent, "owner": "" if missing else f"{name} Network Team",
            "purpose": "" if missing else "Synthetic intended regional inventory",
            "tags": [] if missing else ["regional"],
            "custom_fields": {} if missing else {"planning_region": name},
            "version": 1, "source_record_id": key,
        }
        data["prefixes"].append(row)
        return row["id"]

    north_parent = data["prefixes"][0]["id"]
    for subnet in range(3, 12):
        prefix("North", f"10.40.{subnet}.0/24", north_parent)
    prefix("North", "2001:db8:40:2::/64", data["prefixes"][3]["id"])
    for subnet in range(2, 16):
        prefix("Lab", f"10.40.{subnet}.0/24", missing=subnet == 15)
    for name, octet in (("Coastal", 60), ("Central", 80)):
        parent = prefix(name, f"10.{octet}.0.0/20")
        for subnet in range(1, 12):
            prefix(name, f"10.{octet}.{subnet}.0/24", parent)
        parent6 = prefix(name, f"2001:db8:{octet}::/48")
        for subnet in (1, 2):
            prefix(name, f"2001:db8:{octet}:{subnet}::/64", parent6)
    prefixes = {(p["scope_id"], p["cidr"]): p for p in data["prefixes"]}
    for name, octet in (("Coastal", 60), ("Central", 80), ("Lab", 40)):
        for subnet in (1, 2):
            key = f"pool-{name.lower()}-access-{subnet}"
            data["pools"].append({
                "id": uid(key), "scope_id": scopes[name],
                "prefix_id": prefixes[(scopes[name], f"10.{octet}.{subnet}.0/24")]["id"],
                "name": f"{name} access {subnet}", "management_mode": "dhcp",
                "allocation_authority": "external",
                "ranges": [{"start": f"10.{octet}.{subnet}.10", "end": f"10.{octet}.{subnet}.109"}],
                "exclusions": [], "pool_version": 1, "source_record_id": key,
            })
    return data, scopes, prefixes


def evidence_row(key, scope, family, start, end, kind, **fields):
    time_fields = ({"lease_start_at": stamp(start), "lease_end_at": stamp(end)} if kind == "dhcp"
                   else {"valid_from_at": stamp(start), "valid_until_at": stamp(end)})
    time_fields["observed_at"] = stamp(start)
    return {"id": uid(key), "source_record_id": key, "scope_id": scope,
            "family": family, **fields, **time_fields, "original_timestamps": dict(time_fields)}


def envelope(name, scope, kind, records):
    return {
        "schema_version": 1, "fixture_contract": "ipam-synthetic-v1", "synthetic": True,
        "demo_clock_at": stamp(CLOCK), "source_id": f"synthetic-{kind}-{name.lower()}",
        "source_run_id": "rich-v1-complete", "source_kind": kind,
        "source": {"name": f"Fictional {name} {kind.upper()} export",
                   "owner": f"{name} Network Team", "authority": "observed",
                   "required_for": ["dhcp_history"] if kind == "dhcp" else ["routing_view"]},
        "coverage": [{"scope_id": scope, "kind": "interval", "window_start_at": stamp(START),
                      "window_end_at": stamp(CLOCK), "declared_complete": True}],
        "records": records,
    }


def observations(scopes):
    leases = {name: [] for name in scopes}
    # 410 persistent clients. 328 renew five times, 82 four times: 1,968 intervals.
    # Stable renewals exercise half-open boundaries without altering occupancy.
    client_index = 0
    for name, octet, subnet, clients in (("North", 40, 1, 150), ("Coastal", 60, 1, 90),
                                        ("Coastal", 60, 2, 40), ("Central", 80, 2, 10),
                                        ("Lab", 40, 1, 60), ("Lab", 40, 2, 60)):
        for address_index in range(clients):
            client_index += 1
            segments = 5 if client_index <= 328 else 4
            client = f"{name.lower()}-{subnet}-client-{address_index + 1:03d}"
            for segment in range(segments):
                start = START + timedelta(days=30 * segment / segments)
                end = (START + timedelta(days=30 * (segment + 1) / segments)
                       if segment < segments - 1 else CLOCK + timedelta(days=1))
                key = f"lease-{client}-renewal-{segment + 1}"
                leases[name].append(evidence_row(
                    key, scopes[name], 4, start, end, "dhcp",
                    address=f"10.{octet}.{subnet}.{10 + address_index}", client_id=client))
    # One additional client each completed day: daily p95 is 40 + elapsed day.
    for day in range(1, 30):
        leases["Coastal"].append(evidence_row(
            f"lease-coastal-2-growth-{day:02d}", scopes["Coastal"], 4,
            START + timedelta(days=day), CLOCK + timedelta(days=1), "dhcp",
            address=f"10.60.2.{49 + day}", client_id=f"coastal-2-growth-{day:02d}"))
    # Two incompatible principals overlap on a previously unused assignable address.
    for client in ("alpha", "beta"):
        leases["Lab"].append(evidence_row(
            f"lease-lab-conflict-{client}", scopes["Lab"], 4,
            CLOCK - timedelta(hours=2), CLOCK + timedelta(hours=2), "dhcp",
            address="10.40.1.100", client_id=f"lab-conflict-{client}"))
    leases["Central"].append(evidence_row(
        "lease-central-unlisted", scopes["Central"], 4,
        START, CLOCK + timedelta(days=1), "dhcp",
        address="10.80.240.10", client_id="central-unlisted-client"))

    routes = {name: [] for name in scopes}
    targets = {
        "North": ["10.40.1.0/24", "10.40.2.0/28", "2001:db8:40:1::/64", "10.40.3.0/24", "10.40.4.0/24"],
        "Coastal": ["10.60.1.0/24", "10.60.2.0/24", "10.60.0.0/20", "2001:db8:60:1::/64", "2001:db8:60:2::/64"],
        "Central": ["10.80.1.0/24", "10.80.2.0/24", "2001:db8:80:1::/64", "2001:db8:80:2::/64", "10.80.4.0/24", "10.80.241.0/24", "198.51.100.0/24"],
        "Lab": ["10.40.1.0/24", "10.40.3.0/24", "10.40.4.0/24"],
    }
    for name, cidrs in targets.items():
        for cidr in cidrs:
            for segment in range(10):
                start = START + timedelta(days=segment * 3)
                end = start + timedelta(days=3) if segment < 9 else CLOCK + timedelta(days=1)
                routes[name].append(evidence_row(
                    f"route-{name.lower()}-{cidr}-{segment + 1:02d}", scopes[name],
                    ip_network(cidr).version, start, end, "routing", cidr=cidr,
                    router_id=f"{name.lower()}-router-01"))
    return {f"{kind}-{name.lower()}": envelope(name, scopes[name], kind, rows[name])
            for kind, rows in (("dhcp", leases), ("routing", routes)) for name in scopes}


def policies(data, scopes, prefixes):
    expected = {
        ("North", "10.40.1.0/24"): "exact",
        ("Coastal", "10.60.1.0/24"): "exact",
        ("Coastal", "10.60.2.0/24"): "exact",
        ("Coastal", "10.60.3.0/24"): "covering",
        ("Coastal", "10.60.4.0/24"): "exact",
        ("Central", "10.80.1.0/24"): "exact",
        ("Central", "10.80.2.0/24"): "exact",
        ("Lab", "10.40.1.0/24"): "exact",
        ("Lab", "10.40.2.0/24"): "exact",
    }
    by_id = {prefixes[(scopes[name], cidr)]["id"]: policy for (name, cidr), policy in expected.items()}
    return {
        "schema_version": 1, "fixture_contract": "ipam-synthetic-v1", "synthetic": True,
        "demo_clock_at": stamp(CLOCK), "source_id": "synthetic-inventory-policy",
        "source_run_id": "rich-v1-policy", "effective_from_at": stamp(START),
        "records": [{"source_record_id": "policy-" + p["source_record_id"],
                     "prefix_id": p["id"], "scope_id": p["scope_id"],
                     "expects_announcement": p["id"] in by_id,
                     "route_match_policy": by_id.get(p["id"], "exact")}
                    for p in data["prefixes"]],
    }


def variants(batches):
    for key in ("dhcp-coastal", "dhcp-central", "routing-coastal", "routing-central", "routing-lab"):
        batch = deepcopy(batches[key])
        batch["source_run_id"] = "rich-v1-partial"
        batch["coverage"][0]["declared_complete"] = False
        batch["records"] = []
        write(f"opt-in/{key}-partial.json", batch)
    for key, lag in (("dhcp-central", timedelta(hours=1)), ("routing-central", timedelta(minutes=10))):
        batch = deepcopy(batches[key])
        batch["source_run_id"] = "rich-v1-stale"
        batch["coverage"][0]["window_end_at"] = stamp(CLOCK - lag)
        write(f"opt-in/{key}-stale.json", batch)

    # Preserve deliberately malformed raw values; do not normalize or silently skip.
    for key, mutations in (
        ("dhcp-central", [
            {"lease_end_at": None}, {"scope_id": uid("unmapped-scope")},
            {"address": "10.80.2.999"}, {"lease_start_at": "2026-08-02T00:00:00"},
            {"lease_start_at": "2026-09-02T00:00:00.000Z", "lease_end_at": "2026-09-03T00:00:00.000Z"},
            {"lease_end_at": "2026-08-01T00:00:00.000Z"}, {"family": 6},
        ]),
        ("routing-central", [
            {"valid_until_at": None}, {"cidr": "10.80.1.7/24"},
            {"observed_at": "2026-09-02T00:00:00.000Z"}, {"family": 6},
            {"scope_id": uid("unmapped-scope")}, {"valid_until_at": "2026-08-01T00:00:00.000Z"},
        ]),
    ):
        batch = deepcopy(batches[key])
        batch["source_run_id"] = "rich-v1-invalid"
        good = deepcopy(batch["records"][0])
        good["id"] = uid(f"{key}-valid-control")
        good["source_record_id"] = f"{key}-valid-control"
        batch["records"] = [good]
        for index, changes in enumerate(mutations, 1):
            record = deepcopy(good)
            record.update(id=uid(f"{key}-invalid-{index}"), source_record_id=f"{key}-invalid-{index}")
            record.update(changes)
            record["original_timestamps"] = {k: record[k] for k in good["original_timestamps"]}
            batch["records"].append(record)
        if key == "dhcp-central":
            batch["records"].append(deepcopy(good))
        write(f"opt-in/{key}-invalid.json", batch)
    replay = deepcopy(batches["dhcp-north"])
    replay["records"][0]["client_id"] = "changed-payload-same-batch-identity"
    write("opt-in/dhcp-north-changed-replay.json", replay)


def main():
    data, scopes, prefixes = inventory()
    write("inventory.json", data)
    write("inventory-policy.json", policies(data, scopes, prefixes))
    batches = observations(scopes)
    for key, batch in batches.items():
        write(f"observations/{key}.json", batch)
    variants(batches)
    counts = {group: len(data[group]) for group in ("scopes", "prefixes", "pools", "allocations")}
    counts.update(dhcp_lease_intervals=sum(len(b["records"]) for b in batches.values() if b["source_kind"] == "dhcp"),
                  routing_observations=sum(len(b["records"]) for b in batches.values() if b["source_kind"] == "routing"))
    baseline = (ROOT / "foundation-baseline.json").read_bytes()
    write("pack.json", {
        "schema_version": 1, "fixture_contract": "ipam-synthetic-v1", "synthetic": True,
        "demo_clock_at": stamp(CLOCK), "window_start_at": stamp(START), "window_end_at": stamp(CLOCK),
        "foundation": {"commit": FOUNDATION, "path": "backend/ipam_demo/data/baseline.json",
                       "snapshot": "foundation-baseline.json", "sha256": sha256(baseline).hexdigest()},
        "default_inputs": ["inventory.json", "inventory-policy.json"] +
                          [f"observations/{key}.json" for key in batches],
        "opt_in_inputs": [name for name in FILES if name.startswith("opt-in/")],
        "counts": counts, "generated_files": dict(FILES),
        "provenance": "Entirely fictional. Baseline rows copied unchanged; added IDs use fixed UUIDv5 names. No network or customer input.",
    })
    print(json.dumps({"generated_counts": counts, "generated_files": len(FILES)}, sort_keys=True))


if __name__ == "__main__":
    main()
