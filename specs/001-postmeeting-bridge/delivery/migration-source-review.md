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
