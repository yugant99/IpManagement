# Current implementation-chat handoff

**ACTIVE — Stage 2: first complete path; synthetic-data generation in parallel**

Stage 1 source has completed lead review with no actionable findings. Its exact checkpoint is approved as a dependency for continued implementation; runtime acceptance and main integration remain pending. [Lead review](handoffs/stage-01-lead-review.md). The user has already started Stage 2; do not create another worker from the older draft prompt.

## Active owners

Use task IDs because sidebar titles have changed. All registered tasks use host `local`.

| Role | Current title | Task ID |
|---|---|---|
| Persistent project lead | Synthetic data builder | `01a0b845-6c8d-7021-a5c9-15e673db07c9` |
| Foundation fixes | Foundation 1 | `01a0b8ae-bd65-7331-b548-da5dca1e0d5e` |
| Stage 2 implementation | Implement Stage 2 first path | `01a0b8c2-f283-7cf1-9128-85e9164f5fe9` |
| Synthetic data | Overseer | `01a0b8b9-82fb-7a11-bc50-ec3a5b234729` |

## Exact dependency and scope

- Foundation: `codex/part-1-foundation` at **`c6131c38a460c13c3a189ee64a530042b2a2bf0f`**, [draft PR #5](https://github.com/yugant99/IpManagement/pull/5), unmerged at this update. Runtime source is at `ea51aa64b1780fa5c171e95ae59a619bf0109d52`; final commit adds report/draft handoff.
- Main remains documentation-only. The lead explicitly approved Stage 2 branching from this reviewed foundation in isolated `codex/part-2-first-path`. Do not start application work from main, switch another owner's checkout or silently substitute an unreviewed dependency.
- Stage 2 delivers **routing and intended-policy import → immutable raw references/typed records → one saved missing-expected-route result → API/browser evidence**. Healthy and insufficient-evidence controls accompany the anomalous case. DHCP imports and further rules are deferred from this first path.
- Proposed storage stays small: source batches, coverage, raw/typed records and saved calculation results. Explicit stopped-service CLI migration from recognized schema v1 to v2 uses the existing exclusive lock and one transaction. Startup must not silently migrate or replace unsupported data. Implementing the command does not authorize executing it.
- Intended policy applies only to existing scoped prefix IDs. Select the latest declared source/scope policy view; missing/invalid/future policy is unknown, and a newer partial snapshot cannot silently fall back to older per-prefix policy. Multiple competing authorities remain unknown until resolved.
- Missing-route conclusions require fresh complete applicable routing evidence. Keep severity/evidence state separate. Never read expected-outcome labels to choose results or silently promote imported richer inventory into the current ledger.
- The data worker owns `fixtures/` and data docs and supplies compatible first-path examples alongside the richer pack. Stage 2 owns assigned import/rule/API/UI modules and coordinated schema migration. Spencer retains Part 6. The lead owns global status and main integration.

## Evidence and next boundary

No package installation/build/type/tests/runtime/browser evidence exists. Those checks require explicit user request. `PART6_READY=no`; reset/backup/restore and compiled/runtime/persistence evidence remain absent. No VM/container/cloud/public deployment authority is added.

The [Stage 1 report](https://github.com/yugant99/IpManagement/blob/c6131c38a460c13c3a189ee64a530042b2a2bf0f/docs/handoffs/stage-01-report.md) and [original Stage 2 draft](https://github.com/yugant99/IpManagement/blob/c6131c38a460c13c3a189ee64a530042b2a2bf0f/docs/handoffs/stage-02-first-path.md) are on the foundation branch. This current pointer supersedes the draft's pending branch-coordination wording and broader DHCP-import scope.

Stage 2 reports **READY FOR PROJECT-LEAD REVIEW — Stage 2** with exact pushed SHA/PR, actual evidence/gaps and a draft Stage 3 prompt. The persistent lead reviews that checkpoint, then publishes **START A NEW IMPLEMENTATION CHAT — Stage 3** and its actual generated prompt. Do not invent a future Stage 3 checkpoint or start it automatically. Keep the previous worker available for assigned fixes.
