# Bounded easy-win follow-up

Authorized by the user on 2026-09-20 through **Review Fable easy-win proposals** (`01a0c0e1-aaa0-7152-bfa9-a93c0baa3b43`) and delegated to registered Main Lead 3.0. The instruction is to finish the bounded additions and focused evidence first; VM work is deferred. Starting main is `852010a311065a9cc0258fc4e3f5c1c1a889329a`. This is a follow-up, not a new Stage 6/7 or replacement of accepted evidence.

Focused local implementation, necessary local builds/checks and fresh disposable localhost/browser/API evidence are authorized for the rows below. No broad application E2E rerun, VM planning/checks, Docker commands/image pulls, cloud provisioning/spending, deployment/TLS or hot-snapshot work. Preserve prior acceptance stores, compiled candidates and private artifacts. Record exact source identity for new evidence; past observations remain valid for their original candidate. Do not silently promote questionnaire rows.

## Visible workers and ownership

Every dispatched worker is an app-visible **GPT-5.6 Luna / medium** task with an isolated project worktree. No hidden subagents or additional worker creation is authorized by this record. Main Lead 3.0 owns shared contracts, global status, accounting, review and merges.

| Task | Exact task ID | Owned production files and scope |
|---|---|---|
| Easy wins — import workflow and request… | `01a0c0f0-5735-7e52-9f5a-ec45ac8ac99c` | Sole `backend/ipam_demo/app.py` editor/integrator; minimal scheduler request-correlation change; import callback helper if required. RFP-043/005 and sibling endpoint wiring |
| Easy wins — report family and executive… | `01a0c0f0-c49e-77d2-9e11-f82c516d33b0` | `backend/ipam_demo/reports.py`, `frontend/src/CapacityReports.tsx`. RFP-035/077 |
| Easy wins — domain filters and source… | `01a0c0f1-2f5e-7d73-9858-e275011a362e` | `inventory.py`, small source catalog helper; `App.tsx`, `FirstPath.tsx`, `firstPathApi.ts`, `api.ts`, small catalog component. RFP-026/036 and agreed RFP-043 import UI |
| Easy wins — focused export and normalization… | `01a0c0f1-9dee-7472-ab8b-1ed149354d17` | Evidence only for RFP-006/078/033; no product edits |

Each task owns its correspondingly named `tests/test_easy_wins_*.py`, `docs/handoffs/easy-wins-*.md` and `docs/evidence/easy-wins/<lane>/` only as assigned. The evidence-only lane may supply `scripts/evidence/easy_wins_existing.py`. No uncoordinated schema/lock/dependency changes, shared stylesheet edits or global-document writes. Workers publish route contracts to the sole app owner, preserving normal feature commits when composing the candidate. Commits/pushes and PR/lead-review rules remain in force.

## Report and inventory contract

- RFP-006 evidence: persist meaningful nonempty filters and an ordered non-default column subset; compare exported CSV with its selected saved run and saved preset revision. No custom dashboard-design claim.
- RFP-078 evidence: compare actual audit CSV with audit list, including a real supported failed attempt. No compliance certification or all-system audit claim.
- RFP-033 evidence: supported valid IPv6 textual and timezone timestamp forms become canonical typed values while raw/envelope evidence remains retained. No arbitrary cleansing or heterogeneous live integrations.
- RFP-035: `family` report filter is absent/empty or string `4`/`6`; validate other values visibly and compare numeric saved subject family consistently. Apply through preset, CSV, direct saved-run JSON export and findings API. Preserve existing preset payload/revision when reading older presets. Findings/counts use one matcher; calculations filter by scope/family. Rule/severity/evidence filters govern findings, not a fabricated pool-calculation filter. Preserve explicitly labeled full-run overview totals and the actual JSON-versus-CSV formats.
- RFP-026: optional exact, case-insensitive `domain` and `region` filters derive from scope metadata and combine with prefix/pool filters before pagination/counts. UI choices use existing scopes. Preserve IP parent/child containment results. These labels are not domain orchestration or tenant security.
- RFP-077: selected-saved-run summary answers what needs attention, where evidence is insufficient, which scopes are affected and which pools show pressure. Metrics are filtered anomalous findings, filtered unknown findings, distinct scopes having either, and distinct anomalous `pool_pressure` subjects. Reuse the saved rule result; an unavailable metric is not pressure. Show run ID, saved timestamp and scenario clock. No latest-exception merge, invented financial/business KPI or customer executive acceptance claim.

