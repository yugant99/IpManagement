# Easy wins: import and logging handoff

Stage / owner / task: bounded RFP-043 and RFP-005 implementation, plus app.py integration for sibling easy wins / worker task `01a0c0f0-5735-7e52-9f5a-ec45ac8ac99c`.

Checkout and owned paths: `codex/easy-wins-import-logging`; `backend/ipam_demo/app.py`, request-ID coupling in `backend/ipam_demo/scheduler.py`, focused import/logging tests, and this handoff/evidence path. Sibling-owned backend/UI changes were integrated only from their exact commits; `app.py` remained this lane's integration surface.

## Implemented

- `POST /api/imports?reconcile_after_import=true` commits the receipt first, then optionally runs the existing reconciliation and exception synchronizer under the shared run lock. Default imports retain their prior response shape and status.
- Successful batch-to-run linkage is durable in `audit_events` as `source.import.reconcile`; replay rechecks the link while holding the lock and verifies the saved run exists. The immutable source receipt is not rewritten.
- Staged intended-inventory receipts return additive `reconciliation.status=skipped` with `STAGED_INVENTORY`; busy and downstream failures remain separate from the committed import and expose `audit_recorded` plus bounded audit-write diagnostics.
- Access logs contain bounded method/path/status/request ID without query strings or payloads. Successful schedule configuration stores the HTTP correlation under `details.http_request_id`, leaving the domain `request_id` field unset.
- App integration wires family filters on saved-run export/findings, domain/region filters on prefix/pool listing, and the receipt-derived `/api/source-catalog` endpoint with pagination, evaluation clock and non-discovery limitations.

## Observed checks

- Focused backend: `uv run --no-sync python -m unittest tests/test_easy_wins_import_logging.py tests/test_easy_wins_reports.py tests/test_easy_wins_domain_sources.py` — 12 passed after the held-lock busy case was added; the import-only rerun was 6 passed.
- Frontend: `npm ci` from the unchanged lockfile, then `npm run build` — TypeScript and Vite build passed on Node 23.11.0; the repository's declared Node range excludes this runtime, so supported-runtime portability remains unverified.
- Disposable HTTP candidate on `127.0.0.1:8765`: synthetic routing import returned 201 with `X-Request-ID=aeda3f5b-b2a3-484a-835a-3d699f3ef4d9`, batch `53e7a368-9b2b-4704-a60a-e8892122b761`, run `48f45365-389f-4970-a7ba-716497b58758`, and reconciliation succeeded/replay false. Identical replay returned `X-Import-Replay:true` and reconciliation succeeded/replay true using the same run.
- The same disposable candidate returned domain/region-filtered prefixes, one receipt-derived catalog row at `2026-09-01T00:00:00.000Z`, and family-filtered findings/export totals of 146 findings and 8 calculations. The supported CLI schedule capture matched response/access/audit request ID `dbcb9bb7-e6aa-417d-93b3-9fc048234167`; the audit row's domain request ID was empty. Exact sanitized content is [schedule-correlation.txt](../evidence/easy-wins/import-logging/schedule-correlation.txt).
- IPv6 saved-report HTTP parity on the same run: preset revision `ad9303d7575ae987c0c021987a6c57888bb5eac7413a6454ca91cfa73a67b319`, direct JSON export 27 findings / 0 calculations, paginated findings 27 rows, and CSV 27 rows with columns `subject,scope_id,evidence_state,rule_id`. Raw temporary responses/logs are outside Git at `/tmp/ipam-import-response.json`, `/tmp/ipam-replay.json`, `/tmp/ipam-domain.json`, `/tmp/ipam-catalog.json`, `/tmp/ipam-family6.json`, `/tmp/ipam-family6-findings.json`, `/tmp/ipam-preset.csv`, and `/tmp/ipam-schedule-audit.json`; disposable store was `/private/tmp/ipam-easy-wins-browser.7d5s14`.

## Evidence limits

Focused tests cover callback failure, import preservation, retry, replay and refused failure-audit writes. Busy behavior is implemented with the shared nonblocking guard but no separate live busy run was recorded. No cloud, Docker, deployment, broad E2E or production configuration-audit coverage is claimed. Minimal browser observation on the same candidate produced 12 domain/region-filtered prefixes; staged callback status `skipped · STAGED_INVENTORY`; catalog evaluated-at `2026-09-01T00:00:00.000Z` with routing `fresh · complete` and staged `not_applicable · unknown`; and saved-run family filtering with changed summary/export URL. Browser console had one expected `/favicon.ico` 404 and no application UI error. This is not a substitute for broader acceptance.

## Checkpoint

Implementation checkpoint before this handoff: `506c137` on `codex/easy-wins-import-logging`. The final handoff commit and pushed SHA are reported by the owning worker after this file is added.
