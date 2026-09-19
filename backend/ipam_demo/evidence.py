"""Shared source selection and current positive claims; no inventory authority."""

from datetime import datetime
import json


def instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def selected_views(connection):
    """Latest ingestion per source/scope, including partial; staged data never active."""
    views = {"routing": {}, "route_policy": {}, "dhcp": {}}
    selected, seen = {}, set()
    rows = connection.execute(
        "SELECT b.*,c.scope_id,c.window_start_at,c.window_end_at,c.declared_complete,c.effective_complete "
        "FROM source_batches b JOIN source_coverage c ON c.batch_id=b.id ORDER BY b.sequence DESC"
    )
    for row in rows:
        if row["source_kind"] not in views:
            continue
        key = (row["source_id"], row["scope_id"])
        if key in seen:
            continue
        seen.add(key)
        receipt = json.loads(row["receipt_json"])
        selected[row["id"]] = receipt
        records = [dict(record) for record in connection.execute(
            "SELECT * FROM source_records WHERE batch_id=? ORDER BY row_number", (row["id"],))]
        coverage = {key: row[key] for key in ("scope_id", "window_start_at", "window_end_at")}
        coverage.update({"declared_complete": bool(row["declared_complete"]),
                         "effective_complete": bool(row["effective_complete"]),
                         "batch_id": row["id"], "source_id": row["source_id"], "source_run_id": row["source_run_id"]})
        views[row["source_kind"]].setdefault(row["scope_id"], []).append(
            {"receipt": receipt, "coverage": coverage, "records": records})
    return views, sorted(selected.values(), key=lambda value: value["sequence"])


def reference(view, record=None):
    receipt = view["receipt"]
    result = {"kind": receipt["source_kind"], "batch_id": receipt["id"],
              "source_id": receipt["source_id"], "source_run_id": receipt["source_run_id"]}
    if record is not None:
        result.update({"record_id": record["id"], "source_record_id": record["source_record_id"]})
    return result


def eligible_current_view(view, clock, kind):
    coverage = view["coverage"]
    age = (clock - instant(coverage["window_end_at"])).total_seconds()
    return (instant(coverage["window_start_at"]) <= clock
            and 0 <= age <= {"dhcp": 1800, "routing": 300}[kind])


def typed_records(view):
    for record in view["records"]:
        if record["status"] == "accepted":
            typed = json.loads(record["typed_json"])
            if typed["scope_id"] == view["coverage"]["scope_id"]:
                yield record, typed


def active_dhcp_claims(connection, scope_id, family, address, clock_text):
    """Positive claims block allocation; unknown/silence never proves availability."""
    views, _ = selected_views(connection)
    candidates = views["dhcp"].get(scope_id, [])
    clock = instant(clock_text)
    claims, reasons = [], []
    if not candidates:
        reasons.append("No DHCP source declares this scope; the local static ledger remains allocation authority.")
    if len(candidates) > 1:
        reasons.append("Multiple DHCP sources declare this scope; source authority is unresolved.")
    for view in candidates:
        if not eligible_current_view(view, clock, "dhcp"):
            reasons.append("Latest DHCP source is stale or outside the demo clock: " + view["receipt"]["source_id"])
            continue
        if not view["coverage"]["effective_complete"]:
            reasons.append("Latest DHCP coverage is incomplete: " + view["receipt"]["source_id"])
        for record, typed in typed_records(view):
            if (typed["family"] == family and typed["address"] == address
                    and instant(typed["observed_at"]) <= clock
                    and instant(typed["lease_start_at"]) <= clock < instant(typed["lease_end_at"])):
                claims.append({**typed, "input_reference": reference(view, record)})
    return {"claims": claims, "unknown_reasons": reasons}
