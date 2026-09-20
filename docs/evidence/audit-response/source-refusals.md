# S5-15 supplemental observations: prior-success assets and first-path authority

**Observed pass; accepted by Main Lead 2.0 after independent artifact review on 2026-09-19.** Exact application baseline: `a279f32df0ac7d2147b580dbff36dd88772bdeb2`. Executed on 2026-09-19 local time (2026-09-20 00:53 UTC). This closes the two specifically missing source-refusal observations as new evidence; it does not rewrite the historical S5-15 partial record or substitute for final F1–F7 rehearsal.

Observer: external stdlib Python harness driving the actual installed CLI and localhost HTTP API on port `18874`. A newly locked environment imports this acceptance checkout and its producer; `import-origins.txt` records both paths. No production monkeypatch, fixture expected-answer input, application edit or frontend build was involved. The absent new static build is intentionally not a UI readiness claim.

Local evidence root:

`/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-audit-artifacts/run-20260919-zzeadfai/source-refusals/`

`acceptance.py`, `identity.json`, `result.json`, `observations.json` and `console.log` retain the recipe and result. Each case retains actual request/response/headers, command outputs, process identity/start/stop logs and full logical snapshots plus per-table row counts/digests. **34 observer assertions passed; all six owned child services stopped.** These assertions are not 34 distinct questionnaire requirements or catalog scenarios.

## Previously successful populated state

A fresh rich store completed actual acquisition cycle 1 at scenario clock `2026-09-01T06:00:00.000Z`. Requester and independent approver persisted one new local allocation, then saved a report preset pinned to the acquired run. State contained 9 source batches, 2,266 raw source records, 1 saved run, 10 exceptions, 14 audits, 1 approved allocation request, 2 total intended allocations, 1 preset and 1 committed acquisition operation.

| Identity | Observed value |
|---|---|
| Cycle-1 operation | `769f5094-2301-48ad-95a4-6e3134833068` |
| Cycle-1 saved run | `c8476ef5-0821-40ae-b65c-3689bb80e4ec` |
| Approved allocation request | `ea251163-5964-42b5-b808-72ad9774238e` |
| Recovered cycle-2 operation | `21494fa5-f5c6-4c95-a768-3bbc00f02449` |
| Recovered cycle-2 saved run | `44c71f5b-7eed-4b53-8e11-76a675028a5f` |

The service stopped before each asset substitution. One new process used copied assets with an extra newline in `observations/routing-lab.json`; another used a copy where that file was renamed out of the required path. Original fixture files were untouched. Fresh processes are essential because successfully loaded assets are cached in-process.

Both variants returned ineligible status and HTTP 503 `SYNTHETIC_FEED_UNAVAILABLE` for enable and new Run now. The actual altered-file hash and missing-path error were retained. Each enable refusal added one failure audit; each acquisition refusal added one failure audit and explicit failed attempt/error status. All pre-existing audit rows remained identical.

All 15 actual application tables were enumerated. Only `audit_events` and `schedule_status` changed; inventory, allocations, requests, source receipts/records/coverage, saved runs, exceptions, preset, clock and committed operations were identical. Protected schedule configuration, last success, cycle identity/cursor and last successful run were unchanged. Failure status was not misreported as full-table immutability.

The retained successful cycle-1 key replayed under both invalid-asset variants with the same operation/run IDs, HTTP 200 and `replay:true`; full logical state before/after each replay was identical. Returning to original pristine assets in a fresh process committed exactly cycle 2 at `2026-09-01T12:00:00.000Z`, reaching 18 source batches, 2 runs and 2 operations while preserving the original run, allocation and preset.

Evidence subdirectories: `populated-assets/`, `populated-altered-assets/`, `populated-missing-assets/`.

## First-path-specific refusal

| Fresh control | Observed refusal | Preserved usability |
|---|---|---|
| Packaged minimal baseline plus actual first-path policy, North routing and Lab routing files | HTTP 409 `SYNTHETIC_FEED_INCOMPATIBLE`; original rich-v1 seed identity/baseline required | All three imports accepted; ordinary run before and after refusal succeeded |
| Rich seed at baseline clock plus actual `synthetic-first-path-routing-lab` import | HTTP 409 `SYNTHETIC_FEED_INCOMPATIBLE`; competing source authority explicitly identified | Import accepted; ordinary run before and after refusal succeeded |

For both, GET eligibility, enable and new Run now refused scheduling. Only explicit failure audit/status changed during refusals, with all prior logical rows preserved. Ordinary reruns created a distinct second saved run without advancing the scenario clock, acquiring source batches or creating schedule operations. First-path evidence was accepted for ordinary reconciliation; incompatibility was specifically the pinned scheduled feed contract.

Evidence subdirectories: `first-path-baseline/`, `first-path-rich-authority/`. Services were stopped with SIGINT after requests completed; this is cleanup, not the separate in-flight OS-shutdown proof.

Independent read-only review compared retained snapshots and corroborated all 34 assertions, the exact two added failure audits per refusal pair and all six zero-exit shutdowns. The pristine recovery's single observed advance added 9 batches, 12 coverage rows, 2,272 source records, 1 run, 1 operation and 1 success audit. The cycle-2 key itself was not replayed; the prior cycle-1 key was replayed twice. No observer failures occurred in this S5-15 run. These checks do not cover every filesystem failure, feed exhaustion, real-time endurance, live source or portable runtime condition.
