# T008 migration assessment source review

Main Lead 4.0 accepts source candidate `776f32a3eaff2be9a5bd9d09a8f5dab62e4f5509`
on `codex/bridge-t008-assessment`, based on access publication
`833c2c8676b205c97476ab71f4e3b2cff0a2c608`. Draft
[PR75](https://github.com/yugant99/IpManagement/pull/75) retains the three coherent
commits. Only `backend/ipam_demo/migration_compare.py` changed. No main merge.

Author: GPT-6 Luna high, task `01a0cb4a-4b2c-7451-b2dc-8ae0508a8448`.
Independent reviewer: GPT-6 Sol high, `/root/sol6_access_review`.
Lead also read the implementation and correction diff against actual producer,
access, transaction and schema contracts. The earlier one-shot Opus 5.5 advisory
in [opus-assessment-advisory.md](opus-assessment-advisory.md) concerns the lineage
design; it is neither this implementation review nor acceptance authority.

## Findings and closure

Initial implementation `b873f83574dde20009334440a295f14db7095e7f` had five blockers.
Correction `c7b8bfe7190974221f42e3baff4b1e1b9225cb49` addressed the first two;
`776f32a3eaff2be9a5bd9d09a8f5dab62e4f5509` addressed the remaining three.
Sol's bounded final review closed all five at that exact final SHA.

| Finding | Source correction |
|---|---|
| Normal staged pool has no family field | Derive matching-key family from its validated same-scope candidate prefix; exclude the derived field from pool content equality. Preserve original candidate JSON. |
| Sign-off rejected every tagged SHA-256 digest | Validate exactly `sha256:` plus 64 lowercase hexadecimal characters, length 71. |
| Snapshot exposed origins quarantined by ordinary inventory reads | Classify every active prefix/pool/allocation by the existing local allowlist or current reviewed source/scope/domain mapping. Refuse generically before assessment writes or output if any origin is unclassifiable. |
| Malformed foreign receipt exposed an error distinction | Establish envelope source identity and selected-domain scope/mapping ownership before parsing the receipt and records. Foreign/unclassifiable batches return the same 404. |
| Exact create replay conflicted after configuration rotation | Hash stable request content; reauthorize with current context and target, preserve historical outcome and derive current staleness separately. |

The source retains immutable source/comparison rows, separate active-only accounting,
anchored versioned content digest, independently signed exact-current assessment,
and no candidate promotion or active inventory writes. Source acceptance releases
T009 API and T010 UI against a frozen shared wire contract. It does not establish
their implementation or assembled behavior.

No application tests, builds, imports, database, seed, migration, service, browser,
VM or customer execution was performed. T025 runtime, portable/human gates and all
three questionnaire ledgers remain unchanged. Tier B remains held.

## T009 API review — corrections pending

Luna task `01a0cb5e-f055-7751-b79c-a60c9662a0c5` published initial API candidate
`5a0fcf82112e0c7ae3a161fa11f70921c16f4096` in draft
[PR76](https://github.com/yugant99/IpManagement/pull/76), based on shared
`36dbfb90f3178c07ed9c7d0a55b54370a563bf7f`. Only app.py and models.py changed.
The lead's early uncommitted-diff finding about an unbound request in receipt
projection was corrected before this candidate by passing the trusted principal.

Independent Sol reviewed that exact published candidate against the frozen wire.
Routing/order, strict mutation fields, current transaction authentication,
selected-domain paging/detail/export, principal-scoped receipt lookup and mutation
DTOs were coherent in source. One P2 correction remains: sign-off receipt shape and
target validation must also reconcile its digest, signer, time and signed version
with the authorized saved assessment. Valid-shaped corruption must fail with the
generic integrity error rather than appear as a different historical sign-off.
Current read-time staleness stays separate from the historical outcome. The original
API author owns this two-file correction; T009 acceptance and T011 release remain held.

T010 UI remains in implementation. No application execution, UI/build check or runtime
acceptance occurred during either review.

### T009 source closure

Luna correction `daede1905304c5d5bd363ff230b5f6371763eb49` keeps raw receipt
identities until the target is reauthorized and its saved assessment is loaded.
It compares target ID and anchored digest, and for sign-off also signed state,
raw signer, signed_at and signed version. Initial/replay responses and key-only
readback all use that reconciliation before identity projection. Well-shaped but
inconsistent receipts return the generic integrity error; current staleness remains
separate from historical success. Sol independently closed the bounded delta at
that exact SHA, and the lead read it as well.

Main Lead accepts T009 as source-only. Draft PR76 remains unmerged, application
execution unverified. This releases T011 against T009 plus the lead's explicit
reservation service/version clarification in contracts/lifecycle.md. T010 and
the final assembled migration UI/API review are still pending.
