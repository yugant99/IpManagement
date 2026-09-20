# Part 5: allocation, review and audit

Owner: core workflow agent, **not Spencer**. Original core: G21–G22. Current scope includes the bounded G25 exception/notification/escalation queue (072/082), actual fixed-team handoff (081), and the user-authorized F1 missing-prefix registration slice of G23. Reclamation, external remediation and G24 configurable lifecycle remain deferred. Follow the [audit-response contract](../AUDIT_RESPONSE_CONTRACT.md) and [current acceptance](../STATUS.md); the historical G23 label is not a blanket exclusion of this new local correction. Use separate branches per feature.

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

The queue retains original evidence, latest evidence, ownership, acknowledgement/escalation and audit. Healthy comparable evidence can resolve a finding; the owner separately closes or reopens the case. Missing/unknown/incomparable evidence never resolves it. Recurrence after healthy evidence or a new material discrepancy renews a notice; unchanged generated IDs do not. Fixed-team handoff includes recipient acknowledgement, not merely a team label. See the F5 contract for stable identity and exact retry/version rules.

The F1 correction path proposes one concrete missing top-level prefix inside an existing managed perimeter. A different authorized actor approves or rejects against current scope, overlap and reviewed versions. Approval atomically registers intended inventory with decision/audit; pending and rejected requests leave inventory unchanged. Subsequent reconciliation evaluates actual evidence. Original, first linked and latest results remain separate, and every current ghost member must be accounted for before calling its perimeter healthy. New prefixes without route policy remain unknown. Allocation approval and simulated external provisioning keep their existing semantics.

Handoff: transaction boundaries, role/actor contract, API examples, audit storage and unverified limits. Part 6 must preserve these records across startup/restart/backup; it must not know business logic to do so.
