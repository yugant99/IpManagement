# Main Lead 5.0 pickup after T011

Prepared by Main Lead 4.0 (`01a0cade-506f-7442-97da-0cc09b4f9929`) at the user's
requested T011 stopping point. The user will start the receiving task. Main Lead 5.0
is not registered yet; no task ID is invented. Register the actual receiver only
when the user starts it with the prompt below. Earlier lead tasks then become
reference-only for new coordination; retained workers remain available for fixes.

**T011 source milestone complete.** Independent GPT-6 Sol review closed all three
findings at `3fcdb49d955c39cf08f0a0d6f9483384e43163b1`; Main Lead 4.0 accepts that
source checkpoint. Runtime and full Tier A acceptance remain pending. T012/T013
are undispatched. This is the user-requested stopping point and completed handover.

## Pickup and evidence boundary

- Canonical repository: `/Users/yuganthareshsoni/Downloads/Ip_inventory`,
  `yugant99/IpManagement`. Preserve its untracked `audit/` and `outputs/`.
- Main remains `04eba98cb8673406d1e5d38c5318fb963cc77ff7`. No bridge PR was merged to main.
- Lead documents: `codex/main-lead-4-bridge`, draft [PR67](https://github.com/yugant99/IpManagement/pull/67),
  worktree `/Users/yuganthareshsoni/.codex/worktrees/ipam-main-lead-4/Ip_inventory`.
- Final application source assembly: **`ab370a4273784bd750bf5f59289594a31d097739`**,
  branch `codex/bridge-t011-handover`, worktree
  `/Users/yuganthareshsoni/.codex/worktrees/ipam-bridge-migration/Ip_inventory`.
  It preserves accepted T011 and T010 histories on the T009/T008/access/schema base,
  plus lead records through `6cdfa984945ed905d60e7e2dbe9ca4b3add9eac7`.
  The final branch publication adds this handover and source-review documents;
  it introduces no later application change. Pick up the pushed branch publication
  and record its actual SHA when creating the next shared base.
- Current phase is **source implementation and independent source review**. No bridge
  tests, builds, typechecks, application imports, databases, servers, browser runs or
  runtime observations were performed for these slices. Do not relabel source
  acceptance as demonstrated behavior or complete Tier A acceptance.
- The original user kickoff authorizes bounded T025 local synthetic observation
  after its prerequisites. Read `delivery/authorization-and-ownership.md`; do not
  restart a permission interview or run routine feature tests early. Fresh disposable
  data only; no user-store mutation, infrastructure, customer access or deployment.
  T025 prerequisites are T018, T019, T021, T022, T023 and T024, including their
  transitive dependencies; T020 feeds the human/documentary preparation path.
- T012/T013 and later implementation were deliberately left undispatched for this
  transfer. Starting the new lead authorizes resuming already agreed Tier A work.

## Accepted source checkpoints

| Task | Exact accepted source | Draft PR |
|---|---|---|
| T002 source authority | `ab005d8bf3b6c57e0a071707796d18514c278674` | [68](https://github.com/yugant99/IpManagement/pull/68) |
| T003 schema 6 | `9c73fd8e76c092b4d8297ec4475160b71574de7e` | [69](https://github.com/yugant99/IpManagement/pull/69) |
| T004 trusted access | `c7a3bed6dfec31bd07abc613f52b64f1304a1349` | [71](https://github.com/yugant99/IpManagement/pull/71) |
| T005 API access | `c4b367b3e51028ea70327ce9c62b9fb4598491e7` | [73](https://github.com/yugant99/IpManagement/pull/73) |
| T006 UI access | `671dae8d2c74f1a426c9f29c3c1d8997d3096ad8` | [72](https://github.com/yugant99/IpManagement/pull/72) |
| T007 access review publication | `833c2c8676b205c97476ab71f4e3b2cff0a2c608` | [74](https://github.com/yugant99/IpManagement/pull/74) |
| T008 assessment core | `776f32a3eaff2be9a5bd9d09a8f5dab62e4f5509` | [75](https://github.com/yugant99/IpManagement/pull/75) |
| T009 assessment API | `daede1905304c5d5bd363ff230b5f6371763eb49` | [76](https://github.com/yugant99/IpManagement/pull/76) |
| T010 assessment UI | `4b0b7d71bff38014539d1ff3c5a06c6c06631db2` | [77](https://github.com/yugant99/IpManagement/pull/77) |
| T011 reservation core | `3fcdb49d955c39cf08f0a0d6f9483384e43163b1` | [78](https://github.com/yugant99/IpManagement/pull/78) |
| T019 qualification | `4034c765fce8a68f8cd73195c73f9a3bdd185d24` | [70](https://github.com/yugant99/IpManagement/pull/70) |

T007 reviewed code assembly is `aee0ade8bbeb6405aab4a6cf0c35079d76e6318e`;
its publication adds the retained source review. Review reports under
`specs/001-postmeeting-bridge/delivery/` explain findings and corrections.
All draft PRs retain their original dependencies; a GitHub PR state is distinct
from inclusion in a source assembly.

## Worker registry and next leases

These existing tasks are idle once their accepted slice closes. Reuse them for
assigned corrections; do not duplicate their implementations or change their checkout.

| Task | Actual task ID | Worktree | Branch |
|---|---|---|---|
| T005 | `01a0cb1e-a711-70a3-a74d-5651989a0355` | `/Users/yuganthareshsoni/.codex/worktrees/faf2/Ip_inventory` | `codex/bridge-t005-api` |
| T006 | `01a0cb1f-4086-7e40-a613-3fe2255ff4ec` | `/Users/yuganthareshsoni/.codex/worktrees/1632/Ip_inventory` | `codex/bridge-t006-ui` |
| T008 | `01a0cb4a-4b2c-7451-b2dc-8ae0508a8448` | `/Users/yuganthareshsoni/.codex/worktrees/cf7c/Ip_inventory` | `codex/bridge-t008-assessment` |
| T009 | `01a0cb5e-f055-7751-b79c-a60c9662a0c5` | `/Users/yuganthareshsoni/.codex/worktrees/eb8d/Ip_inventory` | `codex/bridge-t009-migration-api` |
| T010 | `01a0cb5f-6dcf-7080-90ea-fffcc1743645` | `/Users/yuganthareshsoni/.codex/worktrees/e121/Ip_inventory` | `codex/bridge-t010-migration-ui` |
| T011 | `01a0cca1-3873-79a0-ad54-e3f2ae0f25fb` | `/Users/yuganthareshsoni/.codex/worktrees/7802/Ip_inventory` | `codex/bridge-t011-reservations` |

Use these IDs directly with task read/wait/message tools. The app list omitted
these tasks during this run; omission did not mean deletion or inactivity.
Client setup IDs are not real task IDs. The outgoing Sol internal reviewer
`/root/sol6_access_review` is local to the old lead's agent tree; a fresh lead must
use its own independent reviewer rather than assume that relative name is routable.

After takeover, pin a shared base from the final source assembly and freeze the
T012/T013 wire boundary before dispatch. T012 leases only `backend/ipam_demo/app.py`
and `models.py`; T013 leases only `ticket_handoff.py` and `workflow.py`. These can
run in parallel in isolated `codex/` worktrees with GPT-6 Luna high, then receive
independent GPT-6 Sol high source review. T014 follows both; T015/T016 follow their
actual graph edges and must not race on shared UI/backend files. Do not advance
the frozen review bases `codex/bridge-migration-integration` (`36dbfb90f3178c07ed9c7d0a55b54370a563bf7f`)
or `codex/bridge-lifecycle-integration` (`3add18986096e8fd9bc6ac509db28fc08b6bf2a6`).

## Decisions to preserve

- Current routes: Astra lead; GPT-6 Luna high implementation; GPT-6 Sol high
  independent review and escalation. **OpenCode is paused. All Claude/Fable/Opus
  use is stopped.** The one Opus 5.5 advisory completed before the stop request.
  T027's old Fable assignment is superseded; preserve its review intent using the
  authorized Codex route or a documented pending gate, without calling Claude.
  Do not inspect or use the previously pasted credential or enable extra spend.
- C-M final wire and lineage sections are normative. Assessment is immutable
  comparison with anchored content digest, separate active-only counts and
  independent exact-current sign-off; it never promotes inventory. T009 receipt
  readback reauthorizes and reconciles raw historical outcome before projection;
  missing receipt is not proof that an in-flight operation cannot commit.
  T010 holds ambiguous operation identity across reload and does not resend an old
  payload under a new identity. Selection/detail IDs gate sign-off and export.
- C-L permits only `workflow.STATIC_POOL_ID` = `8821c420-18ea-4caa-9d97-83a331c0c002`,
  local/static IPv4. `purpose` remains descriptive. Reservation conversion requires
  explicit `reservation_id`, `service_reference`, strict positive
  `reservation_version`, matching owner/address/scope/pool and current reserved state
  at creation and approval. Keep historical unreserved payload hashes unchanged.
  Caller-owned `BEGIN IMMEDIATE` must cover eligibility, conversion, history,
  audit and exactly one pool/baseline bump; no capacity-history bump.
  Create replay reauthorizes current target ownership. Release proposals replay
  from their own unique requester/key row; only final decisions use the operation
  receipt action `reservation.release.decision`. Superseded allocation requests
  require current selected-domain authorization before payload or actor disclosure.
  Expiry never frees a hold. T016 owns future aging/notices/current occupancy.
- C-T future ticket handoff is simulated. Local approval and ticket outcome are
  independent. Unknown never means success; no ticket receipt grants network or
  provisioning authority. Preserve correlation/digest and three-attempt budget.
- Source/schema work is not migration or backup/restore evidence. T023/T024 still
  owe schema-6 state/config/package integration. No main merge of incomplete Tier A.
- Separate ledgers: workbook **36/21/8/46**; accepted repository **39/18/10/44**;
  meeting labels **92/0/12/7**, each denominator111. No row promotions in this phase.
  Historical native/Linux evidence retains its old exact candidate; the disposable
  VM was destroyed. New-candidate portability and human acceptance are unverified.
- Spencer has about eight total hours for T020/T022/T024/T026, outside core ownership.
  No human acknowledgement has been received. User review is Wednesday September23
  night or Thursday September24, America/Los_Angeles; exact duration/recipient/VM
  remain unassigned. Do not fabricate progress or provision infrastructure.
- Keep 20% reserve. Tier B/T029–T040 stays locked until T025 passes and reserve survives.
  The old oversight automation is paused/expired; do not resume or duplicate it.

## Copyable new-lead prompt

```text
You are Main Lead 5.0 for the IPAM post-meeting bridge. I authorize you to take over
from Main Lead 4.0, task 01a0cade-506f-7442-97da-0cc09b4f9929, at its completed T011
source milestone. Register your actual task ID as the persistent receiving lead.
Do not restart planning or repeat the model setup work.

Repository: /Users/yuganthareshsoni/Downloads/Ip_inventory.
Start by reading the complete handover at:
/Users/yuganthareshsoni/.codex/worktrees/ipam-main-lead-4/Ip_inventory/docs/handoffs/main-lead-5.0.md
It pins the final source assembly, accepted feature SHAs/PRs, worker IDs, limits and
next file leases. Refresh Git/task status before editing; preserve dirty work and
all existing workers. Main is still 04eba98cb8673406d1e5d38c5318fb963cc77ff7.
Application source is pinned at ab370a4273784bd750bf5f59289594a31d097739 on
codex/bridge-t011-handover; use its later pushed documentation publication as pickup.

Read AGENTS.md, DEVELOPMENT_RULES.md, current lead/status records, and the latest
specs/001-postmeeting-bridge contracts, task graph, first-wave registry, source
reviews and authorization-and-ownership record from that assembly. Latest dated
amendments control historical prose. Then continue T012 reservation API and T013
simulated ticket core from a pinned shared base, with explicit disjoint leases.

Use GPT-6 Luna for implementation and GPT-6 Sol for independent review/escalation;
Astra remains lead. OpenCode is paused and all Claude/Fable/Opus use is stopped.
Do not substitute routes, buy capacity, repeat setup or call Claude.

Keep this source-only until the already authorized bounded T025 disposable
synthetic acceptance gate has its prerequisites. No routine tests/build/runtime,
user-store mutation, main merge, deployment, customer access or new infrastructure.
Preserve the source/runtime/portable/human evidence distinctions and all three
111-row ledgers. Keep Spencer's human gates honest and Tier B locked.

Carry the authorized work forward autonomously, reuse existing owners for fixes,
and keep updates brief. Do not stop for routine approvals already covered here.
```
