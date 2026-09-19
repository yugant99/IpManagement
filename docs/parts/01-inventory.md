# Part 1: inventory and API

Owner: lead/inventory agent. Core goals: G01–G03. Stretch: G04. Branch: `codex/part-1-inventory`.

## Win

Find a scoped IPv4/IPv6 prefix or address and explain its owner, purpose, hierarchy and intended assignment. Supply one stable application/API foundation to every other part.

## Inputs and owned work

Read architecture, contracts and the goal scorecard. Own initial backend/module/schema/API wiring and coordinate migrations/locks. Agree UI-shell ownership with Part 4. Supply a small fixed IPv4 allocation pool for Part 5.

Preserve intended IP-level assignments, not just prefix totals. Support valid repeated private addresses in isolated scopes. Parent/child containment is not automatically a conflict.

## Output

Scoped inventory API, detail/search/filter results, common schemas and data access conventions. Establish runtime command/module/locks for Part 6; mark their actual readiness in status. Document API payloads from the implementation rather than maintaining a competing speculative schema.

## Acceptance and limits

Inventory is persisted, searchable and traceable to sources. IPv6 can be represented without enumerating hosts. No hardcoded UI-only inventory. General subnet editing, user-defined schemas, multi-tenant security and full IPAM replacement are outside the core.

Handoff: record branch/commit, schema/API examples and readiness for Parts 2–6. Do not change a shared contract after another lane relies on it without coordinating the change.
