# T011 reservation lifecycle source review

Main Lead 4.0 accepts source candidate
`3fcdb49d955c39cf08f0a0d6f9483384e43163b1` on `codex/bridge-t011-reservations`,
draft [PR78](https://github.com/yugant99/IpManagement/pull/78). Its frozen base is
`3add18986096e8fd9bc6ac509db28fc08b6bf2a6`, which includes accepted T009 and the
lead's explicit C-L conversion service/version clarification. Only
`backend/ipam_demo/lifecycle.py` and `backend/ipam_demo/workflow.py` changed.

Author: GPT-6 Luna high, task `01a0cca1-3873-79a0-ad54-e3f2ae0f25fb`, worktree
`/Users/yuganthareshsoni/.codex/worktrees/7802/Ip_inventory`.
Independent reviewer: GPT-6 Sol high, `/root/sol6_access_review`.
The lead also read the implementation and correction diffs.

## Findings and closure

Initial source `ace4fe0156fd496732f1b6c6adf6a419b9bc7c89` was followed by the
author's UUID service-argument compatibility correction
`5d5ea1be63444d57b5f7bbb519ca95e10d0b0836`. Independent Sol reviewed that exact
candidate and returned three actionable findings.

| Finding | Correction |
|---|---|
| P1: create replay disclosed saved reservation before current target ownership check | `ee3ec398bbf707f31148df34a96ee405c9c6e33e` authorizes submitted pool and receipt target reservation under the current selected domain before result/conflict disclosure, then confirms pool identity. It preserves historical replay after normal lifecycle progression without reapplying creation eligibility/version checks. |
| P2: release proposal used the final decision receipt namespace | The same correction removes proposal reads/writes of `reservation.release.decision`. Proposal replay uses existing unique requester/key plus payload digest in `reservation_release_requests`, reauthorizing the original reservation first. No schema change. |
| P2: supersedes lookup read prior payload before domain authorization | `3fcdb49d955c39cf08f0a0d6f9483384e43163b1` loads the raw prior row, authorizes its scope, then decodes payload and checks the requester. Foreign-domain predecessor links and distinguishing payload/actor errors are refused. |

Sol independently closed the bounded correction delta at the final SHA above,
with no residual blocker in that review. A changed saved policy_revision string
alone is not a blocker: current designated static/local IPv4 pool capabilities
are checked for each new transition. Historical replay still requires current
ownership; API integration must freshly authenticate and pin its write context.

## Accepted source boundary

Scoped reads, exact-address reservation, 24-hour default/168-hour maximum UTC
duration, versioned extension, independent unused release and matching allocation
conversion are implemented as caller-owned transaction functions. Strict positive
versions and explicit owner/service/address/scope/pool matching apply. Ordinary
unreserved normalized payload/hash shape remains unchanged. Cross-table eligibility,
conditional conversion/release, history and audit share the caller's immediate
transaction. Hold transitions increment pool/baseline once and never change
capacity_history_version. Proposal/rejection/replay do not change occupancy.
Expiry does not release a hold. No network/external provisioning write exists.

T012 still owes strict API DTOs, trusted context/role integration, current transaction
authentication, error/audit and receipt recovery boundaries. T013 owes simulated
ticket core. T015/T016 owe UI, aging/notices and current occupancy reporting.
No API route is implied by a callable lifecycle service function.

No tests, builds, typechecks, application imports, database/seed/migration operations,
services, browser runs or runtime observations were performed. No full Tier A,
portability, human acknowledgement, ledger promotion or main merge is claimed.
T025 remains the bounded independent runtime gate after its prerequisites.

## User-requested lead transition

Application source assembly `ab370a4273784bd750bf5f59289594a31d097739` on
`codex/bridge-t011-handover` combines accepted T011, T010 and their prerequisites
without conflict or application edits during assembly. Later publication adds
handover documents. T012/T013 are deliberately undispatched. The user starts the
new lead using [the complete pickup and prompt](../../../docs/handoffs/main-lead-5.0.md).
