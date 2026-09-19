# Coverage target and the 20-hour plan

**Historical baseline, retained for traceability.** The user subsequently made the 111-row questionnaire the primary scorecard. [QUESTIONNAIRE_PRIORITIES.md](QUESTIONNAIRE_PRIORITIES.md) and [QUESTIONNAIRE_ROW_MAP.md](QUESTIONNAIRE_ROW_MAP.md) now control scope: the original 22 goals link to 53 unique requirements; prioritized additions target 65, with two conditional additions to 67 and optional scheduling to 68. All include partial/documentary rows; none is full-compliance credit. The 22/30 percentage below is historical and must not headline progress.

Planning proposal only. No application has been built, tested, or demonstrated. This file contains generic planning identifiers and paraphrases; the private source workbook remains outside the public repository.

## Two denominators; neither replaces the other

The complete questionnaire has **111 technical rows**. Strictly more than 60% means at least **67 fully evidenced whole requirements**. The current feasibility assessment has 47 direct-demo candidates, 22 partial/simulated candidates, 22 enterprise-deferred requirements, and 20 business/process evidence requirements. Those are planning categories, not delivered coverage.

47/111 is 42.3%. Adding all 22 partial/simulated candidates produces 69/111, or 62.2%, but reporting that as full coverage would be wrong. Some of the 47 direct candidates are themselves broad or compound requirements whose minimum weekend behavior covers only part. A fixed local approval flow, for example, is not an administrator-configurable lifecycle framework.

The development target proposed here is **22 of 30 fixed, equally weighted demonstration goals: 73.3% of this demo scorecard**. The arithmetic threshold for more than 60% of that scorecard is 19/30, or 63.3%; aiming for 22 provides three goals of numerical margin. That margin is not permission to omit an essential end-to-end gate. Freeze the denominator before implementation; do not split goals, remove difficult goals, or award fractional credit to manufacture a percentage.

Use this explicitly named scorecard as the proposed weekend demonstration target under the delegated planning decision. It does not redefine the original request to cover a majority of the questionnaire: if success means 67 fully satisfied questionnaire rows, we cannot responsibly promise that from an empty implementation in 20 hours. State both numbers in status reports without stopping development planning for another percentage question.

`GOALS.csv` defines all 30 observable goals, exact RFP links, priority, owner, estimate, dependencies, acceptance, and limits. `REQUIREMENT_COVERAGE.csv` preserves every one of the 111 rows, its prior feasibility classification, proposed goal links and current unverified status. A goal-to-row link is traceability, not full coverage credit.

## What the 22-goal target contains

| Part | Core / total goals | Owner | Visible result |
|---|---:|---|---|
| 1. Inventory and API | 3 / 4 | Lead, inventory/UI agents | Scoped IPv4/IPv6 inventory, metadata, search/detail and documented API |
| 2. Sources and assessment | 4 / 4 | Data agent with lead | Deterministic three-source replay, raw evidence/freshness, import rejection, illustrative assessment export |
| 3. Reconciliation | 7 / 8 | Rules agent | All six Pool Watch conditions, conflict/valid-overlap distinction, healthy and unknown controls |
| 4. Capacity and dashboard | 2 / 4 | Calculation/UI agent | Occupancy history, explained forecast and calculated overview with evidence drilldown |
| 5. Approval and local allocation | 2 / 5 | Lead or workflow agent | One real local allocation path, server-enforced demo roles, visible failures and decision audit |
| 6. Portable delivery | 4 / 5 | Spencer | Startup packaging, persistent data and backup/restore/reset, local health, operator/agent handoff |
| **Total** | **22 / 30** | | **73.3% proposed demo-goal target; not delivered RFP coverage** |

These goals cover every work part, all six central anomaly scenarios, the assessment story, a persistent Phase 2 transaction, and the user's portability requirement. They are not a list of cosmetic dashboard widgets. Equal weighting is for a legible delivery score, not a statement that every goal takes equal effort. Scenario goals share one engine; the allocation goal is more expensive than a single rule.

All core goals are the intended scope. The release gates are a connected source-to-finding-to-evidence path; real calculations; explicit synthetic and unknown states; one persisted approval/allocation path; and a portable handoff preserving data. A numerical score cannot override a broken release gate.

## Budget assumptions and critical path

The estimate assumes **about 20 elapsed working hours for the lead-led development effort**, with Spencer's **6–8 hours overlapping** that window. It is not 20 hours multiplied by the number of agents. If the 20 hours means total combined human effort including Spencer, the target must be re-estimated. More agent tokens help investigate and implement bounded slices; they do not eliminate interface decisions, waiting for shared changes, or integration failures.

