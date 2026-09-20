"""Receipt-derived source catalog; it never promotes source data to authority."""

import json

from . import evidence


def catalog(connection, *, scope_id=None) -> list[dict]:
    """Return selected source+scope rows at the seeded demo clock.

    Selection deliberately reuses ``evidence.selected_views``: latest by
    ingestion sequence per source and scope, with no older-complete fallback.
    The catalog reports declared authority and provenance; it does not infer
    uniqueness or discover systems outside recorded receipts.
    """
    meta = connection.execute("SELECT demo_clock_at FROM app_meta WHERE singleton=1").fetchone()
    evaluated_at = meta["demo_clock_at"] if meta else None
    views, _ = evidence.selected_views(connection)
    selected = []
    for scopes in views.values():
        for current_scope, entries in scopes.items():
            if scope_id and current_scope != scope_id:
                continue
            selected.extend(_entry(view["receipt"], view["coverage"], evaluated_at) for view in entries)

    # Staged intended inventory is not an active evidence view, but its receipt
    # remains visible with explicit non-active status and no invented freshness.
    seen_staged = set()
    for row in connection.execute(
        "SELECT b.*, c.scope_id, c.window_start_at, c.window_end_at, "
        "c.declared_complete, c.effective_complete FROM source_batches b "
        "LEFT JOIN source_coverage c ON c.batch_id=b.id "
        "WHERE b.source_kind='inventory_staged' ORDER BY b.sequence DESC"
    ):
        if row["source_id"] in seen_staged:
            continue
        seen_staged.add(row["source_id"])
        if scope_id:
            continue
        receipt = json.loads(row["receipt_json"])
        selected.append(_staged_entry(receipt, evaluated_at))
    return sorted(selected, key=lambda value: (value["source_id"], value["scope_id"] or ""))


def _entry(receipt, coverage, evaluated_at, *, staged=False):
    kind = receipt["source_kind"]
    complete = bool(coverage["effective_complete"])
    freshness = "not_applicable" if staged or kind == "route_policy" else (
        "fresh" if evidence.eligible_current_view(
            {"coverage": coverage}, evidence.instant(evaluated_at), kind) else "stale")
    return {
        "source_id": receipt["source_id"], "source_name": receipt["source"]["name"],
        "owner": receipt["source"]["owner"], "source_kind": kind,
        "authority": receipt["source"]["authority"], "authority_status": "declared",
        "scope_id": coverage["scope_id"], "source_run_id": receipt["source_run_id"],
        "batch_id": receipt["id"], "application_status": "staged" if staged else receipt["application_status"],
        "rejection_status": "rejected" if receipt["rejected_rows"] else "accepted",
        "rejected_rows": receipt["rejected_rows"], "duplicate_rows": receipt["duplicate_rows"],
        "evaluated_at": evaluated_at, "freshness": freshness,
        "completeness": "complete" if complete else "partial", "coverage_grain": "scope/time-window",
        "window_start_at": coverage["window_start_at"], "window_end_at": coverage["window_end_at"],
        "declared_complete": bool(coverage["declared_complete"]), "effective_complete": complete,
        "references": {"batch_id": receipt["id"], "receipt_id": receipt["id"]},
    }


def _staged_entry(receipt, evaluated_at):
    return {
        "source_id": receipt["source_id"], "source_name": None, "owner": None,
        "source_kind": "inventory_staged", "authority": "not_applicable",
        "authority_status": "not_applicable", "scope_id": None,
        "source_run_id": receipt["source_run_id"], "batch_id": receipt["id"],
        "application_status": "staged", "rejection_status": "accepted",
        "rejected_rows": receipt["rejected_rows"], "duplicate_rows": receipt["duplicate_rows"],
        "evaluated_at": evaluated_at, "freshness": "not_applicable",
        "completeness": "unknown", "coverage_grain": "not_applicable",
        "window_start_at": None, "window_end_at": None,
        "declared_complete": None, "effective_complete": None,
        "references": {"batch_id": receipt["id"], "receipt_id": receipt["id"]},
    }
