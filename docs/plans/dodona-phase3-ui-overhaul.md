# Dodona Phase 3 UI overhaul

## Goal and boundary

Apply the approved operational concept to the existing React/Vite app. Keep the Dodona logo and palette, the current navigation, domain and evidence semantics, and the saved data behind each view. The concept image is a visual reference with illustrative records; no displayed example becomes fixture or API data.

The new Evidence Sources view remains the landing screen. Twelve mechanisms are possible; the seeded inventory baseline and imported synthetic DHCP/routing evidence are the three with demo evidence. No Rogers or live operator connection is claimed. Spencer owns login and OIDC separately.

## Shared visual contract

- Forest green `#365b3b`, ink `#27372d`, ivory `#f7f8f1`, sage `#eef2e5`, restrained gold `#9a7428`.
- Optima-like headings near 29px for page titles and 18px for sections; Avenir Next-like body/table near 15px, navigation 14px, supporting labels at least 13px. Keep technical IDs/CIDRs in the existing mono stack. No downloaded fonts or new UI library.
- Use a calm table-first layout, thin rules and clear selected-row state. Prefer grouped rows to KPI-card grids. Keep the current focus, loading, empty, error and unknown behaviors visible.
- Inventory is intended state: prefix, owner, purpose, scope, tags and source references. Saved-run health and drift stay in Reconciliation/Capacity, never inferred in Inventory.
- Fit populated tables, long IDs and narrow screens. Horizontal scroll regions keep keyboard access and labels.

## Work ownership

All branches start at the tested R1+R3 head `23aa12a`, and all worktrees are isolated from the recorded demo checkout/store.

| Slice | Owned files | Integration note |
| --- | --- | --- |
| Shared shell and Inventory | `frontend/src/App.tsx`, `frontend/src/styles.css`, this plan | Touch ProtectedApp/Inventory only in `App.tsx`; do not edit Spencer's login section. |
| Evidence Sources | `frontend/src/Sources.tsx`, new `frontend/src/SourcesView.css` | Preserve the 15-second polling, evidence provenance, EMS sample label and all twelve mechanisms. |
| Reconciliation | `frontend/src/FirstPath.tsx`, new `frontend/src/ReconciliationView.css` | Preserve receipt/run/finding identity and unknown states. |
| Capacity | `frontend/src/CapacityReports.tsx`, new `frontend/src/CapacityView.css` | Preserve saved-run and current static occupancy distinctions, filters, presets and exports. |

Component CSS must be scoped under each view root so the parallel branches integrate without shared-file edits. The lead integrates coherent commits, reviews the combined diff, then runs the presenter browser flow on a copied synthetic store and separate port. Spencer's login change is integrated sequentially and tested separately when available.

## Acceptance pass

On the exact integrated candidate: frontend build; domain selection; Sources mechanism/status and sample EMS wording; synthetic DHCP evidence; Inventory table/filter/detail/source reference; Reconciliation saved receipt/run/finding; Capacity run/filters/export; off-camera acquisition reflected through polling; navigation, focus, and narrow layout. Report the exact candidate and every unverified condition. Do not use the recorded demo's port 18841 or its store.