The CSV estimates are rough focused implementation effort per goal after shared contracts are settled. They are not measured throughput or guarantees. Some parts run in parallel, and the schedule separately reserves integration and recovery time. The plan assumes a small synthetic dataset, one service/database, an available familiar runtime, and no live external integration.

| Lead working time | Intended milestone | Parallel work and stop condition |
|---|---|---|
| Hours 0–1.5 | Freeze canonical fields, source/time semantics, rule evidence DTO, one-pool transaction and runtime contract | Spencer receives Part 6 startup contract and handoff entrypoint. No agent invents a second data model. |
| Hours 1.5–6 | Inventory + source replay + one complete finding/detail path | Data and UI work against the same fixtures. Spencer prepares package/startup docs and data-path contract. Stop expanding scenarios if the vertical path is not integrated. |
| Hours 6–11 | Six rule conditions, controls, capacity view and allocation slice | Rules/UI/workflow lanes use the frozen contracts. Lead owns integration. No new libraries or configurable workflow designer for aesthetic completeness. |
| Hours 11–14 | All core flows integrated; claims and diagnostics visible | Fix integration failures before attempting stretch work. Spencer connects actual app startup/persistence and finishes handoff. |
| Hours 14–17 | Freeze new features at hour 14; portable artifact and focused acceptance work, once authorized | One complete demonstration plus the decisive failure cases and fresh-start/persistence behavior. Record evidence and gaps. |
| Hours 17–20 | Recovery margin, final documentation and rehearsal | Freeze continues. No architecture swaps, cloud dependency or broad new test suite. Use remaining time to repair the core. |

The user’s rules prohibit tests or verification commands unless explicitly requested. The acceptance descriptions here are future targets; they are not permission to execute those commands. After authorization, use a small risk-based acceptance set around address math/scope, missing evidence, allocation transaction, and packaging. Do not repeat a whole regression suite for copy changes or use test-count growth as progress.

## Spencer's independent Part 6 package

Spencer now owns **Part 6, portable delivery**, not the old Part 5 workflow assignment. The previous plan is stale on this point. He has no presentation assignment.

Provide before he starts: canonical repository/branch, architecture decision and runtime target, exact application command/module and port, build output location, environment variables, SQLite data path, seed/reset entrypoint, health contract, supported host/CPU, owned files, forbidden shared files, and where his agent records progress. A packaging agent cannot safely infer the API module or migration command from a planning narrative.

Proposed 6–8-hour allocation: 0.5–1 hour context/runtime contract; 1–2 hours startup/package work; 1–2 hours persistence/reset/backup/restore; 0.5–1 hour health and diagnostics; 0.5–1 hour operator/agent documentation; the remaining time for integration/repair. He can prepare against the contract while the application is built, but final startup depends on the real application artifact. Optional second-host work is stretch and requires an explicitly supported target; a VM is not a prerequisite.

## What remains stretch

G04 subnet editing/custom metadata; G16 historical reconciliation/reporting; G19 IPv6 planning; G20 saved reports; G23 approved correction plus real rerun; G24 configurable lifecycle rules; G25 exception/escalation queue; G29 second supported host.

G24 is particularly likely to be post-Monday: a configurable workflow system is several additional hours and conflicts with the weekend's simplicity goal. Do not introduce it under the fixed approval workflow. G29 can become a delivery gate if the audience requires a particular remote host; settle the target before claiming portability.

No stretch goal may displace a core release gate. If core work finishes early, choose G16 or G23 according to which makes the evidence story stronger, then G25. Retain the original 30-goal denominator regardless of what finishes.

## What 67/111 full rows would actually require

There are only 47 items currently categorized as direct-demo candidates, so at least 20 more rows would need to move beyond partial/simulated/deferred/business evidence even if every one of the 47 were fully satisfied. In reality, several of those 47 require broader behavior than the proposed minimum.

Progress beyond the weekend scope requires real integration environments and credentials; production identity and operational controls; deployment, scale and resilience evidence; customer-specific assessment inputs; or organizational references, training/support/commercial commitments. Code generation cannot manufacture those facts. Additional mocked connectors would increase illustrated breadth, not convert partial integration rows into full coverage.

No numeric delivery guarantee is made. At implementation start, the demonstrated score remains **0/30 goals** and **0/111 whole requirements** until evidence exists. Update delivery status only from observed acceptance results, with separate local, partial, simulated and deferred states. Retain the full requirement text and vendor response comments privately; the public tracking table needs only generic identifiers and bounded implementation claims.
