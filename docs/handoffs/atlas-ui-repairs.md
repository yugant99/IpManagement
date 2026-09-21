# Atlas UI repairs handoff

Status: ready for bounded project-lead review; this is a frontend-only repair checkpoint, not global acceptance.

## Candidate

- Base: accepted main `392e9b594169b49d49b57e1edc9eecbe4598d405`
- Branch: `codex/atlas-ui-repairs`
- Code checkpoints: `48c2b4e` Capacity findings, `3b83f20` saved-run totals, `d71ae4e` exception detail focus
- Final source correction and docs publication are the pending head after this handoff edit.
- Owned paths: `frontend/src/CapacityReports.tsx`, `frontend/src/FirstPath.tsx`, `frontend/src/Workflow.tsx`, `frontend/src/styles.css`, and this handoff.
- No backend, schema, API, dependency, fixture, global accounting, VM, Docker, or demo-store changes.

## Repairs

1. Capacity keeps scope and address family as the only pool-metric filters. All five selected filters now visibly narrow a bounded, keyboard-focusable “Matching saved findings” region with count and zero-result handling; rule, state, and severity do not alter occupancy calculations.
2. Saved-run history shows total evaluations. Open results label the full saved-run total separately from the paginated filtered finding range. The count comes from `run.overview.total`; it is not hardcoded.
3. Opening an exception marks its row, exposes `aria-expanded` and `aria-controls`, and focuses a CIDR/scope-specific detail heading. Reopening the same case repeats focus/scroll. The detail heading scrolls with a top margin and the first detail section remains visible.

## Focused validation

- Supported Node 24.21.0 TypeScript no-emit and Vite production build passed after the final source changes.
- `git diff --check` passed.
- Preserved compiled API preview at `http://127.0.0.1:8000/`, PID 64292, store `/tmp/ipam-atlas-f234-rich-20260921`; no seed, reset, restart, VM, Docker, or reprovision action was taken.
- Browser evidence on the compiled preview: canonical run `32ef5528-2b16-4050-ad5e-533dde438289` showed `173` total evaluations and `1–20 of 173` matching findings; Capacity `ghost_scope` showed `7 of 173`, `unknown` showed `0` with explicit empty state; exception open showed one selected row, expanded control, focused heading `pool_pressure · 10.60.1.0/24 · Coastal · case open`, and the first detail section in view.
- No broad application test suite was run. No browser data mutation was performed.

## Try flow

1. Open Reconciliation → expand “Open a saved calculation run” → open run `32ef5528-2b16-4050-ad5e-533dde438289`.
2. Confirm “Total evaluations in saved run 173” and the paginated “Showing 1–20 of 173 matching findings” line. Change a result filter and confirm the matching range changes while the full total stays 173.
3. Open Capacity → select the same saved run → choose `ghost_scope` and confirm the matching-findings region reports `7 of 173`; choose `unknown` and confirm the zero-result message. Pool cards remain capacity-filtered by scope/family.
4. Open Requests and exceptions → activate an “Open exception” action. Confirm the row highlight, expanded/controlled button, focused CIDR/scope heading, and visible detail content.

## Limits and next owner

- Synthetic/local evidence only. No production, live discovery, external provisioning, VM, Docker, or portable-recipient claim follows.
- Project lead owns independent review, final narrow-layout/keyboard confirmation, PR creation/merge coordination, and acceptance accounting.
