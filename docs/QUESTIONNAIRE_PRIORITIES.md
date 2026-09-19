# Questionnaire-first delivery plan

Status: planning revision, 2026-09-19. Supersedes the 22-of-30 internal-goal percentage as the success headline. The original 30 goals remain useful work references; no application capability is implemented or demonstrated yet. This revision follows the user's request to maximize useful coverage of the actual 111 questionnaire rows, including architecture, deployment and delivery artifacts.

## What the 111 rows require

Each row has exactly one primary delivery category below, even when several teams contribute. These are analyst categories, not workbook sections or official weights. [The row map](QUESTIONNAIRE_ROW_MAP.md) records every ID, proposed evidence and remaining gap.

| Primary category | All rows | Original core plan addressed | Prioritized revision | With import trigger + team handoff |
|---|---:|---:|---:|---:|
| Application, data, workflow and reporting | 49 | 36 | 44 | 45 |
| Architecture, deployment and resilience | 15 | 5 | 5 | 5 |
| External integrations and identity | 19 | 2 | 2 | 2 |
| Scale and performance | 5 | 0 | 0 | 0 |
| Delivery, process and business evidence | 23 | 10 | 14 | 15 |
| **Total** | **111** | **53** | **65** | **67** |

The old 39/5/9 split was a feasibility split, not code/deployment/documentation ownership. In particular, the old 39 already included architecture, backup and health-related rows; adding deployment rows on top would double count them.

**65/111 = 58.6%; 67/111 = 60.4%; optional scheduling reaches 68/111 = 61.3%.** These are unique rows with a planned concrete demonstration or supporting artifact, including explicitly partial evidence. They are not percentages of fully satisfied requirements. A roadmap sentence alone earns no implementation credit; documents count only where the row actually asks for a design, process, method or delivery artifact. RFP-105's proposed roadmap is a draft deliverable, not a vendor commitment.

Report each row as demonstrated in the agreed synthetic scope, partially demonstrated, design/document supplied, or not demonstrated, with an evidence pointer and remaining gap. Synthetic inputs do not weaken a calculation that really works; a missing capability is still missing. The workbook's existing answers remain untouched.

## Build the small additions into the existing work

The previous plan already occupied the 20-hour lead window. These are prioritized fold-ins, not free extra time. Keep the final six hours for integration and handoff, and Spencer's 6–8 hours for Part 6. Use separate owned lanes; no blanket increase in agent count or test runs.

| Bundle | Smallest useful result | New rows beyond the original 53 | Owner / incremental focused effort |
|---|---|---|---|
| Inventory editing | Create a child prefix; edit safe prefix bounds/owner/tags; string key/value custom metadata; real validation and audit | 003, 027 | Part 1 + UI; 1.25–2.25h |
| Domain and IPv6 planning | Explicit network-domain grouping; IPv6 child-prefix capacity and first-free preview; persist a selected child under a fictional region parent | 026, 035, 095 | Parts 1/4; 1–1.75h |
| Run history and useful exports | Compare two stored runs; save one report preset; export actual findings/audit | 071; strengthens existing 006/069/078 | Parts 3/4; 0.75–1.25h |
| Exception handling | Actual finding notification in-app; owner, acknowledged/escalated state and reason/history | 072, 082 | Part 5 + UI; 0.75–1.5h |
| Delivery method pack | Review cadence/checklist; improvement backlog method; domain migration waves/rollback plan; proposed 24-month roadmap with assumptions | 083, 086, 088, 105 | Lead/documentation lane; 2–3h shared pack, also improves existing delivery rows |

Those five bundles add **12 unique rows**, taking 53 to 65. Product additions total roughly **4–7 focused lane hours** after the shared foundation exists; the document pack adds **2–3**. Parallel work can overlap the lead's elapsed window, but integration and unavailable dependencies cannot be multiplied away. This is an ambitious target, not measured throughput.

The next two additions are the preferred route from 65 to 67, only after the underlying import and queue work:

- **043, import-triggered reconciliation:** after an accepted evidence import commits, invoke the existing reconciler. Record which import triggered it and the result; show busy/failure separately from successful import. Fixed callback, no event bus. Estimated 0.25–0.75h.
- **081, team handoff:** extend the actual exception queue with two fictional named teams, an assigned recipient, acknowledgement/escalation and audit. A team-name label alone does not qualify. Estimated 0.25–0.5h after the queue exists.

**068, configurable local scheduling**, is a later option to reach 68: one-process timer using the existing run lock, saved interval/last/next status and visible busy/failure outcomes, approximately 0.75–1.25h. It is not required for the 67-row breadth target. It does not discover a real network.

