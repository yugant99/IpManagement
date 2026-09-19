# Stage 3 independent source review

Persistent lead: `01a0b845-6c8d-7021-a5c9-15e673db07c9`. Date: 2026-09-19.

## Review boundary

Initial candidate: [PR #18](https://github.com/yugant99/IpManagement/pull/18), `codex/stage-3-main-capabilities`, **`c2629fbf6516a744e65c52a424700563c0f4a0a2`**. Integrated code before that report: `32d751fac381aef8bd53dcfdaa1f27639a64dc07`. Application base: PR #8 `8a1a122737618748c58c5a8fc31b58a3b5f6f37e`.

Three independent bounded source reviews covered evidence/calculation/rules; inventory/allocation/exception commands; and frontend/API/export wiring. The lead separately inspected app transactions/audits, schema/migrations/store, reports, packaging metadata and the combined CLI. This was not an exhaustive audit and produced no runtime evidence.

## Findings routed to the existing owner

| Finding at initial candidate | Consequence | Source correction |
|---|---|---|
| P2, confidence 9/10: `App.tsx:317–320` mounts Workflow only while bootstrap is ready; refresh changes it to loading | Unmount loses unresolved create/decision idempotency keys and payloads; a later submission can become a new request | Fixed at `7acb30ed5bece193af58c4f5adde88769d4ed2a0`: retained readiness scopes keep Workflow mounted while hidden; independently closed in source |
| P2, confidence 8/10: `CapacityReports.tsx:127` displays cached preset identity but `reports.py:109–115` exports current mutable singleton | Another tab can replace the preset, making CSV differ from the displayed pinned evidence | Fixed at `fb63241c9066f64625f75cf9100a9bd1db8e9eea`: displayed content revision is checked in one read transaction, mismatch returns 409, UI verifies response and offers reload/review; independently closed in source |
| P2, confidence 9/10: `rules.py:63–66` and `calculations.py:79–91` skip static-pool DHCP claims | A fresh lease at North static `10.40.2.3` escapes discrepancy reporting, contrary to GRILL_75 Q13 | Fixed at `9cfb93a29030a68f8625e5cfd154fa2ae669f336`, integrated at `009e80197ab610e5a365d1e3dd4462588754d646`: static positive discrepancies separated from disabled DHCP capacity/inactivity; independently closed in source |

Inventory/workflow source review found no additional actionable findings. The earlier `098b1e8` corrections are present: current exhaustion takes precedence over invalid history, and inactivity includes excluded/out-of-range prefix leases. The lead routed all new fixes to task `01a0b8f0-7036-74d1-81c1-e388d17b4cf4`; it did not make competing application edits.

**Accepted Stage 3 source checkpoint: `009e80197ab610e5a365d1e3dd4462588754d646`.** All three corrections were independently reread at this exact candidate; the lead read the full correction diff and confirmed the pushed PR head. No residual actionable finding remained in these bounded surfaces. A later report-only publication may follow; it cannot silently substitute additional application changes. This acceptance permits the separate Stage 4 source lane; it does not accept runtime behavior or merge application code into main.

Final PR #18 publication is **`63287e0ff281b678abbd8809ca9160739de8c537`**. The lead read its two-document-only delta over accepted code; it records the fixes, actual component PR state and new scheduling scope. This is the Stage 4 pickup head; the accepted application code remains `009e801`.

## Actual integration state

GitHub records component PRs #12, #13, #14, #16 and #17 **merged into the Stage 3 feature branch**, following normal history-preserving Git merges. They are not open dependencies. The earlier lead statement that they would remain open was incorrect. Application code is still outside main; PR #18 is open/draft against Stage 2.

Exact inherited checkpoints: foundation #5 `c6131c38a460c13c3a189ee64a530042b2a2bf0f`; Stage 2 #8 `8a1a122737618748c58c5a8fc31b58a3b5f6f37e`; data #7 `907f6e7bf32f23f36d270da49c3177b015c8bfae`; inventory #13 `95a4efbc445adabf649df6439108a12d1232e4ff`; workflow #14 `b14f8ebd70b278fe35b3a18482802a657ea87950`; evidence #17 `170718dd931503c95e0f172b4ec9978250f55107`; state compatibility #16 `e6029d855abf13581b95fda20ade52f5a6c5792e`; rich CLI #12 `d7b1fd580b88f875883dbde975c9504ead58a6a9`. PR #16 inherits original #10 `0e139a85b445f7d07968c855e770c525c5e4d91c`; do not integrate the original v1/current-only selector over the correction.

PRs #5/#7/#8/#10 remain open in GitHub, despite being inherited by the Stage 3 source candidate. None is merged into main. PR #9 delivery method at `c3e45fa43a1e9f59e6c9af298b14e2c0857ebaa2` is separate, review pending, with the user's no-merge restriction. Spencer's published package checkpoint is not yet registered. These are explicit missing dependencies/evidence, not implied completion.

## Remaining evidence and scope

No tests, smoke/type/parser/compile/import checks, builds, generators, dependency installation, app/API/browser/state/migration/container/VM or infrastructure commands were executed by this review. No application PR was merged by the lead. Source acceptance cannot establish readiness, database preservation or a demonstrated questionnaire row.

Required later evidence, when authorized:

1. Fresh baseline/rich setup, initialized-state refusal and recognized legacy migration preservation.
2. Real receipts for accepted/replay/partial/stale/conflicting authority cases, saved run identity and independent expected-fixture comparison of scoped rules, p95 and forecast.
3. Actual inventory/IPv6 edits; allocation stale-version/self-approval/ambiguous retry/rollback/failure audit; exception/team acknowledgement records.
4. Browser/detail/export agreement, including all three review corrections, compiled UI and readiness.
5. Core backup/restore/reset/restart preserving populated allocations, audit, queue, presets and IDs; invalid/foreign/unsupported refusal and failure outcomes.
6. Spencer's packaged startup, persistent data and recipient handoff on the stated target. Evolving-feed assets and scheduler restart/cycle evidence will be additional gates once implemented.

The denominator stays **111** and demonstrated/substantiated rows remain **0 at this lead checkpoint**. RFP-081 has unobserved source wiring; RFP-043's general import callback remains deferred. The user has now required RFP-068 evolving scheduled acquisition: [SCHEDULING_CONTRACT.md](../SCHEDULING_CONTRACT.md) supersedes its Stage 3 deferral and is separate new work, not evidence that Stage 3 contains a scheduler. Static fixtures remain unchanged. `PART6_READY=no` and runtime acceptance remains pending.
