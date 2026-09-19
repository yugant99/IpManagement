# Part 3: reconciliation and evidence

Owner: rules agent. Core goals: G09–G15. Stretch: G16. Branch: `codex/part-3-reconciliation`.

## Win

A user opens a discrepancy and sees the input records, applicable rule, time window and limitations that explain it.

## Inputs and owned work

Consume Part 1's scoped model and Part 2's typed observations. Own assigned calculation/rule modules. Emit the agreed saved-run/finding shape for dashboard and exports.

Implement pool pressure, oversized pool, zombie candidate, ghost scope, unregistered managed announcement and missing expected route. Also distinguish concurrent assignment conflicts from sequential reuse, valid hierarchy and cross-namespace overlap.

## Semantics

Inactivity over a complete applicable 30-day DHCP window creates a candidate only. Missing/stale/failed evidence produces unknown and suppresses unsupported absence conclusions. Route matching follows the recorded scope/announcement policy, not arbitrary exact-string joins. Count distinct active allocations at a time, not DHCP event volume.

Pressure is p95 occupancy >=80% OR a valid forecast <60 days to full; oversized is 30-day p95 <50%. Consume the shared backend calculation delivered first within G17; do not depend on the G17 UI or build another forecast. Known true makes the pressure OR true; both known false make it false; otherwise it is unknown. Read the calculation and eligibility details in `docs/IMPLEMENTATION_DECISIONS.md`.

## Acceptance and limits

All conditions have evidence, healthy controls and insufficient-evidence controls. Changing eligible inputs changes actual rule outputs. No reclaim/withdraw execution, traffic inference from leases, event bus, collector fleet or broad policy engine.

Handoff: rule definitions/version, run/finding examples, coverage assumptions, calculated sample outputs and actual verification status. Historical comparison UI remains stretch; retaining immutable saved runs and their source references for pinned reads is core.
