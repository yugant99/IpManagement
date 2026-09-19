# Lead review: synthetic data and Stage 2

Date: 2026-09-19. Persistent lead: `01a0b845-6c8d-7021-a5c9-15e673db07c9`.

## Decision

**Accepted as unmerged source checkpoints for Stage 3. Runtime acceptance remains pending.** Three bounded independent reviews found no actionable defects in the assigned surfaces. No application PR was merged. No tests, builds, runtime, browser, generator, parser-validation or infrastructure commands were run for this review. No source findings does not prove executable behavior.

| PR | Reviewed final pushed SHA | Relationship |
|---|---|---|
| [#7 synthetic data](https://github.com/yugant99/IpManagement/pull/7) | `907f6e7bf32f23f36d270da49c3177b015c8bfae` | Open, unmerged, based on main; data/generator checkpoint `60df87025a9a76187638bcad1921981b851f6cbb` |
| [#8 Stage 2](https://github.com/yugant99/IpManagement/pull/8) | `8a1a122737618748c58c5a8fc31b58a3b5f6f37e` | Draft, unmerged, based on foundation; code checkpoint `3c193c4ca320985e3dc258b39d8af1ec6632d155` |
| [#5 foundation](https://github.com/yugant99/IpManagement/pull/5) | `c6131c38a460c13c3a189ee64a530042b2a2bf0f` | Previously source-reviewed, draft/unmerged; [earlier review](stage-01-lead-review.md) |

These remote heads/base branches were read during this review. Main was documentation-only `1db87d6b45e4c58c77ebc54b829740c71dcadebd` before this publication. A later docs commit is not a newly reviewed application checkpoint.

## Independent review

| Reviewer / source scope | Finding | Limit |
|---|---|---|
| `questionnaire_analysis`: generator, selected envelopes, schema, independent expected manifest, first-path fixtures | Foundation identities retained; interval recipes and authored counts/p95/forecast expectations internally consistent; partial/stale/scope/replay controls preserve unknown; no expected-answer input path; first-path shapes align with PR #8 | Selected source/artifacts, not exhaustive generated-file or executed import validation |
| `grill_architecture`: imports, reconciliation, schema v2, store/migration, API transaction sites and fixture contracts | Latest accepted source/scope selection includes partial replacements; scope/half-open time matching, conservative completeness, replay identity, saved provenance and transaction boundaries match the contract | No SQL transaction, migration, import or rule executed |
| `coverage_20h`: upload/receipt, run/detail components, API paging/filter and migration wiring | Fatal UTF-8 decoding preserves submitted source text; first-path state survives view switches/refresh; evidence stays pinned to run/record IDs; failures retain prior run visibly; paging/filter parameters align | No rendered browser, network request or runtime evidence produced |

The lead reconciled the source and owner reports. No corrective changes were required; both existing owners received the decision. They retain responsibility for assigned fixes. No speculative refactor or new test pipeline is attached.

## What exists in source

PR #8 implements routing/policy import, immutable receipts/raw and typed evidence, explicit schema v1-to-v2 migration, saved **G13 missing-expected-route** results and API/browser wiring. G14 conflicts and DHCP/calculation breadth remain Stage 3 work.

PR #7 supplies a rich pack and a separate foundation-only first path. The latter uses the six-prefix seed: fresh North presence, complete Lab absence, partial/stale unknown controls and a later recovery. Authored baseline expectations are one healthy, one anomalous and four not-applicable results; they have **not** been observed from the application. Partial policy replacement must suppress unsupported conclusions rather than fall back to older per-prefix policy.

Rich inventory is not active merely because fixture files exist. Typed DHCP is outside Stage 2. Stage 3 must implement explicit safe fresh-store bootstrap and DHCP support. Changed intended-baseline imports cannot overwrite initialized state or approved allocations. Expected labels are comparison-only.

## Remaining evidence

| Area | Pending before the corresponding acceptance claim |
|---|---|
| Application/migration | Authorized install/build/startup and explicit supported migration, including preservation/failure behavior on the actual candidate |
| Imports/replay | Actual receipts/raw retention, scope isolation, identical replay and changed-payload rejection |
| Policy/time/unknown | Executed complete/partial/stale/ambiguous-source and boundary cases; latest partial replacement and visible unknown |
| Browser/saved results | Real import-to-run-to-detail path; old results pinned after later imports/reruns; raw evidence and overview/detail from one run |
| Rich scenarios | Fresh-store setup, typed DHCP, shared occupancy/p95/forecast and rule/control results compared with independent manifest |
| Portable state | Core reset/backup/restore, allocation/audit persistence, packaging and recipient startup evidence; `PART6_READY=no` |

This lists missing evidence, not permission to execute commands. No source-readiness claim or screenshot substitutes for required acceptance outcomes.

## Dependencies and next stage

Stage 3 may combine exact PR #8 and PR #7 on an isolated feature integration branch, preserving commits; PR #5 is inherited. Read current lead documents on main first because application branches have older global pointers. Application merges into main remain with the lead and require evidence.

Core state commands stay with task `01a0b8ae-bd65-7331-b548-da5dca1e0d5e`, packaging with Spencer and fixtures with the data owner. State-command PR #10 and delivery-method PR #9 arrived during review and remain **unreviewed/unaccepted/unmerged** by this lead. PR #9 also retains its user's no-merge restriction. Neither is part of this acceptance.

The [approved Stage 3 kickoff](stage-03-kickoff.md) supersedes the worker draft. This original task remains lead. Preserve the 111-row denominator; source acceptance creates no demonstrated-row credit. Separate implemented source, actual evidence, partial/documentary support and remaining gaps.
