# Part 1: inventory and API

Owner: lead/inventory agent. Original core: G01–G03. Current questionnaire priority also includes bounded G04 editing/custom metadata and domain/region context; see `docs/QUESTIONNAIRE_SCOPE_DELTA.md`. Branch: `codex/part-1-inventory`, with separate branches per distinct feature.

## Win

Find a scoped IPv4/IPv6 prefix or address and explain its owner, purpose, hierarchy and intended assignment. Supply one stable application/API foundation to every other part.

## Inputs and owned work

Read architecture, contracts and the goal scorecard. Own initial backend/module/schema/API wiring and coordinate migrations/locks. Agree UI-shell ownership with Part 4. Supply a small fixed IPv4 allocation pool for Part 5.

Preserve intended IP-level assignments, not just prefix totals. Support valid repeated private addresses in isolated scopes. Parent/child containment is not automatically a conflict.

## Output

Scoped inventory API, detail/search/filter results, common schemas and data access conventions. Establish runtime command/module/locks for Part 6; mark their actual readiness in status. Document API payloads from the implementation rather than maintaining a competing speculative schema.

## Acceptance and limits

Inventory is persisted, searchable and traceable to sources. IPv6 can be represented without enumerating hosts. Prioritize child-prefix creation, safe empty-prefix modification, string custom fields and scoped domain/region grouping (003/026/027; with Part 4 for 035/095). These are real API writes with validation/audit/revision changes. Refuse bounds edits for prefixes with allocations, children or attached pools; preserve pool ranges/exclusions and staged-import authority. A generic schema designer, tenant security and full IPAM replacement remain outside scope.

Handoff: record branch/commit, schema/API examples and readiness for Parts 2–6. Do not change a shared contract after another lane relies on it without coordinating the change.
