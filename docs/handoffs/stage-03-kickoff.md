# Approved Stage 3 kickoff: main capabilities

**START A NEW IMPLEMENTATION CHAT — Stage 3.** Approved by persistent lead `01a0b845-6c8d-7021-a5c9-15e673db07c9` after the [source review](stage-02-lead-review.md). Permission covers assigned source implementation, not runtime acceptance or application merges. No Stage 3 task is registered yet.

This supersedes the PR #8 worker draft `stage-03-main-capabilities.md`. Use the final PR #8 commit below, not the earlier code-only commit. The original task remains overseer; prior workers remain available for assigned fixes.

## Complete copyable prompt

```text
Start Stage 3: IPAM main capabilities in https://github.com/yugant99/IpManagement, under persistent lead task 01a0b845-6c8d-7021-a5c9-15e673db07c9. Canonical checkout /Users/yuganthareshsoni/Downloads/Ip_inventory stays lead-owned. Do not restart planning, grill the user or take over global acceptance.

Read current main's root AGENTS.md and DEVELOPMENT_RULES.md, then docs/PROJECT_OVERSIGHT.md, docs/STATUS.md, docs/CURRENT_HANDOFF.md and docs/handoffs/stage-03-kickoff.md before using older application branches. Also read docs/handoffs/stage-02-lead-review.md, PR #8's stage report/STAGE2_API.md/FIRST_PATH.md, PR #7's data handoff/schema, and the contracts, implementation decisions, questionnaire priorities/scope delta/row map, parts 1–5 and skill playbook under docs/.

Accepted source dependencies, all unmerged and runtime-unverified:
- Application: PR #8, codex/part-2-first-path, 8a1a122737618748c58c5a8fc31b58a3b5f6f37e.
- Inherited foundation: PR #5, codex/part-1-foundation, c6131c38a460c13c3a189ee64a530042b2a2bf0f.
- Fixtures: PR #7, codex/part-2-synthetic-data, 907f6e7bf32f23f36d270da49c3177b015c8bfae.

Inspect Git/PR/worktree state. Create isolated /Users/yuganthareshsoni/Downloads/Ip_inventory-stage-3 on codex/stage-3-main-capabilities from exact PR #8. Preserve any existing worktree/work; do not reset or duplicate workers. The lead permits normal merges of exact PR #7 and current published lead documentation into this feature integration branch, preserving commits. Do not substitute later application commits without coordination. This does not authorize application PR merges into main. Report your task ID, baseline, ownership and first slice.

Deliver in dependency order:
1. Explicit fresh-store rich-inventory setup, preserving original seed IDs and minimal default. Never overwrite initialized intended state; changed-baseline imports stay staged. Implement a seed helper and send its interface to the state-command owner for any CLI wiring.
2. Typed DHCP import using existing receipt/raw/replay and source/scope/time eligibility contracts. Deliver ONE shared backend occupancy/p95/forecast calculation before pressure rules; save its results for rules, UI and exports.
3. Preserve G13 missing-route behavior. Complete pressure, oversized, zombie-candidate, ghost-scope, unregistered-managed-announcement and concurrent-assignment-conflict paths with healthy/unknown controls. Follow half-open time, distinct occupancy, completeness and freshness rules. Missing/stale/partial/ambiguous evidence stays unknown; cross-scope reuse is not a conflict. Expected labels never drive calculations. Candidates are not safe-to-reclaim claims.
4. Add bounded questionnaire slices: validated child-prefix/safe metadata edits; domain/IPv6 child planning; two-run comparison and one report preset/export; one-static-pool request/review/local-allocation/audit; then finding exception/notification queue. Preserve exact-candidate/version checks, server-side actor permissions, no self-approval, idempotency and atomic allocation/audit.
5. RFP-043 import trigger and RFP-081 actual fictional-team handoff are conditional on prerequisites. Scheduling RFP-068 is last and deferrable. Keep hour-14 feature freeze and the final integration reserve; this task does not restart the 20-hour budget.

You own assigned application/import/calculation/rule/inventory/workflow modules, seed helper and frontend views. One Stage 3 coordinator owns store.py, schema/migrations, app.py and common UI integration. Give independent agents disjoint modules, feature branches and worktrees. Preserve identity, explicit migration and locking helper contracts; coordinate schema/helper changes affecting state commands. No new services/database/framework or dependency upgrades.

Reserved paths—do not edit:
- Core state owner 01a0b8ae-bd65-7331-b548-da5dca1e0d5e, codex/part-1-state-commands: backend/ipam_demo/state_ops.py, backend/ipam_demo/__main__.py, docs/STATE_OPERATIONS.md, docs/handoffs/part-1-state-commands.md. Route CLI wiring here. Reset/backup/restore correctness stays here; backup also requires stopped service/exclusive access.
- Data owner 01a0b8b9-82fb-7a11-bc50-ec3a5b234729: fixtures/, docs/SYNTHETIC_DATA.md, docs/handoffs/part-2-synthetic-data.md. Consume files; route corrections to that owner.
- Spencer: Dockerfile, compose.yaml, .dockerignore, scripts/ops/, docs/RUNNING.md, docs/parts/06-portability.md, docs/handoffs/part-6.md. Packaging/operator handoff stays with him; no presentation.
- Delivery-method owner 01a0b8db-76df-7511-b024-9d3deb589074: docs/DELIVERY_METHOD.md, docs/handoffs/delivery-method.md. PR #9 is separate, awaiting review, under a no-merge instruction.
- Lead: global instructions/status/handoff/oversight, shared contracts and questionnaire maps. Propose necessary contract updates to the lead; record actual interfaces in docs/STAGE3_API.md and your stage report.

Route existing Stage 2 defects to 01a0b8c2-f283-7cf1-9128-85e9164f5fe9; coordinate narrow shared-file fixes. Do not create duplicate tasks. Use bounded subagents and separate codex feature branches/worktrees. You may combine reviewed Stage 3 features on your integration branch; main merges remain lead-owned. Commit coherent changes; push after three or earlier for handoff. Use selective skills, not automatic interviews/audits.

No tests, smoke/type checks, builds, generators, runtime/browser, container/VM or infrastructure commands. Do not add tests or install dependencies without an explicit user request. Inspect source and record pending evidence; do not call source review runtime acceptance. PART6_READY remains no until lead acceptance. Preserve 111 questionnaire rows and partial/documentary limits; 65/67 are targets, not completed counts.

Stop at READY FOR PROJECT-LEAD REVIEW — Stage 3. Push exact SHAs/PRs and write docs/handoffs/stage-03-report.md: task/worktree/ownership, implemented slices, unmerged dependencies, actual versus unobserved evidence, changed RFP IDs/gaps, interfaces and blockers. Draft Stage 4 integration/freeze prompt. Do not self-accept, merge application PRs into main, start Stage 4 or declare project completion. The original task continues oversight.
```
