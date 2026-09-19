# Part 4: dashboard and capacity

Owner: UI/calculation agent. Core goals: G17–G18, with Part 1 for G02. Stretch: G19–G20. Branch: `codex/part-4-dashboard`.

## Win

Understand inventory discrepancies and pool capacity from a readable browser dashboard, then inspect the evidence behind a number or finding.

## Inputs and owned work

Use the common API and saved calculations. Own assigned React views/components and the bounded forecast module by agreement with the lead. Coordinate shared navigation/build configuration once; do not fork the app shell.

Inventory, source status, findings/detail, capacity and workflow should share layout/type/color/state conventions. Use restrained motion and reusable empty/loading/error/unknown states. Do not add a visual library because a generic skill demands it.

## Output

Computed overview totals, working filters/drilldown, lease-occupancy history and an explained simple positive-growth exhaustion estimate. Handle no-growth, already-exhausted and insufficient-history cases. Show capacity denominator and observation window. Distinguish candidate space from released space.

## Acceptance and limits

Detail and overview agree for the same saved run. Every action uses the real local API. Synthetic/unknown/simulated states remain visible. No disconnected mock charts, traffic utilization claim, advanced model, separate metrics generator or IPv6 host-density arithmetic.

Handoff: routes, reusable components, API dependencies, built asset location and implemented-versus-placeholder list. Part 6 receives a real build path, not only a development server command.
