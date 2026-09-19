# Synthetic data lane handoff

**READY FOR PROJECT-LEAD REVIEW — Synthetic data**

## Owner, checkout and published checkpoint

- Lane owner: data task `01a0b8b9-82fb-7a11-bc50-ec3a5b234729`, originally **Build IPAM synthetic data pack**. Sidebar titles changed during coordination; use this ID and branch to identify the owner.
- Persistent project lead: task `01a0b845-6c8d-7021-a5c9-15e673db07c9`, originally **Build synthetic inventory demo**. Acceptance, global status and merge authority remain with that lead.
- Stage 2 integration owner: task `01a0b8c2-f283-7cf1-9128-85e9164f5fe9`; first-path contract coordinated directly with the lead and worker.
- Existing checkout: `/Users/yuganthareshsoni/Downloads/Ip_inventory-synthetic-data`; branch `codex/part-2-synthetic-data`. It was clean at pickup; no newer user changes were present or overwritten. No worktree was recreated or other checkout switched.
- Integration base: `50a1dce9406ea8e9e52c032c321bb6ebfea063f8`.
- **Pushed generator/data checkpoint: `60df87025a9a76187638bcad1921981b851f6cbb`.** This handoff and independent oracle are in a subsequent documentation/comparison commit; use the PR's current head, preserving both implementation commits. The final worker response records that exact published head, avoiding a self-referential document SHA.
- Focused PR: [#7 — Add deterministic IPAM synthetic data and integration fixtures](https://github.com/yugant99/IpManagement/pull/7). This worker does not merge it.
- Owned/changed paths only: `fixtures/`, `docs/SYNTHETIC_DATA.md`, this handoff. No backend/frontend, locks, shared schema, packaging or global status changes.

## Read order and dependencies

Read `AGENTS.md`, `DEVELOPMENT_RULES.md`, `PROJECT_OVERSIGHT.md`, this handoff, [synthetic data notes](../SYNTHETIC_DATA.md), [fixture schema](../../fixtures/SCHEMA.md), [pack index](../../fixtures/v1/pack.json), and relevant `CONTRACTS.md` / `IMPLEMENTATION_DECISIONS.md` sections.

Seed/API shape is pinned to published Stage 1 **ea51aa64b1780fa5c171e95ae59a619bf0109d52**, branch `codex/part-1-foundation`: `docs/FOUNDATION_API.md` and `backend/ipam_demo/data/baseline.json`. Frozen baseline Git blob: `1fda9dbba4fb50ce93261f7417b18ff89720f43d`. The fixture branch does not merge/copy foundation application code. Later foundation/Stage 2 checkpoints must be coordinated by the lead; the existing seed contract, not a sibling checkout path, is the dependency.

`demo-v2-questionnaire` governs semantics. New observation/policy payload details are fixture-local `ipam-synthetic-v1`, documented and coordinated, not a silently changed shared application schema. Stage 2 accepted explicit `inventory_policy` source-kind mapping and per-scope snapshots. Policy, source selection, receipts, ingestion timestamps and richer inventory activation remain application integration work; source review is not execution proof.

## Implemented and observed

- Small Python standard-library generator; named outputs, fixed UUIDv5 recipe and clock, no network or dependencies. Generation raises read/write failures visibly; it is not transactional.
- Generated **four scopes, 60 prefixes, eight pools, 2,000 DHCP intervals and 200 routing observations** across 30 days, plus the original one intended allocation. The six original prefixes, two scopes, two pools and allocation retain all row values/UUIDs.
- **28 generated JSON files**: two rich inventory/policy files, eight observation batches, ten isolated opt-in variants, seven first-path files and index. The preserved baseline snapshot plus authored expected manifest make 30 committed JSON files.
- All six Pool Watch conditions, forecast/p95 controls, a concurrent assignment conflict, scope reuse, sequential renewals, missing metadata, static control, complete/partial/stale/invalid sources and replay cases. Values remain synthetic and review candidates do not prove safe reclamation.
- Independent expected manifest is not generated or read by the generator and is excluded from every input list. Scenario mapping and expected receipt/metric meanings are in `SYNTHETIC_DATA.md`.
- Foundation-only first path: six policy rows, two scope snapshots, one North route and complete-empty Lab view; separate Lab partial, stale, recovery and omitted-policy controls. No richer ledger bootstrap is needed for this recipe.
- Actual authorized command: `python3 fixtures/generate.py`, successful initially and again after first-path/policy additions. Final output reported `allocations=1`, `dhcp_lease_intervals=2000`, `pools=8`, `prefixes=60`, `routing_observations=200`, `scopes=4`, `generated_files=28`. Per-file byte/row counts and digests are in the index.
- Git source/status/staged-diff inspection, commits and pushes were performed for publication. Independent agent review used static source/contract reading only, with no material remaining discrepancy reported.

Questionnaire support: primary **RFP-033, 034, 036, 037, 061, 062, 063, 087, 089**; scenarios additionally support **002, 026–031, 035, 064–066, 071, 073–076, 095**. This lane supplies artifacts/documentation, not completed import, reconciliation, dashboard or acceptance evidence for those rows. Core goals G05–G08; future consumers G09–G14/G17.

## Unverified and remaining limits

- No tests, smoke checks, app builds, import calls, rule execution or infrastructure operations. No database created or modified. No live/customer input. No claim of app acceptance, saved metrics, detected findings or replay receipts.
- Metrics and receipt counts in the manifest are independent design expectations, not observed runtime results. No extra parser or regeneration-comparison check was run.
- Stage 1 only seeds its packaged baseline; rich seed-shaped JSON is not a supported custom-path CLI command. Changed intended inventory must stay staged and must not overwrite approved local allocations.
- Rich defaults and first-path feeds must remain separate recipes until multi-source precedence is explicitly defined. Latest per-source/scope selection must include newer partial batches; identical old-batch replay cannot restore a prior complete selection. First-path recovery supplies a new complete run identity.
- Policy omission/rejection means unknown, not implicit false or per-prefix fallback. Invalid raw values must remain traceable and required rejects make coverage incomplete. Expected labels must never select findings.
- No blocker to reviewing this artifact lane. Acceptance and merge remain pending project-lead review; application evidence remains with Stage 2 and later authorized checks.

## Draft next integration prompt

> Continue the lead-coordinated Stage 2 first path for `https://github.com/yugant99/IpManagement` in your existing isolated Stage 2 worktree. Read PR #7 and its current published head, preserving synthetic-data ownership. Generator/data checkpoint is `60df87025a9a76187638bcad1921981b851f6cbb`; foundation seed/API dependency is `ea51aa64b1780fa5c171e95ae59a619bf0109d52`. Use `fixtures/v1/pack.json.first_path` against the existing six-prefix foundation ledger. Implement/persist policy and observation import with explicit source/scope coverage, exclusive accepted/rejected/duplicate receipts, immutable raw provenance and identical-batch replay. Calculate only the agreed missing-expected-route path from independently imported data: North present, Lab absent, partial/stale unknown, fresh new-run recovery, omitted-policy unknown without fallback. Do not read expected-outcomes.json in application logic, alter fixture ownership, silently activate richer inventory or change global status. No tests, smoke checks, builds, runtime or infrastructure operations unless the user separately authorizes them. Report a bounded code/contract checkpoint and distinguish implementation from unverified behavior to the persistent project lead.
