# Locked first dispatch manifest — Main Lead 4.0

**Exact amended specification / worker base: `6b66f943b7c7783285bfd1f70859ede42380bf60`.**
Supplied original specification: `9df8393171af632b126a9801fe4cca73b1c575d1`.
Remote main at lock: `04eba98cb8673406d1e5d38c5318fb963cc77ff7`, no drift.
Lead branch `codex/main-lead-4-bridge`. The amended base is source-adopted after independent
review; it is an explicit unmerged dependency, not main or a runtime-accepted candidate.
All prepared worktrees below are created at this exact base. No worker has been invoked.

## Dispatch decision

**Manifest locked; implementation wave HELD for Terra route resolution.** OpenCode active
service has no Terra/OpenAI connection despite the user's expected availability. Fable's
Claude Max route and Codex Sol route are separately identified. No silent substitution.
After the route is resolved, lead records the route decision, dispatches T003 and T002,
and releases later work only on the exact accepted prerequisite SHA. Do not rebuild these
worktrees on another base or switch another worker's checkout. FABLE-DESIGN may review
this locked specification/manifest now; final T027 still waits for T024/T025.

| Owner | Task / prerequisites | Branch | Worktree | Exclusive file lease / status |
|---|---|---|---|---|
| Terra / OpenCode intended openai/gpt-5.6-terra | T003; adopted T001, route must resolve | codex/bridge-t003-schema | /Users/yuganthareshsoni/.codex/worktrees/ipam-bridge-terra/Ip_inventory | backend/ipam_demo/schema.sql; schema_v6.sql; store.py; seed.py. PREPARED, route held. |
| Grok 4.7 / opencode-go/grok-4.7#high | Integration sublead; supervise T002 and review contract-sensitive changes | codex/bridge-contracts | /Users/yuganthareshsoni/.codex/worktrees/ipam-bridge-grok/Ip_inventory | Source review only initially; later delivery/offline-api.md at T021. PREPARED. |
| Grok 4.6 / opencode-go/grok-4.6#medium under Grok 4.7 | T002 after T001; T019 only after accepted T002 | codex/bridge-t002-sources | /Users/yuganthareshsoni/.codex/worktrees/ipam-bridge-scout/Ip_inventory | specs/001-postmeeting-bridge/delivery/source-authority.md only for first assignment. PREPARED. |
| Luna / opencode-go/gpt-5.6-luna#medium | T007 after exact T005 + T006 integration | codex/bridge-t007-access-review | /Users/yuganthareshsoni/.codex/worktrees/ipam-bridge-luna/Ip_inventory | specs/001-postmeeting-bridge/delivery/access-review.md only. PREPARED, dependency held; no QA invocation yet. |
| Spencer / human, coordinated by Luna | T020 after T002 | codex/bridge-t020-matrix | /Users/yuganthareshsoni/.codex/worktrees/ipam-bridge-spencer/Ip_inventory | specs/001-postmeeting-bridge/delivery/integration-matrix.md only. PREPARED, no human acknowledgement inferred. |

When later dependencies arrive, fast-forward/merge them only in the assigned lane with
lead coordination; record the newly exact base in its dispatch. T004/T005 remain Terra's
next coherent features and need separately named branches after their prerequisite
checkpoint; T006 DeepSeek UI starts after T004 on disjoint files. T008/T011/T013/T016
backend leaf work is serial where workflow.py/lifecycle.py overlap. T015/T018 UI is serial.
Use task-graph.csv for all 40 dependencies, exact paths/contracts/gates. Its updated
semicolon-delimited file lists include inventory_commands.py in T005 and all three
previously omitted actor-state components in T006. No task leases a folder implicitly.

## First worker packets

The machine-readable [first-wave.json](first-wave.json) records the exact task payloads.
Each includes base, branch/worktree, owned paths, prerequisites, requested model route,
prohibited surfaces, acceptance, retained evidence, nonclaims and handoff. Pass one packet
at a time to its specified owner. Do not let the default OpenCode model select a worker.
No more than three active subleads, each at most two leaves, and no third delegation level.
Fable is direct advisory, not a sublead; Sol replaces a blocked implementation worker.

T003 success is coherent schema 6 initialization and recognized migration source that
preserves IDs, foreign keys and existing history, quarantines legacy presets and adds
only Tier A tables. Reserve schema 6 only while main remains schema 5. T003 owns store.py,
which already supplies migration recognition to the CLI/state validator; T023 remains
final recovery/readiness integration. Do not move packaging or invent Tier B tables.

T002 success is a source/field authority and unresolved vendor/business register covering
assigned FR-009/010/012/014/018/020. No vendor endpoint or authentic business fact may be
invented. Missing facts have an owner role and exact future evidence gate. T019 is a later
coherent documentary slice, not an automatic extension of T002.

T007 reviews every allowed/denied/projected/quarantined route, nested/error/list/count/
export path, complete client auth context and legacy handling at the assembled source
SHA. It is not runtime evidence. T025 later retains the explicitly requested bounded
local success/refusal/stale/replay/concurrency/unknown/aging/recovery observations on fresh
synthetic data. No routine full-suite loop; source adoption does not prove those outcomes.

Spencer's [Day 1 packet](spencer-day-1.md) has a two-hour finish within approximately eight
human hours. VM choice remains later; no infrastructure creation or paid hosting authorized.
User review: Wednesday night September 23 or Thursday September 24, America/Los_Angeles.
The [capacity plan](resource-plan.md) supplies the named 16-task path and weighted forecast;
no three-day acceptance promise. Preserve 20% reserve and hold all T029–T040 until T025.

## Review, retained evidence and stopping rules

Every worker records task/requirements, base/final SHA, exact owned diff, source or runtime
mode, actual commands/results, schema/config/input/target identifiers, sanitized artifacts,
remaining gates and a draft next prompt. Commit coherent work; push after three changes
or earlier at handoff. Source-ready reports use `READY FOR PROJECT-LEAD REVIEW — Stage 1
(post-meeting bridge)` for the foundation wave. The lead assigns later stage boundaries.

Immediate escalation: authority, history loss, shared-contract conflict, overlapping lease,
secret exposure, model/route mismatch or payment/overage requirement. Otherwise escalate
at 45 minutes without a defensible path. Supply exact files/SHA/failures/attempts/decision;
Sol replaces the blocked slot. No auto-merge, data reset, external message, cloud purchase,
customer operation, public exposure, acceptance downgrade or ledger promotion.

A passed focused check is not full Tier A acceptance. Simulation is not live ServiceNow
or provisioning. Assessment never promotes inventory. Local allocation is separate from
leased/routed/traffic state. A package is not recipient evidence; an agent is not a human
acknowledgement. The accepted 39/18/10/44 ledger remains unchanged.
