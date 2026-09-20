# Atlas UI repair acceptance

Main Lead 3.0 accepts the user's three bounded frontend repairs. [PR #65](https://github.com/yugant99/IpManagement/pull/65), exact head **`3d38399c4a4b248fa3e4231598e723143023011a`**, merged normally at **`4d59a77f3783cf1fdc90e0c7413438aa5b76c39f`**. The existing visible Atlas task used GPT-5.6 Luna / medium, with its branch and coherent commits preserved. [Authorization](atlas-ui-authorization.md) and [worker handoff](atlas-ui-repairs.md).

## Behavior and review

- **Capacity:** all five filters now visibly narrow a matching-findings table with a count and empty state. Its scroll area is bounded and keyboard accessible. Scope/family govern saved pool metrics; rule/state/severity govern findings and the report summary. No occupancy calculation or export/preset meaning changed.
- **Reconciliation:** saved-run history now includes total evaluations. Open results prominently label the existing `run.overview.total`, and the filtered list states its current page range, matching total and full saved-run total separately. The total already existed in the earlier result view under “Evaluated”; this repair improves discoverability and count clarity rather than adding or hardcoding a calculation.
- **Exceptions:** opening a case marks the selected row/button, exposes expanded/control semantics and moves focus to its rule/CIDR/scope heading near the top of the viewport. Opening the same selected case repeats that response. Existing ownership, review versions and mutation controls are preserved.

Lead review corrected the initially unbounded findings table, inaccurate paginated “displayed” count, loading text on errors, misleading filter direction wording and scroll-margin placement. No blocking finding remains within this scope. Changes are confined to three frontend components, their small style additions and handoff documentation; backend, schema, fixtures and dependency locks are unchanged.

## Focused evidence

The worker's supported Node **24.21.0** TypeScript no-emit and Vite production build passed after the final source changes. The lead read the complete source diff and independently inspected the compiled UI on the retained native service:

- Canonical run `32ef5528-2b16-4050-ad5e-533dde438289` reported **173 total evaluations: 11 anomalous / 108 healthy / 0 unknown / 54 not applicable**, matching the API. Filtering Reconciliation to anomalous showed **1–11 of 11 matching findings**, while the full total remained 173; the unfiltered first page showed 1–20 of 173.
- Capacity rule `pool_pressure` showed **8 of 173** findings; adding anomalous narrowed to **2**; critical severity produced **0** with an explicit empty state. Coastal/IPv4 with anomalous/high pool pressure showed two matching findings and two pool cards; IPv6 changed both counts to zero. The worker separately observed `ghost_scope` at seven matches and unknown at zero.
- At **390×844**, the page width remained 390px. The findings region was 420px high; it received keyboard focus and ArrowDown changed its internal scroll position. Tables retain their own horizontal scrolling. Reconciliation also stayed within the viewport.
- Keyboard activation opened the Lab metadata-gap case, selected exactly one row and focused its identifying heading about 24px from the viewport top; the first evidence section was visible. Desktop switching to the Central oversized-pool case and opening it again preserved correct selection/focus. The viewport override was reset afterward.

These were read-only selections and navigation, with no demo-data mutation, seed/reset, backend restart, VM/Docker work or broad E2E cycle. The owned API process remained PID 64292 / session 44304, using `/tmp/ipam-atlas-f234-rich-20260921`; static assets were updated by the frontend build. Treat the PID as a historical pointer and inspect ownership before future service operations.

## Updated try flow

Refresh **http://127.0.0.1:8000/** to load the repaired compiled UI.

1. **Capacity:** select the canonical saved run above. Choose `pool_pressure`, then anomalous: the matching findings change from eight to two. Scope/family also filter the pool cards. The saved CSV preset remains explicitly separate from unsaved current filters.
2. **Reconciliation:** expand **Open a saved calculation run**, then open that run. Inspect **Total evaluations in saved run: 173** and the separate filtered page count; choosing anomalous leaves the total at 173.
3. **Requests and exceptions:** activate **Open exception**. The selected row says **Opened**, and the corresponding detail heading receives focus and comes into view.

Accounting remains **39 Demonstrated / 18 Partial / 10 Documentary / 44 Missing = 111**. The earlier Linux VM evidence stays pinned to `eab1d3376633bf3280ff7bd8834fe46c88353d9a`; these frontend repairs were validated locally only, as requested. The retired VM was not recreated. No new questionnaire credit, production claim, implementation stage or automatic test cycle follows. Human practice/recipient acceptance and other recorded customer limits remain separate.
