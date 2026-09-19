# Stage 2 pickup: first complete path

**START A NEW CHAT — Stage 2: first complete path**

This is the Stage 1 worker's draft, ready for the persistent project lead to review and publish against an accepted baseline. Stage 1 has a pushed source checkpoint; runtime evidence and PR acceptance remain pending. The original **Build synthetic inventory demo** task remains the lead. Do not infer a merge or accepted stage from this draft.

## Actual handoff state

| Field | Recorded state |
|---|---|
| Repository | `https://github.com/yugant99/IpManagement` |
| Canonical checkout | `/Users/yuganthareshsoni/Downloads/Ip_inventory`; leave it under lead ownership |
| Stage 1 worktree | `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-1` |
| Pushed code dependency | `codex/part-1-foundation` at `ea51aa64b1780fa5c171e95ae59a619bf0109d52` |
| PR/merge | [Draft PR #5](https://github.com/yugant99/IpManagement/pull/5), unmerged at preparation |
| Integration main | `50a1dce9406ea8e9e52c032c321bb6ebfea063f8`; foundation is an unmerged prerequisite |
| Contract | `demo-v2-questionnaire`, additive `FOUNDATION_API.md` revision 1; SQLite schema version 1 |
| Source implemented | Installed-package metadata/resources; serve/seed CLI; scoped inventory APIs; SQLite schema; small deterministic seed; React/Vite inventory/detail; dependency locks |
| Evidence | Source review and lock generation only; no package install/build/type/tests/runtime/browser checks |
| Remaining state commands | Reset/backup/restore absent; `PART6_READY=no` |
| Richer fixtures | Separate `codex/part-2-synthetic-data` task, owned `fixtures/`; last inspected remote still at documentation baseline `50a1dce`. Refresh its current handoff/PR |
| Other work | No Stage 2 import, observations, findings or rule implementation yet; Spencer retains Part 6 |

Stage 1 feature worktree was clean at the code checkpoint. The report and this draft are a subsequent documentation publication on the same branch. Refresh all relevant Git state before pickup and preserve newer/dirty work. The initial dirty oversight changes in the canonical checkout were preserved and later published by their owner; no reset/stash/copy-over was used.

## Read order and next outcome

Read applicable `AGENTS.md`, `DEVELOPMENT_RULES.md`, `PROJECT_OVERSIGHT.md`, `CURRENT_HANDOFF.md`, `STATUS.md`, [Stage 1 report](stage-01-report.md), [FOUNDATION.md](../FOUNDATION.md), [FOUNDATION_API.md](../FOUNDATION_API.md), shared contracts/implementation decisions, Parts 2/3/4, questionnaire priorities/row map and the richer-data task's actual published handoff.

Deliver one connected path: **versioned source JSON import → saved immutable raw references and typed observations → one computed saved finding → API/browser evidence detail**. Use the existing service/database/UI and the agreed source/run/scope/time definitions. Select one of the fixed rules whose required fixture evidence is available; keep a healthy and insufficient-evidence control. Do not start all six rules, allocation workflow, capacity forecasting or packaging just to widen scope.

Coordinate ownership before edits. Create `codex/part-2-first-path` in a fresh `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-2` worktree, or preserve an existing owner if that branch/path already exists. Prefer the current lead-accepted main after foundation merge; if still unmerged, name the exact current foundation dependency and obtain lead coordination before branching from it. Do not start application work from the documentation-only main or switch another worker's checkout.

Stage 2 owns agreed backend import/observation/rule modules, the necessary coordinated schema migration and UI views. Shared startup/locks/schema are centrally coordinated; no second backend or database. Rich fixture source/generator remains with its data owner. Spencer keeps packaging; core retains correctness of state commands in its assigned later work.

## Behavior and limits to carry forward

- Existing seed initializes intended state. Changed inventory imports remain staged and never overwrite later approved state. Richer seed fixtures are not automatically promoted into the active ledger.
- Versioned JSON limits: 10 MiB/10,000 records. Receipt counts are mutually exclusive accepted/rejected/duplicate and sum to input. Whole-batch identity/hash replay is idempotent; changed content under the same identity is a conflict.
- Preserve raw source/run/record references, scope, UTC half-open validity intervals, explicit fixed demo clock and real ingestion time. Select the latest accepted source batch without silently reverting to older complete evidence. Required rejected rows make effective completeness false.
- Save rule/version, run ID, subject/scope, severity and evidence state separately, explanation, references, evaluated window, limitations and proposed action. API overview/detail uses the same saved result; missing/stale/incomplete evidence remains unknown.
- Expected fixture outcomes are for independent comparison, never a detection input. No hardcoded finding totals, live-network claim or safe-reclaim conclusion.
- Keep dependency locks stable unless a concrete change needs coordination. Python is 3.12; npm graph expects Node 22.12+ within 22 or Node 24. Author Node 23 was unsupported; no build result exists.
- No tests, smoke/type/build/runtime/browser checks without explicit user request. No container/VM/cloud/public-deployment authority. Source review and authored code are not runtime evidence. No application validation was retroactively authorized by this handoff.

## Exit boundary

Stop with the first complete path implemented and pushed, actual interfaces and one fixture-to-result explanation documented, and evidence clearly split between source review and authorized observed behavior. Generate a Stage 2 worker report plus draft Stage 3 pickup, submit global update wording to the persistent lead, and display **READY FOR PROJECT-LEAD REVIEW — Stage 2**. Do not start Stage 3 here. If the path is disconnected around lead hour 6, surface the exact blocker and cut optional breadth. Preserve the overall hour-14 feature freeze.

## Paste-ready prompt

```text
Start Stage 2: first complete path in https://github.com/yugant99/IpManagement.
Canonical checkout: /Users/yuganthareshsoni/Downloads/Ip_inventory; keep that checkout under the persistent project lead. Stage 1 worktree: /Users/yuganthareshsoni/Downloads/Ip_inventory-stage-1.

Read AGENTS.md, DEVELOPMENT_RULES.md, PROJECT_OVERSIGHT.md, CURRENT_HANDOFF.md, STATUS.md, docs/handoffs/stage-01-report.md and docs/handoffs/stage-02-first-path.md, then FOUNDATION_API.md, FOUNDATION.md, relevant contracts and Parts 2/3/4. Planning is complete; implement without restarting the interview.

Stage 1 code dependency is codex/part-1-foundation at ea51aa64b1780fa5c171e95ae59a619bf0109d52, draft PR #5, based on main50a1dce9406ea8e9e52c032c321bb6ebfea063f8. Later documentation commits may extend it. Inspect current Git/PR state, preserve newer/dirty work, and follow the lead-accepted baseline. If foundation remains unmerged, coordinate that exact dependency with the persistent lead before starting; do not branch from an empty main. Use codex/part-2-first-path in an isolated Ip_inventory-stage-2 worktree, preserving any existing owner.

Implement versioned source import -> immutable raw references and typed observations -> one computed saved finding -> API/browser evidence detail. Reuse the current FastAPI/SQLite/React foundation. Read the separate codex/part-2-synthetic-data owner's actual handoff and reconcile source fields/IDs centrally; do not edit its fixtures/generator in parallel. Preserve scope/time/provenance, exclusive receipt counts, replay identity, incomplete-evidence unknown states and staged intended-baseline authority. Never read expected-outcome labels to decide findings.

Current foundation is source-reviewed only. No app install/build/type/tests/runtime/browser checks were run. Keep the explicit-test-request and infrastructure limits; PART6_READY=no, with reset/backup/restore missing. Spencer owns Part 6 packaging. Use the 111-row priorities, bounded skills, explicit file ownership and separate worktrees. Commit coherent changes and push after three or before handoff.

Stop at the first-path Stage 2 checkpoint. Report actual SHA/PR, implemented versus observed/unverified behavior and gaps; generate the Stage 3 draft prompt and proposed global updates for the original Build synthetic inventory demo lead. Display READY FOR PROJECT-LEAD REVIEW — Stage 2. Do not merge independently or start Stage 3 unless I ask.
```