## Imported-source catalog

RFP-036 supplies an **Imported-source catalog**, not automatic system discovery. Use the current `app_meta.demo_clock_at`, with explicit `evaluated_at`; no user-configurable historical as-of feature. Row grain is source/scope, selected by existing latest-ingestion semantics without falling back to an older complete batch. Distinct competing sources remain visible; declared source authority is not verified unique authority.

Reuse existing DHCP/routing eligibility windows and selected-view helpers. Display freshness/eligibility separately from declared/effective completeness and row rejection. Do not invent a freshness threshold for policy or staged inventory; make staged/non-active and not-applicable semantics explicit. Link source, batch and source-run identities to immutable receipt/envelope/record evidence. Imports rejected before receipt persistence are not cataloged failures. Scope filters and pagination totals use the same row set. The app owner wires `/api/source-catalog` from the catalog worker's final agreed return shape.

## Opt-in import reconciliation

RFP-043 adds `POST /api/imports?reconcile_after_import=true`, default false. The default receipt/status/header behavior stays compatible. Commit import first. The opt-in response adds a separate `reconciliation` result with batch identity and `succeeded`, `busy`, `failed` or `skipped`; a callback failure cannot disguise a committed import as failed. HTTP 201/200 and `X-Import-Replay` continue to describe import commitment/replay, separately from reconciliation replay.

Committed complete/partial observed/policy receipts are eligible, including valid zero-record coverage and all-row-rejected partial evidence. An invalid envelope with no committed receipt never triggers a callback. Staged intended inventory returns `skipped` / `STAGED_INVENTORY` with a reason: no intended baseline promotion or misleading unchanged run.

The callback holds the existing shared run lock and immediate transaction, invoking existing reconciliation and exception sync. Recheck an existing successful batch-to-run link inside that guard/transaction before creating a run. Reuse `audit_events`: one successful `source.import.reconcile` event, subject batch ID, with batch/run/trigger and `http_request_id`, commits atomically with the run. Preserve immutable receipt JSON. Successful replay returns the linked saved run without duplication; validate the link target. If no successful link exists, a later explicit opt-in replay retries after busy/failure. Import replay and reconciliation replay remain distinct.

Busy/failure is visible in the additive response/log, with no fake run ID. Record its attempt audit separately when possible; if that audit fails, expose `audit_recorded:false` and the actual diagnostic without rolling back committed import. UI checkbox is opt-in and shows committed import separately from the callback outcome. An ordinary reconciliation evaluates active stored evidence at execution; linkage identifies the triggering import, not an exclusive frozen one-batch result. No event bus, automatic baseline promotion, rule change or new schema follows.

## Request logging and accounting

RFP-005 requires evidence of successful-request access logging and HTTP request-ID correlation to an audited schedule configuration change. Existing response/error request IDs alone do not establish this. The bounded correction may log method/path/status/request ID without request bodies, queries or sensitive headers, and attach `http_request_id` to the actual configuration audit. Preserve failure audit behavior and wider coverage gaps.

Starting accounting remains **32 Demonstrated / 22 Partial / 10 Documentary / 47 Missing = 111**. The separate workbook's 36/21/8/46 differs in 090/092/104/106 and is not accepted here. Lead compares each exact original clause with actual new evidence, preserving remaining gaps; useful partial progress is not automatically Demonstrated. Portable startup/recipient proof, human training, customer phases, live sources and production claims stay separate.