## What to simplify or defer

- Reuse the inventory form, one dashboard shell and saved-run data. Keep visual polish to readability; no bespoke executive layout, animation pass or separate reporting platform.
- Keep assessment and delivery material as a small shared document pack with explicit fictional examples. Do not build a maturity-assessment wizard or duplicate every document as a UI screen.
- Defer 057/070's local reclaim/remediation extension, 111's configurable workflow designer, live external connectors, tenant isolation, enterprise identity, HA and scale work. Do not trade allocation correctness or evidence provenance for these rows.
- Keep saved reports to one filter/column preset and CSV export. Keep IPv6 to prefix arithmetic and bounded prefix assignment, with no host enumeration or IPv6 subscriber allocator.
- At hour 6, require the original source-to-finding browser path. At hour 11, select remaining additions based on working prerequisites. Freeze new features at hour 14. Unfinished rows remain missing/partial; do not lower the denominator or fill a gap with a label.

## Architecture changes required now

Keep React/Vite, one FastAPI worker and local SQLite. No database replacement, queue, microservice split, cloud dependency or general plugin framework is needed for the selected additions.

1. Extend scoped inventory with domain/region context and a small custom-metadata map; scope identity remains the isolation key. Reuse prefix parent/child relations for regional and IPv6 planning.
2. Allow controlled local intended-inventory edits with actor checks, validation, audit and revision changes. Changed imported baselines still remain staged. Refuse edits that would invalidate existing allocations or child containment.
3. Expose already-persisted runs for comparison and a small report preset. Unknown evidence cannot resolve a prior anomaly.
4. Add a small exception record linked to a finding, rather than a workflow engine. The conditional import callback and timer call the existing reconciler and preserve its one-run lock.

These contracts are in [QUESTIONNAIRE_SCOPE_DELTA.md](QUESTIONNAIRE_SCOPE_DELTA.md). They supersede only the relevant earlier stretch/exclusion statements; the source thresholds, synthetic evidence rules and state safety remain unchanged.

## Architecture and deployment do count, but against the right row

- **010:** a centralized API/data design is concrete architecture evidence once implemented. **012/013:** real API access and API-driven UI substantiate API capabilities without a separate feature for every screen.
- **018:** real backup/restore and **090:** the application package are valid delivery capabilities. **022** still needs an actual health alert, not merely a health endpoint. **091** is only partial while orchestration is a fixed local workflow.
- **023:** host portability is useful design evidence; hybrid-cloud integrations need more. **024:** a Docker image packages this app; it does not itself manage virtual/container network inventory. Neither gets added to the 65/67 target solely for a container label.
- **014–017/019–020:** the selected single-instance app does not supply HA, failover, geographical DR or measured recovery objectives. A bigger VM does not remove those gaps.
- **021:** transport TLS alone does not establish encryption at rest. **008:** network scopes do not provide tenant access isolation. Their concrete implementation/configuration evidence remains absent.
- **025/093/094/096/097:** carrier scale, record volume, provider DNS/DHCP and large-team concurrency remain future engineering and evidence. The SQLite choice optimizes portable demo delivery; its single-writer constraint means a production concurrency design may need a client/server database and broader changes. See [SQLite's usage guidance](https://www.sqlite.org/whentouse.html).

The future production design should be a short proposed path with workload assumptions, database/service changes, identity/integration needs, HA topology and measurements required. Do not build it this weekend or describe it as already supported. Host packaging and network management are separate concerns; [Docker's networking documentation](https://docs.docker.com/engine/network/) describes actual container networking beyond image packaging.

## Ownership and the remaining gaps

Spencer keeps Part 6's application package, local persistence, state-command wrappers, health diagnostics and operator handoff. Do not assign him HA, SSO, scale demonstrations or presentation work. Core implements state correctness and new application behavior; the lead owns questionnaire evidence and the delivery method pack.

At 67 addressed rows, **44 remain outside the selected evidence scope**: four application rows (043 is included, while 057/068/070/111 remain), ten architecture/deployment rows, seventeen integration/identity rows, five scale rows and eight business/provider-evidence rows. The row map names each. Within the addressed 67, partial clauses still remain and must be disclosed separately.

The missing business/provider evidence includes references, a dedicated delivery-team commitment, local support, commercial licensing, SLAs and compliance evidence. Agents can prepare requested templates; they cannot invent these company facts. No commercial answer, customer reference or external commitment is authorized by this plan.
