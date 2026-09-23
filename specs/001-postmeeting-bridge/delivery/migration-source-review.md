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

## T010 UI source closure

Initial Luna candidate `d58ef6466b4e98fc1208cb8cd87632d759240eb3`, draft
[PR77](https://github.com/yugant99/IpManagement/pull/77), adds MigrationCompare and
changes only FirstPath.tsx, firstPathApi.ts and App.tsx alongside it. Independent Sol
review cross-checked the actual accepted T009 API at
`daede1905304c5d5bd363ff230b5f6371763eb49`. Wire/types, roles and independent
sign-off, separate counts/active-only/current versus historical labels, authenticated
request/download context and exact ambiguous-operation recovery were coherent in source.

Sol found one P2 selection race: changing the selected assessment briefly left the
previous ready detail actionable. Luna correction
`4b0b7d71bff38014539d1ff3c5a06c6c06631db2` synchronously clears detail for a
different selection and requires matching selected/detail IDs for rendering,
sign-off eligibility/submission and export. Same-row selection stays usable; exact
retry retains its original target. Sol closed the exact delta and the lead read it.

Main Lead accepts T010 source only. The resumed task is
`01a0cb5f-6dcf-7080-90ea-fffcc1743645`; its correction lease is now idle and retained
for assigned fixes. No build/typecheck/test/browser/runtime occurred. API/UI source
compatibility does not establish observed integrated behavior. The final handover
assembly must preserve both accepted heads; T025 remains the runtime gate.

## T010 correction during independent T025

The first committed-lock UI build of candidate `68e0b4ed466c66ce73926ddfec8a79ad94d7d1c8` failed: `MigrationAssessmentPage` extended `Page` without importing it, cascading into missing pagination members and implicit-any callbacks. Retained original Luna author task `01a0cb5f-6dcf-7080-90ea-fffcc1743645` corrected only the type import in `firstPathApi.ts` at **`220c4a25469961542f640418a0e5503c3f9d48e4`**. Independent Sol confirmed the exported shared type and consumers, and closed the source delta without running checks. PR101 integrated at **`996d0a8cadeb1d399eb780862055ccdc19211488`**.

Separate Luna verifier observed the full locked candidate2 `npm ci` and `npm run build` pass, with retained logs at the local T025 artifact root. The earlier failed build remains negative evidence; a separately emitted candidate1 Vite-only bundle was provisional and never establishes a passing full build. Complete business/UI/readiness/recovery T025 evidence is still pending. This correction and build result do not establish main, portable or human acceptance.
