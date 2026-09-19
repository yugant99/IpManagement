# Part 5: allocation, review and audit

Owner: core workflow agent, **not Spencer**. Original core: G21–G22. Current questionnaire priority includes the bounded G25 exception/notification/escalation queue (072/082), with actual cross-team handoff (081) conditional. G23 reclaim/remediation and G24 configurable lifecycle remain deferred. Branch: `codex/part-5-workflow`, with separate branches per feature.

## Win

Request one address from a designated synthetic IPv4 pool, approve or reject it, and inspect the persisted local allocation and decision trail.

## Inputs and owned work

Use Part 1's pool/allocation schema, actor mapping and shared database access. Own assigned workflow API/service/UI modules. Do not independently change schema or identity conventions.

Use one static IPv4 pool with an authoritative local ledger. Approval also consumes Part 2's current eligible contradictory observations, not saved findings or DHCP silence. Imports/reruns do not automatically increment pool or baseline versions. Read the workflow version/retry/error rules in `docs/IMPLEMENTATION_DECISIONS.md`.

## Fixed flow

Request records the exact candidate and reviewed pool/baseline version. Pending requests do not reserve inventory. On approval, the server checks actor permission and prohibits self-approval, then atomically rechecks eligibility and writes allocation plus successful audit. Repeated approval is safe. A changed baseline or occupied address fails visibly and requires renewed review; do not silently allocate a different address. Rejection leaves inventory unchanged.

Show downstream provisioning as simulated and distinct from the actual local allocation. Keep failures explicit and retain decision actor/time/reason/before-after. The presenter can switch between two labeled demo actors; this is not enterprise identity.

## Acceptance and limits

Persisted decisions survive restart; unauthorized/self approval fails; rejection and conflict do not leave partial allocations. A fixed state machine is sufficient. No live provisioning, SSO, configurable workflow designer, broad reclamation engine or customer process claim.

The additional queue stores finding reference, owner, acknowledgement/escalation and reason/history. These operational states never overwrite the rule's evidence state. Conditional 081 requires an actual recipient handoff and acknowledgement between named fictional teams; a team label is insufficient. Reuse the existing audit path. See `docs/QUESTIONNAIRE_SCOPE_DELTA.md`.

Handoff: transaction boundaries, role/actor contract, API examples, audit storage and unverified limits. Part 6 must preserve these records across startup/restart/backup; it must not know business logic to do so.
