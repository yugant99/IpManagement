# Stage 3 draft pickup: main capabilities

**Worker draft for persistent project-lead review. Stage 3 has not started.** The lead must reconcile the exact accepted integration/dependency state before publishing its final next-stage prompt. A code-ready checkpoint does not satisfy runtime acceptance.

## Current source checkpoint

- Stage 2 code: `codex/part-2-first-path` at `3c193c4ca320985e3dc258b39d8af1ec6632d155`, [draft PR #8](https://github.com/yugant99/IpManagement/pull/8), currently based on foundation branch rather than main.
- Foundation: `codex/part-1-foundation`, `c6131c38a460c13c3a189ee64a530042b2a2bf0f`, unmerged [draft PR #5](https://github.com/yugant99/IpManagement/pull/5).
- Fixtures: `codex/part-2-synthetic-data`, `907f6e7bf32f23f36d270da49c3177b015c8bfae`, [PR #7](https://github.com/yugant99/IpManagement/pull/7). `fixtures/v1/first-path/` uses the current seed; the rich pack still needs an explicit safe fresh-store bootstrap path and DHCP import support.
- Lead's global publication: main `1db87d6b45e4c58c77ebc54b829740c71dcadebd`, documentation-only at preparation. Inherited global files on dependent feature branches may be stale; use the lead's current published pointers.
- Later Stage 2 documentation publication contains this draft and [worker report](stage-02-report.md). Preserve later commits; inspect current Git and PR state rather than resetting to old SHAs.

Implemented source: routing/policy import and raw evidence, one saved missing-route calculation, API/browser receipt and evidence path, schema v2 plus explicit migrate command. No application install/build/type/test/runtime/browser/migration evidence has been obtained. Details and source-derived fixture expectations are in [FIRST_PATH.md](../FIRST_PATH.md); actual payload/storage contracts are in [STAGE2_API.md](../STAGE2_API.md).

## Next deliverable and stopping point

Continue the agreed Stage 3 hours 6–11 scope under the persistent lead, with bounded independent feature lanes where useful. Preserve the already implemented missing-route rule and shared saved-run source of truth. Prioritize prerequisite gaps: explicit fresh-store rich-baseline setup without overwriting initialized state, typed DHCP import, and the one shared backend occupancy/forecast calculation needed by pressure/oversized/zombie rules. Complete the remaining rule/control paths and scoped assignment conflict semantics, then the agreed inventory/IPv6/history additions, core local allocation/audit and exception queue as the lead assigns. Do not duplicate calculation logic or turn optional breadth into a new platform.

Stop at the Stage 3 checkpoint: required lanes integrated or exact dependencies recorded, candidate SHA/PRs, actual evidence versus gaps, questionnaire contributions and a Stage 4 integration/freeze draft. Preserve the overall hour-14 feature freeze and final six-hour integration/delivery reserve. Runtime observations remain pending unless the user explicitly authorizes them; authoring more source does not erase this gate.

## Complete copyable draft prompt

```text
Start Stage 3: main capabilities in https://github.com/yugant99/IpManagement, under the persistent project lead task 01a0b845-6c8d-7021-a5c9-15e673db07c9. Canonical checkout /Users/yuganthareshsoni/Downloads/Ip_inventory stays lead-owned. Do not restart planning or rotate project ownership.

Read AGENTS.md, DEVELOPMENT_RULES.md, PROJECT_OVERSIGHT.md, CURRENT_HANDOFF.md, STATUS.md, docs/handoffs/stage-02-report.md, docs/handoffs/stage-03-main-capabilities.md, STAGE2_API.md, FIRST_PATH.md, current synthetic-data handoff, relevant contracts/parts and the questionnaire priorities/row map.

Stage 2 pushed code checkpoint is codex/part-2-first-path at 3c193c4ca320985e3dc258b39d8af1ec6632d155, draft PR #8, with unmerged foundation dependency c6131c38a460c13c3a189ee64a530042b2a2bf0f / PR #5. Fixture dependency is codex/part-2-synthetic-data at 907f6e7bf32f23f36d270da49c3177b015c8bfae / PR #7. Main was documentation-only 1db87d6b45e4c58c77ebc54b829740c71dcadebd at draft preparation. Inspect current Git/PR state and coordinate the accepted baseline with the lead; preserve later/dirty work, use separate codex feature branches and isolated worktrees. Do not independently merge into main or copy another owner's fixtures.

Continue the agreed Stage 3 path. Keep Stage 2's explicit routing-policy source, latest per-source/scope selection, immutable raw evidence and pinned saved results. Coordinate safe fresh-store rich-baseline setup, with no silent overwrite of initialized intended state; changed inventory imports remain staged. Add typed DHCP import and the shared backend occupancy/p95/forecast function before pressure rules. Implement remaining rule/control paths, scoped conflict/time semantics and the assigned inventory/IPv6/history, local allocation/audit and exception work within the existing one-app/SQLite architecture. Expected outcomes are comparison-only, never calculation inputs. Missing/stale/incomplete/ambiguous evidence remains unknown, not resolved or safe to reclaim.

No tests, smoke/type/build/runtime/browser checks have been authorized; do not add/run them without an explicit user request. No VM/container/cloud/public-deployment authority is added. Spencer owns Part 6; core owns state-command correctness and Part 5. PART6_READY remains no until real prerequisites/evidence exist. Preserve questionnaire-first accounting, explicit path ownership and coherent commits, pushing after three changes or earlier for handoff.

Stop at READY FOR PROJECT-LEAD REVIEW — Stage 3 with exact pushed SHAs/PRs, dependency state, actual versus unverified evidence, gaps and a Stage 4 draft. Keep the hour-14 freeze and integration reserve. The persistent lead owns global status/acceptance and the final next-stage prompt; do not start Stage 4 automatically.
```
