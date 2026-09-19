# Stage 3 workflow lane

**READY FOR PROJECT-LEAD REVIEW — Stage 3. Source authored; runtime evidence pending.**

Owner: Stage 3 coordinator's `/root/workflow` subagent. This lane does not replace the persistent project lead. Checkout: `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-3-workflow`. Repository: `https://github.com/yugant99/IpManagement`.

Branch: `codex/stage-3-workflow`. Integration base: `5578431`. Pushed service checkpoint: `cdf52a20d2827f753926d2b18a60c635d64fab39`. Pushed code/UI checkpoint: `1d2af63c12da50f94d996f97b142d1a9d552845b`. This document is published in a later documentation commit; it does not claim its own future SHA. PR publication is reported in the lane's final handoff.

Only owned paths changed: `backend/ipam_demo/workflow.py`, `frontend/src/Workflow.tsx`, `frontend/src/workflowApi.ts`, and this file. Shared schema, store, routes, common UI/styles, global status, state commands, fixtures and Part 6 are outside this lane.

## Contributions and evidence limits

G21/G22 source contributions: RFP-001/004/005/009/053/054/059/060/078/080/084. G25 source contributions: RFP-072/082, plus conditional RFP-081's actual persisted fictional-team transfer/recipient acknowledgement path. These remain source contributions, not demonstrated or fully satisfied questionnaire rows. The denominator remains 111.

- Fixed actor mapping: Mira (`demo-requester`, requester, Access Planning) can request addresses and own exceptions. Rowan (`demo-approver`, approver, Network Operations) can also approve and edit inventory. Permission derives from the recognized identity, never a client-supplied role. Both cover the local demo scopes; no authentication or tenant-security claim.
- Only designated North static pool `8821c420-18ea-4caa-9d97-83a331c0c002` is allocatable. Its local/static/IPv4 authority, range/exclusion validity, exact candidate, scoped intended assignments, reviewed pool/baseline versions and current eligible DHCP positive claims are checked. Source silence remains an explicit limitation; static intended authority supplies the local decision basis.
- Creation stores normalized payload and hash under actor plus idempotency key. Same key/payload returns the existing request, changed payload conflicts. Pending requests do not reserve addresses. Superseding review links to the same actor's prior request.
- A separate permitted actor approves or rejects. Terminal decisions are immutable; the same normalized decision hash replays the stored result. Approval rechecks current evidence and exact stored versions, then inserts the exact allocation, increments pool/ledger versions, updates the request and writes success audit within the caller's single transaction. Rejection leaves intended inventory unchanged.
- Simulated provisioning success/failure is saved separately from the committed local allocation. A simulated failure does not erase the local result.
- Newly calculated anomalous rule/scope/family/subject combinations create one queue record and system audit event. Queue evidence references the first immutable finding/run. Owner acknowledgement/escalation never edits finding evidence. Queue mutations require the current owner and exception version; transfer names the other team's recipient and resets recipient acknowledgement. Recipient acknowledgement is separately stored and audited.
- The API-backed UI shows named actor switching, exact versions/candidate, request history, local/simulated outcomes, reasoned decisions, separate queue state/evidence, team transfer/recipient acknowledgement and paginated audit history. Ambiguous creation/decision responses retain exact retry payloads. No mock response supplies a successful screen.

Actually observed: current source/contracts and staged Git diffs were read; the two code commits were pushed successfully. No tests, check scripts, compilation/type checks, migration, seed/generator, app/server, browser, container or infrastructure commands were run. Behavior, persistence, rollback and browser rendering remain unverified. No portable readiness or final acceptance claim is made.

## Integration contract

Required unmerged dependencies are coordinated by the Stage 3 root:

