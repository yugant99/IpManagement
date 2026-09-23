# Main merge rule

Made explicit at the user's request on 2026-09-22. Main is the validated technical
baseline. A completed worker task, pushed branch, source review or lead handover
does not by itself satisfy the main merge gate.

## General rule

The lead merges a coherent feature once its dependencies are included, independent
review has no unresolved blocking findings, and the required correctness and
integration evidence exists for the candidate being merged. Documentation-only
changes need bounded source review, not application tests. Preserve feature commits
with a normal merge; do not merge the same dependency history separately afterward.

Commit count controls push frequency only. It never controls merge readiness.
Tests/builds/runtime still require their existing scoped authorization; this rule
does not authorize additional execution, infrastructure or deployment.

## Current post-meeting bridge: merge at T028

The bridge changes schema, access, workflow, API and UI together. Its first main
merge is the complete technical Tier A candidate, after the following gates:

1. **Technical scope complete and assembled.** Required feature, recovery and
   operator/package dependencies are implemented, source reviewed and included in
   one pinned candidate. T025 prerequisites are T018, T019, T021, T022, T023 and
   T024, including their transitive dependencies. Optional Tier B is not required.
2. **T025 independently passes.** Retain the exact candidate, configuration/schema,
   disposable synthetic target and actual outcomes for the authorized Tier A
   success, denial, stale/replay, concurrency, unknown, aging and stopped-recovery
   cases. Missing or failed required technical evidence blocks this merge. Source
   inspection alone does not satisfy this gate. After a relevant fix, refresh only
   the affected evidence and review before accepting the new exact candidate.
3. **Blocking reviews closed.** Required independent source reviews and the final
   candidate/evidence review have no unresolved blocking findings. Use GPT-6 Sol
   for the T027 final review intent under the user's current routing. Record the
   replacement explicitly; do not call or mark Claude/Fable as completed. Earlier
   design advice is not the final implementation review.
4. **T028 records technical acceptance and gate dispositions.** Record exact SHA,
   PR, evidence pointers, remaining nonclaims and the T026/T027/business dispositions
   in the lead acceptance record. T026 may truthfully record human rehearsal as
   pending when unavailable or unauthorized, as its existing contract permits.
   That limits acceptance to the technical package; actual human acknowledgement
   remains mandatory for a completed human-handoff claim. Documentary commercial
   gaps stay visible and do not become invented technical capabilities.
5. **Lead performs the merge at that checkpoint.** Refresh main and PR head, resolve
   any dependency/conflict drift, and retain appropriate affected review/evidence.
   When the gates above pass, take the PR out of draft and merge through the PR,
   preserving history. Record the resulting main SHA, update status/handoff and
   reconcile included dependency PRs. Do not leave a qualifying candidate waiting
   for another chat, arbitrary date or unrelated optional work.

Merge is not deployment, production/customer acceptance, universal portability,
human training or automatic questionnaire promotion. Those claims retain their
own authority and evidence requirements. A genuinely missing permission or failed
gate must be named with its owner and next action; it must not be silently waived.

## Historical T011 hold — superseded by completed T028

T028 subsequently completed through PR98 at
`78ebf156778085b616b0068196f4f28a8661b360`; see the [lead adjudication](../specs/001-postmeeting-bridge/delivery/lead-adjudication.md).
The following records why the earlier T011 source-only checkpoint was held.

At that checkpoint, main was `04eba98cb8673406d1e5d38c5318fb963cc77ff7`; draft PR79 contained the bridge
source checkpoint. T002–T011 and T019 have recorded documentary/source acceptance.
T012 onward still includes required reservation API, simulated ticket workflow,
UI/aging, state recovery and package work; T025 has not run. Consequently gates
1 and 2 are still open. This is an explicit technical hold, not a waiting period
for a human rehearsal or new lead.

The user requested a lead transfer after T011. This policy update does not dispatch
T012/T013, run application checks or merge the current incomplete bridge. The
receiving lead continues from [the handover](handoffs/main-lead-5.0.md) and owns
the T028 merge once the gates pass.
