# FABLE-DESIGN — actual advice and lead adjudication

Date2026-09-22. Actual model claude-fable-5-1, high, through existing Claude Code Max.
One bounded tool-less invocation completed without error. Reviewed dispatch snapshot
5c061b2391b739141eec561c0e7037b89ffa28ce, source base6b66f943b7c7783285bfd1f70859ede42380bf60.
No repository tools, runtime tests or external research were available to Fable. Model
list-price telemetry is not proof of additional billing. No credentials/account identifiers
are retained here. This completes FABLE-DESIGN only, not T027 or application acceptance.

## Lead adjudication

| Finding | Disposition |
|---|---|
| Ticket reassignment lacks identity/lineage rules | Accepted; C-T and data-model keep immutable business digest/correlation, versioned assignment, zero-attempt-only reassign and pinned attempt route/scenario. T003/T013/T014 carry it. |
| Static authority source missing | Resolved by source citation: existing workflow.STATIC_POOL_ID and _pool already enforce the single IPv4 local static pool. No new configurable pool list. |
| Readiness/configuration drift ambiguous | Accepted with bounded correction: C-A lists six protected booleans, Operator/domain permission and sanitized reasons. C-O preserves history; old revision mismatch alone does not fail readiness. Changed config recovery is labeled with normal stale/reauthorization rules. T023 carries it. |
| Main Lead3 in original spec | Existing T001/transfer already superseded it; direct current-authority banner added to spec.md so isolated readers see the transfer. Original historical header retained. |
| Advisory budget labeling | Resource plan now separates FABLE-DESIGN from final T027; no early completion claim. |
| Baseline granularity | Existing global app_meta version retained and conservative cross-domain staleness explained without disclosing foreign data. |
| Refused envelope evidence | Truthful boundary recorded: no receipt/rows; visible request/error and success-only import audit today. No invented durable refusal receipt/audit. |

Independent source adviser /root/spec_review checked actual readiness/import/baseline
source; Terra checked the schema/route representation. These are source decisions, not
Fable follow-up approval or runtime proof. The user later requested user-run prompts for
substantial further Fable advice; no automatic repeated review is authorized.

## Original advisory response

Reviewing the packet at 5c061b2 with spec base 6b66f94, design only, no tools run.

**Overall:** the package is coherent on the settled architecture. I find four design blockers, all correctable with small text additions and none requiring a rebase of the prepared worktrees. Everything runtime-related remains unproven by design and is listed separately.

## Blocking design findings

1. **Ticket route reassignment contradicts intent uniqueness.** `contracts/ticketing.md` "Proposed interface and payload" says a route change is "explicit reassignment", but the Intent record in `data-model.md` "Ticket intent, attempt and simulator effect" has unique domain+request+action, a single route revision/team, and no reassignment or supersedes field. A routing_blocked intent therefore has no legal path back to pending after a configuration fix. A second intent violates uniqueness, and mutating the stored route may change the payload digest and trip the 409 rule. Minimal correction: add a versioned route assignment to Intent with route revision, team, assigner and UTC, exclude route/team from the payload digest, allow reassignment only from routing_blocked or pending with zero attempts, and bind each Attempt to the route version it ran under. Add that case to T013/T014 acceptance.

2. **Designated local static pool has no authority source.** `contracts/lifecycle.md` and the Reservation section of `data-model.md` restrict holds to "the designated locally authoritative static pool", but the reviewed configuration record lists mappings, routes, connector mode and policy version only. Nothing names which pool is designated, so T011/T012 refusal of "unsupported pool" has no defined input. Minimal correction: either cite the existing pool attribute that carries local authority, or add a per-domain designated static pool list to the configuration record in `data-model.md` and reference it from C-L. T025 should then observe refusal on a non-designated pool.

3. **Recovery readiness under configuration drift is undefined.** The spec requires "all readiness booleans plus business-state validation", `contracts/operator.md` Day 3 excludes config and tokens from the snapshot, and persisted assessments, reservations and intents all carry configuration, policy or route revisions. No document enumerates the readiness booleans or states what happens when the restored state references a revision the live configuration does not match. Minimal correction: enumerate the booleans for the proposed readiness route in `contracts/access.md`, include a configuration-revision compatibility check, and state in the Day 3 pack that a restore under a different revision is recorded as a governing revision change with its normal staling effects, not a like-for-like recovery. Add this to T023's completion criterion.

4. **Adopted base still names Main Lead 3.0 as accepting authority.** The header and "Assumptions and authority" of `spec.md` say adoption is pending with Main Lead 3.0 and that 3.0 alone coordinates acceptance, while the manifest and spec review record adoption by Main Lead 4.0. Read alone, the locked base shows no authority for the current lead. Minimal correction: record the supersession, the exact base SHA and the reason the header is left stale in T001's authorization file. Do not rebase the worktrees for this.

## Advisory

- **FABLE-DESIGN labeling.** `resource-plan.md` budgets "two Fable passes" under T027 and calls dispatch-time work "T027-design", while tasks.md says the design pass does not complete T027. Rename the resource-plan row to avoid a later T027-completed claim.
- **Attempt record should persist the chosen synthetic scenario.** C-T lets the operator select the outcome scenario, but the Attempt fields list only result and reason. Without the scenario retained, scripted outcomes can be misread as observed behavior in T025 evidence.
- **Readiness route bundle unclassified.** Access.md lists the readiness route but assigns no bundle. Operator.md gives Spencer a "domain credential for readiness". T005 completion requires classifying it.
- **Baseline staleness granularity.** Any hold change bumps pool/baseline versions, and candidate identity pins the active baseline. Concurrent US2 work will stale pending US1 sign-offs. State whether the pinned baseline is scope-level or domain-level so T025 can sequence.
- **Rejected envelopes and SC-004.** Whole-envelope rejection happens before any receipt, so refused inputs leave no persisted record. State whether the refusal is audited or only returned.
- **Critical path.** Every Tier A code task other than DeepSeek's routes through Terra, and T003 gates all of them. While the route is held, only T001, T002 and documentation can move. The Sol fallback decision is the schedule-determining item, and the plan's own arithmetic already rules out three eight-hour days.

## Missing evidence, not design findings

- Whether the reused intended-inventory staging path writes only source records and never active inventory. US1's core invariant depends on it. Confirm at T007/T008.
- The source line citations in `delivery/spec-review.md` and the "no drift" main SHA claim in the manifest are unverified here.
- All access, replay, concurrency, unknown-readback, aging and stopped-recovery behavior remains T025 runtime evidence. This advisory does not complete T027 and carries no acceptance authority.
