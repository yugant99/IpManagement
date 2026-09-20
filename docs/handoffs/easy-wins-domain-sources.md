# Easy wins: domain sources handoff

Stage / owner / task: bounded IpManagement RFP-026, RFP-036 and approved RFP-043 UI slice / worker delegated by Main Lead 3.0.

Checkout and owned paths: `codex/easy-wins-domain-sources`; inventory filters, `source_catalog.py`, FirstPath/App filter UI, focused tests and this handoff. `app.py` remains integration-owned by `01a0c0f0-5735-7e52-9f5a-ec45ac8ac99c`.

## Implemented

- `inventory.prefixes` and `inventory.pools` accept case-insensitive exact `domain` and `region` scope metadata filters. The app owner must pass those query parameters and page after filtering so totals match results.
- Intended inventory UI exposes Domain and Region selectors, includes them in the prefix request, and clears them with the existing Clear filters action.
- `source_catalog.catalog(connection, scope_id=None)` reuses `evidence.selected_views`: latest by ingestion sequence for each source/scope, evaluated at `app_meta.demo_clock_at`, with no older-complete fallback. Each row retains source/run/batch receipt references, authority declaration, rejected/duplicate counts, freshness, completeness and time-window grain. Staged intended inventory is shown as `staged` and `not_applicable` freshness.
- FirstPath includes an Imported-source catalog view and the approved opt-in `reconcile_after_import=true` checkbox. Import success remains separate from reconciliation `succeeded`, `busy`, `failed` or `skipped` status.

## API integration handoff

The app owner should wire:

```text
GET /api/prefixes?domain=&region=
GET /api/pools?domain=&region=
GET /api/source-catalog?scope_id=&limit=&offset=
```

The catalog endpoint should call `source_catalog.catalog`, page the returned source/scope rows, attach `evaluated_at` and a synthetic receipt-derived/not-discovery limitation, and return `{items,total,limit,offset}`. Do not add a user-supplied evaluation clock.

## Checks and evidence

- Passed: `PYTHONPATH=backend python3 -m unittest tests.test_easy_wins_domain_sources` (2 tests).
- Passed: focused Python bytecode compile for changed Python files; `git diff --check` passed.
- Frontend build attempted with `npm run build` but could not start because `frontend/node_modules/.bin/tsc` is absent. No dependency installation was performed.
- No browser or integrated API evidence was run. Endpoint wiring and connected-candidate behavior remain unverified until the app owner integrates `app.py`.

## Remaining limits

Domain/region labels remain scope metadata filters; they do not establish tenant security, domain orchestration or cross-domain operations. Catalog entries are known imported receipts, not automatic discovery, and declared authority is not proof of unique authority. Reconciliation backend remains sibling-owned.
