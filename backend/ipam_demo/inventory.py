"""Read-only inventory projections. Address counts never become floating point."""

from ipaddress import ip_address, ip_network
import json
import sqlite3

from .errors import AppError


def scope_payload(row: sqlite3.Row) -> dict:
    return {**dict(row), "managed_cidrs": json.loads(row["managed_cidrs"]), "synthetic": True}


def prefix_payload(row: sqlite3.Row) -> dict:
    result = dict(row)
    result.pop("network_hex")
    result.pop("prefix_length")
    for field in ("tags", "custom_fields", "origin"):
        result[field] = json.loads(result[field])
    result["address_count"] = str(ip_network(result["cidr"]).num_addresses)
    return result


def pool_payload(row: sqlite3.Row) -> dict:
    result = dict(row)
    for field in ("ranges", "exclusions", "origin"):
        result[field] = json.loads(result[field])
    def count(ranges):
        return sum(int(ip_address(r["end"])) - int(ip_address(r["start"])) + 1 for r in ranges)
    result["capacity"] = str(count(result["ranges"]) - count(result["exclusions"]))
    return result


def allocation_payload(row: sqlite3.Row) -> dict:
    result = dict(row)
    result.pop("address_hex")
    result["origin"] = json.loads(result["origin"])
    return result


def page(items: list, limit: int, offset: int) -> dict:
    return {"items": items[offset:offset + limit], "total": len(items), "limit": limit, "offset": offset}


def scopes(connection, *, domain=None) -> list:
    rows = connection.execute("SELECT * FROM scopes" + (" WHERE domain=?" if domain else "") + " ORDER BY name,id",
                              (domain,) if domain else ())
    return [scope_payload(row) for row in rows]


def prefixes(connection, *, scope_id=None, family=None, owner=None, tag=None,
             domain=None, region=None, q=None) -> list:
    rows = connection.execute(
        "SELECT p.*, s.name AS scope_name, s.domain, s.region FROM prefixes p JOIN scopes s ON s.id=p.scope_id "
        "ORDER BY p.scope_id, p.family, p.network_hex, p.prefix_length, p.id"
    )
    # Small, bounded demo ledger. IP/CIDR filtering uses real address arithmetic.
    query_network = None
    if q:
        try:
            query_network = ip_network(q.strip(), strict=False)
        except ValueError:
            pass
    result = []
    for row in rows:
        item = prefix_payload(row)
        if scope_id and item["scope_id"] != scope_id:
            continue
        if domain and row["domain"].casefold() != domain.casefold():
            continue
        if region and row["region"].casefold() != region.casefold():
            continue
        if family and item["family"] != family:
            continue
        if owner and item["owner"].casefold() != owner.casefold():
            continue
        if tag and tag.casefold() not in [value.casefold() for value in item["tags"]]:
            continue
        if query_network is not None:
            network = ip_network(item["cidr"])
            if network.version != query_network.version or not network.overlaps(query_network):
                continue
        elif q and q.casefold() not in " ".join([item["cidr"], item["owner"], item["purpose"], *item["tags"]]).casefold():
            continue
        result.append(item)
    return result


def pools(connection, *, scope_id=None, prefix_id=None, domain=None, region=None) -> list:
    rows = connection.execute(
        "SELECT p.*, s.domain, s.region FROM pools p JOIN scopes s ON s.id=p.scope_id "
        "ORDER BY p.scope_id, p.prefix_id, p.id"
    )
    return [pool_payload(row) for row in rows
            if (not scope_id or row["scope_id"] == scope_id)
            and (not prefix_id or row["prefix_id"] == prefix_id)
            and (not domain or row["domain"].casefold() == domain.casefold())
            and (not region or row["region"].casefold() == region.casefold())]


def allocations(connection, *, scope_id=None, prefix_id=None, pool_id=None, q=None, domain=None) -> list:
    query_network = None
    if q:
        try:
            query_network = ip_network(q.strip(), strict=False)
        except ValueError:
            pass
    items = []
    query = ("SELECT a.* FROM allocations a JOIN scopes s ON s.id=a.scope_id "
             + ("WHERE s.domain=? " if domain else "") + "ORDER BY a.scope_id,a.family,a.address_hex,a.id")
    for row in connection.execute(query, (domain,) if domain else ()):
        if any(value and row[key] != value for key, value in
               (("scope_id", scope_id), ("prefix_id", prefix_id), ("pool_id", pool_id))):
            continue
        item = allocation_payload(row)
        if query_network is not None:
            address = ip_address(item["address"])
            if address.version != query_network.version or address not in query_network:
                continue
        elif q and q.casefold() not in " ".join([item["address"], item["owner"], item["purpose"]]).casefold():
            continue
        items.append(item)
    return items


def prefix_detail(connection, object_id: str, *, domain=None) -> dict:
    row = connection.execute(
        "SELECT p.*, s.name AS scope_name, s.domain FROM prefixes p JOIN scopes s ON s.id=p.scope_id "
        "WHERE p.id=?" + (" AND s.domain=?" if domain else ""),
        (object_id, domain) if domain else (object_id,),
    ).fetchone()
    if row is None:
        raise AppError("NOT_FOUND", "No prefix exists with that ID.", status=404)
    return {**prefix_payload(row), "pools": pools(connection, prefix_id=object_id, domain=domain),
            "allocations": allocations(connection, prefix_id=object_id, domain=domain)}
