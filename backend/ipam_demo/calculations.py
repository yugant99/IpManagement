"""One saved occupancy/history/forecast calculation consumed by rules and views."""

from datetime import timedelta
from ipaddress import ip_address, ip_network
from math import ceil

from .evidence import eligible_current_view, instant, reference, typed_records
from .inventory import pools
from .seed import _ranges


def stamp(value):
    return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def assignable_intervals(pool, cidr):
    network = ip_network(cidr)
    ranges = _ranges(pool["ranges"], network)
    exclusions = _ranges(pool["exclusions"], network)
    if not ranges or any(not any(a <= x <= y <= b for a, b in ranges) for x, y in exclusions):
        raise ValueError("Pool exclusions must be inside its configured ranges")
    result = []
    for start, end in ranges:
        cursor = start
        for left, right in exclusions:
            if right < start or left > end:
                continue
            if cursor < left:
                result.append((cursor, left - 1))
            cursor = right + 1
        if cursor <= end:
            result.append((cursor, end))
    if not result:
        raise ValueError("Assignable capacity must be positive")
    return result


def _p95(values):
    return sorted(values)[ceil(.95 * len(values)) - 1]


def calculate_pools(connection, views, clock_text):
    """Calculate once, before pressure; callers persist these exact metrics."""
    clock = instant(clock_text)
    window_start = clock - timedelta(days=30)
    last_day_end = clock.replace(hour=0, minute=0, second=0, microsecond=0)
    subjects = {row["id"]: dict(row) for row in connection.execute(
        "SELECT p.*,s.name AS scope_name FROM prefixes p JOIN scopes s ON s.id=p.scope_id")}
    results = []
    for pool in pools(connection):
        prefix = subjects[pool["prefix_id"]]
        candidates = views["dhcp"].get(pool["scope_id"], [])
        metric = {"pool_id": pool["id"], "prefix_id": pool["prefix_id"], "scope_id": pool["scope_id"],
                  "scope_name": prefix["scope_name"], "family": pool["family"], "cidr": prefix["cidr"],
                  "name": pool["name"], "management_mode": pool["management_mode"],
                  "pool_version": pool["pool_version"], "capacity": pool["capacity"],
                  "input_references": [reference(view) for view in candidates],
                  "coverage": [view["coverage"] for view in candidates],
                  "current": {"status": "unavailable", "at": clock_text, "occupied_addresses": None,
                              "utilization_pct": None, "positive_observed_addresses": None},
                  "p95": {"status": "unavailable", "occupied_addresses": None, "utilization_pct": None,
                          "eligible_samples": 0, "required_samples": 720,
                          "window_start_at": stamp(window_start), "window_end_at": clock_text,
                          "sample_interval_seconds": 3600, "method": "nearest_rank"},
                  "forecast": {"status": "unavailable", "days_to_full": None, "estimated_full_at": None,
                               "slope_addresses_per_day": None, "baseline_addresses": None,
                               "complete_days": 0, "daily_p95": [], "method": "ordinary_least_squares"},
                  "history": [], "lease_overlap_30d": None,
                  "limitations": ["Synthetic lease occupancy is not traffic; hourly samples are an illustrative approximation.",
                                  "Counts use distinct assignable addresses; renewals and conflicting clients do not inflate occupancy."]}
        results.append(metric)
        reason = None
        try:
            intervals = assignable_intervals(pool, prefix["cidr"])
            capacity = sum(end - start + 1 for start, end in intervals)
            metric["capacity"] = str(capacity)
        except (ValueError, KeyError, TypeError) as exc:
            reason = "invalid_capacity: " + str(exc)
        if reason is None and (pool["family"] != 4 or pool["management_mode"] != "dhcp"):
            reason = "not_applicable: occupancy and forecasting apply to DHCP-managed IPv4 pools"
        if reason is None and len(candidates) != 1:
            reason = "missing_source" if not candidates else "ambiguous_source_authority"
        view = candidates[0] if len(candidates) == 1 else None
        if reason is None and not eligible_current_view(view, clock, "dhcp"):
            reason = "stale_or_inapplicable_source"
        if reason:
            for field in ("current", "p95", "forecast"):
                metric[field]["reason"] = reason
                if reason.startswith("not_applicable"):
                    metric[field]["status"] = "not_applicable"
            continue
        coverage = view["coverage"]
        start, end = instant(coverage["window_start_at"]), instant(coverage["window_end_at"])
        leases = []
        for record, typed in typed_records(view):
            if typed["family"] != pool["family"]:
                continue
            address = int(ip_address(typed["address"]))
            if not any(left <= address <= right for left, right in intervals):
                continue
            if instant(typed["observed_at"]) <= clock:
                leases.append((address, instant(typed["lease_start_at"]), instant(typed["lease_end_at"])))
                metric["input_references"].append(reference(view, record))

        def occupancy(sample):
            return len({address for address, left, right in leases if left <= sample < right})

        current = occupancy(clock)
        metric["current"]["positive_observed_addresses"] = str(current)
        if coverage["effective_complete"]:
            metric["current"].update(status="available", occupied_addresses=str(current),
                                     utilization_pct=100 * current / capacity)
        else:
            metric["current"]["reason"] = "incomplete_coverage; positive observations are a lower bound"
        # Version changes conservatively invalidate history until reset/reseed.
        # No historical capacity timeline is fabricated from today's geometry.
        consistent = pool["pool_version"] == 1 and prefix["version"] == 1
        eligible = lambda sample: bool(consistent and coverage["effective_complete"] and start <= sample < end)
        values = []
        for index in range(720):
            sample = window_start + timedelta(hours=index)
            value = occupancy(sample) if eligible(sample) else None
            metric["history"].append({"at": stamp(sample), "occupied_addresses": str(value) if value is not None else None})
            if value is not None:
                values.append(value)
        metric["p95"]["eligible_samples"] = len(values)
        if len(values) == 720:
            value = _p95(values)
            metric["p95"].update(status="available", occupied_addresses=str(value), utilization_pct=100 * value / capacity)
        else:
            metric["p95"]["reason"] = "scope_or_capacity_changed" if not consistent else "incomplete_30_day_sample_coverage"
        positive_overlap = any(left < min(clock, end) and right > max(window_start, start) for _, left, right in leases)
        if positive_overlap:
            metric["lease_overlap_30d"] = True
        elif consistent and coverage["effective_complete"] and start <= window_start and end >= clock:
            metric["lease_overlap_30d"] = False

        daily = []
        # Consecutive full UTC days ending at the last completed demo day.
        for days_back in range(1, 31):
            day_start = last_day_end - timedelta(days=days_back)
            samples = [day_start + timedelta(hours=hour) for hour in range(24)]
            if not all(eligible(sample) for sample in samples):
                break
            daily.append({"day_start_at": stamp(day_start), "occupied_addresses": str(_p95([occupancy(sample) for sample in samples])),
                          "eligible_samples": 24})
        daily.reverse()
        forecast = metric["forecast"]
        forecast.update(complete_days=len(daily), daily_p95=daily,
                        window_start_at=daily[0]["day_start_at"] if daily else None,
                        window_end_at=stamp(last_day_end))
        if not consistent:
            forecast["reason"] = "scope_or_capacity_changed"
        elif metric["current"]["status"] != "available":
            forecast["reason"] = "missing_complete_current_evidence"
        elif current >= capacity:
            forecast.update(status="exhausted", days_to_full=0, baseline_addresses=str(current))
        elif len(daily) < 14:
            forecast["reason"] = "fewer_than_14_consecutive_complete_days"
        else:
            ys = [int(day["occupied_addresses"]) for day in daily]
            baseline = ys[-1]
            average_x = (len(ys) - 1) / 2
            average_y = sum(ys) / len(ys)
            slope = sum((x - average_x) * (y - average_y) for x, y in enumerate(ys)) / sum(
                (x - average_x) ** 2 for x in range(len(ys)))
            forecast.update(slope_addresses_per_day=slope, baseline_addresses=str(baseline))
            if baseline >= capacity:
                forecast.update(status="exhausted", days_to_full=0)
            elif slope <= 0:
                forecast.update(status="no_positive_growth", reason="nonpositive_daily_p95_slope")
            else:
                days = (capacity - baseline) / slope
                forecast.update(status="beyond_horizon" if days > 365 else "available", days_to_full=days)
                if days <= 365:
                    forecast["estimated_full_at"] = stamp(clock + timedelta(days=days))
    return results
