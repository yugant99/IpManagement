# Part 4: dashboard and capacity

Owner: UI/calculation agent. Original core: G17–G18, with Part 1 for G02. Current questionnaire priority includes bounded G19 IPv6 prefix planning and a minimal G20 report preset/export, alongside G16 history display. Branch: `codex/part-4-dashboard`, with separate branches per feature.

## Win

Understand inventory discrepancies and pool capacity from a readable browser dashboard, then inspect the evidence behind a number or finding.

## Inputs and owned work

Use the common API and saved calculations. Own assigned React views/components and the bounded forecast module by agreement with the lead. Coordinate shared navigation/build configuration once; do not fork the app shell.

Deliver the G17 backend occupancy/forecast module first so Part 3 can consume it for G09 pressure. Its inputs are Parts 1–2 data and coverage, not a pressure finding. The G17 chart then displays the same saved result. This is one calculation within the existing goal, not a new service or goal.

Inventory, source status, findings/detail, capacity and workflow should share layout/type/color/state conventions. Use restrained motion and reusable empty/loading/error/unknown states. Do not add a visual library because a generic skill demands it.

## Output

Computed overview totals, working filters/drilldown, lease-occupancy history and an explained simple positive-growth exhaustion estimate. Handle no-growth, already-exhausted and insufficient-history cases. Show capacity denominator and observation window. Distinguish candidate space from released space.

Pin overview, details and exports to one `run_id`. Label the 720 hourly samples as the bounded demo approximation. The backend fits daily p95 occupied-address counts over 14–30 complete consecutive days; the UI never recomputes the forecast or substitutes zero for unavailable values. See `docs/IMPLEMENTATION_DECISIONS.md` for states and limits.

## Acceptance and limits

Detail and overview agree for the same saved run. Every action uses the real local API. Synthetic/unknown/simulated states remain visible. No disconnected mock charts, traffic utilization claim, advanced model, separate metrics generator or IPv6 host-density arithmetic.

Prioritize one existing inventory form for custom metadata and a child-prefix planning panel over separate polished layouts. Show IPv6 prefix capacity without host enumeration; persist a selected child through Part 1's validated API under a region parent. Expose two-run comparison and one saved report preset using current filters. See the scope delta for exact bounds; these strengthen the actual questionnaire, not an internal widget count.

Handoff: routes, reusable components, API dependencies, built asset location and implemented-versus-placeholder list. Part 6 receives a real build path, not only a development server command.
