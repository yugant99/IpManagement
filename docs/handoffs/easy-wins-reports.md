# Easy wins: RFP-035 and RFP-077

Stage / owner / task ID or exact task title: Easy wins reports worker / Luna medium / delegated from Main Lead 3.0 (`01a0c0c1-3952-7720-93c8-ff49192b8e13`)

Checkout/worktree and owned paths: `/Users/yuganthareshsoni/.codex/worktrees/bb9a/Ip_inventory`; `backend/ipam_demo/reports.py`, `frontend/src/CapacityReports.tsx`, `tests/test_easy_wins_reports.py`, this handoff, and `docs/evidence/easy-wins/reports/`.

Questionnaire IDs changed: RFP-035 address-family filtering and report/export parity; RFP-077 saved-run executive summary.

Branch / exact pushed SHA / PR: `codex/easy-wins-reports` / `d3a4a5a7ebe8897bfed2593584b9adf85edb4bd0`; PR is not opened by this worker. The branch is ready for the integration owner to merge or open a bounded PR.

Integration base / unmerged dependencies: baseline `852010a311065a9cc0258fc4e3f5c1c1a889329a`; app.py route wiring remains with integration owner `01a0c0f0-5735-7e52-9f5a-ec45ac8ac99c`.

Implemented:

- `reports.filtered_findings` accepts optional `family` with strict `4`, `6`, or empty validation. Existing filters and presets without family remain valid.
- JSON saved-run export filters both findings and calculations by family; calculations remain limited to scope plus family, while rule/severity/evidence-state remain finding-only filters.
- The report UI adds an IPv4/IPv6 selector, includes it in preset payloads and direct JSON export parameters, and applies it to visible capacity metrics.
- The saved-run summary reports anomalous findings, unknown findings, affected scopes, and unique anomalous `pool_pressure` subjects. It shows the selected run ID, `created_at`, and `demo_clock_at`; it does not merge current exception state or infer pressure from unavailable capacity evidence.
- The integration owner has the proposed app.py contract: add `family` to `/api/runs/{run_id}/export` and `/api/runs/{run_id}/findings`, preserve JSON export media type, and preserve pagination totals.

Actually observed and evidence pointers: code checkpoint `00c8dd9` contains the backend implementation and focused tests; UI checkpoint `318f48c` contains the frontend implementation; current branch head is `d3a4a5a7ebe8897bfed2593584b9adf85edb4bd0`. Focused unit evidence is recorded in `docs/evidence/easy-wins/reports/focused-check.md`.

Synthetic / simulated / partial / unverified: report data and source evidence remain synthetic/local. No browser evidence or integrated HTTP route evidence was produced in this isolated worker because app.py is outside ownership. Frontend build was attempted once and is unverified because `frontend` dependencies are absent (`tsc: command not found`).

Checks actually run and authorization: authorized focused check only: `PYTHONPATH=backend python3 -m unittest tests/test_easy_wins_reports.py` — 3 tests passed. `npm run build` was attempted once as the requested relevant frontend build and stopped at missing `tsc`; no install was performed. `git diff --check` passed.

Blocker / requested lead decision: integration owner must wire the two `family` query parameters in app.py. Lead should review the exact summary labels and route diff. Frontend build needs a dependency-equipped checkout before UI acceptance.

Suggested next-stage prompt: “Review and integrate `codex/easy-wins-reports` at the pushed SHA; wire `family` into the two existing saved-run routes using `reports.filtered_findings`, preserve JSON export and pagination boundaries, then run one focused route check and a dependency-equipped frontend build. Keep browser/runtime evidence separate from this synthetic/local worker evidence.”