1. Root schema/store migration at `f241b07` supplies `allocation_requests`, `audit_events`, `exceptions` (read as source and matched to this lane's fields).
2. Evidence lane's `9e9efc7` introduces `active_dhcp_claims(connection, scope_id, family, address, clock_text) -> {claims, unknown_reasons}`. Later evidence commits may supply implementation refinements; use the root's accepted dependency head. Positive claims come from latest fresh applicable source views even if incomplete/ambiguous; only contradictory positive claims block this locally authoritative flow.
3. Root owns API route wiring, `BEGIN IMMEDIATE`, rollback and post-rollback failure audit, plus common navigation/styles. Importing `Workflow` as a default component needs no props.

Service helpers do not begin or commit transactions:

- `actors()`, `require_actor(actor_id, permission=None)` and shared `audit_event(connection, *, actor_id, action, outcome, reason, request_id=None, subject_id=None, scope_id=None, pool_id=None, address=None, details=None)`.
- `workflow_status(connection)`; `create_request(connection, payload) -> (request, replay)`; `decide_request(connection, id, payload) -> (request, replay)`; `get_request(connection, id)`; `list_requests(connection)`; `list_audit(connection, request_id=None, subject_id=None)`.
- `sync_exceptions(connection, saved_run) -> new_count` must execute after inserting the saved run, within that transaction. `list_exceptions(connection)` and `update_exception(connection, id, payload)` expose queue operations.

Routes expected by the UI: `GET /api/workflow`, `GET/POST /api/allocation-requests`, `POST /api/allocation-requests/{id}/decision`, `GET /api/exceptions`, `POST /api/exceptions/{id}`, `GET /api/audit?subject_id=...`. Root additionally provides request detail and actor lookup. GET lists use the existing `Page` format with `limit`/`offset`; root handles pagination. POST allocation endpoints return the request object itself, not a wrapper around `(request,replay)`.

Create payload: `actor_id,idempotency_key,pool_id,candidate,pool_version,baseline_version,owner,purpose,reason`, optionally `supersedes_request_id`. Decision payload: `actor_id,action=approve|reject,reason,simulate_failure` (boolean; only approval may simulate failure). Queue payload: `actor_id,version,action=acknowledge|escalate|handoff,reason`, plus `recipient_actor_id` for handoff. Unknown fields are rejected. Errors use existing `AppError`.

Failed-attempt audit is root-owned because the operation must roll back first. A failed audit write must surface `audit_recorded=false` and a visible message/log; do not turn that loss into a success claim. Include attempted action, object, reviewed/current versions where available, safe reason and original error details. `audit_event` maps unknown attempted identities to an unknown role for failures; the internal `system` actor is only an audit provenance identity, never accepted by `require_actor`.

## Remaining limits and next owner

The queue does not auto-close resolved findings, re-notify recurrence of an existing stable subject, or modify prior evidence. It retains the first anomaly and operational history. UI notification counts explicitly cover the current queue page. It loads stored records when mounted/refreshed; no scheduler, websocket or external notification transport is implemented. Queue retry conflicts expose changed state rather than silently replaying an owner mutation. Request/decision retry safety is independent of queue state.

Read-only list operations load bounded-demo records before API pagination; no carrier-scale or concurrency evidence is claimed. The fixed actors, single pool and two fictional teams are deliberate scope limits. No reclaim/release/remediation engine, workflow designer, SSO, production granular permissions or external provisioning is implemented.

Next owner: Stage 3 coordinator for dependency integration and bounded source review; persistent project lead for global acceptance. Runtime evidence remains pending until explicitly authorized. Part 6 persistence acceptance needs actual allocation, audit and exception records across the authorized restart/backup/restore path, not this source report.

Draft follow-up prompt:

> Continue Stage 3 integration for `yugant99/IpManagement` on the coordinator's isolated `codex/stage-3-main-capabilities` branch. Review/integrate workflow commits `cdf52a20d2827f753926d2b18a60c635d64fab39` and `1d2af63c12da50f94d996f97b142d1a9d552845b` plus this lane handoff, preserving commits. Reconcile schema `f241b07`, the accepted evidence helper, root routes/transaction rollback audits and common UI navigation. Confirm by source review that root failure audits happen only after rollback and that local successful allocation/audit commit together. Retain unverified runtime/persistence/browser status, the 111-row denominator, reserved state/fixture/Part 6 ownership and the prohibition on tests/builds/runtime/infrastructure execution. Report the exact integrated source checkpoint and remaining evidence gates to the persistent project lead; do not declare global completion.
