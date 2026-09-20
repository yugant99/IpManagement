# IPAM design experiment

## Purpose and boundary

This is a standalone visual study, not an application redesign or an implementation request. It uses synthetic labels and values. It does not change React components, APIs, schemas, calculations, persistence, permissions, or the application's saved-run semantics.

Open `ipam-design-study.html` in a browser. It contains three genuinely distinct visual directions with overview/inventory, detail, saved evidence, capacity, exception, and approval context.

## Recommendation: Atlas

Atlas is the recommended foundation. It is a durable operational-record design, not a dashboard skin:

- A persistent left rail follows the existing product's top-level areas: inventory, reconciliation (`FirstPath`), capacity, workflow, corrections, schedule, and saved runs.
- A persistent scope bar anchors scope, family, region, and report context, matching the existing scope-aware model.
- The main table holds intended inventory; a right-side detail or evidence panel provides context without pretending every item is current network truth.
- A saved-run card always names the run ID/time and source eligibility. Current exception and approval state is visually separate.
- State language remains literal: **intended**, **eligible**, **partial**, **unknown**, **anomalous**, **open**, and **acknowledgement due**. Color reinforces, never replaces, those words.

## Direction tradeoffs

| Direction | Best setting | Strength | Cost |
| --- | --- | --- | --- |
| Atlas | everyday inventory plus decisions | clearest general-purpose evidence hierarchy | less maximal information density |
| Console | high-volume investigation/triage | fast scanning and source-state comparison | a more specialized operations-console character |
| Ledger | review meetings and approvals | decisions and limits are exceptionally legible | slower for large inventory browsing |

## Research inputs

- [NetBox Visual Explorer](https://netboxlabs.com/docs/visual-explorer/) uses per-view scope, a right-side detail panel, and makes its system-of-record boundary explicit. Atlas borrows the scoped-view and inspect-in-context approach, not the topology-heavy visual language.
- [NetBox Analytics](https://netboxlabs.com/docs/analytics/) pairs high-level capacity/data-health questions with actionable detail tables and acknowledges that trend history begins when collection begins. This supports a table-first capacity view and explicit insufficient-history state.
- [NetBox Assurance getting started](https://netboxlabs.com/docs/validation/getting-started/) separates everyday results review from policy/configuration work. Console similarly puts the working queue and evidence status first, without turning the demo into a policy platform.
- [Infoblox IPAM administration lab](https://docs.education.infoblox.com/lab/2586) presents conflict investigation in the IP map and opens the selected record for detail. The concepts retain direct subject-to-detail drilling, but avoid color-only conflict meaning.

## Narrow later implementation plan

1. In `frontend/src/styles.css`, introduce only shared visual tokens and the Atlas shell: ink/paper palette, line weights, type scale, scope bar, literal evidence badges, and a wider content detail layout. Keep existing controls and accessibility behavior.
2. In `frontend/src/App.tsx`, adapt the existing navigation into the Atlas rail/header while retaining the same view values and loaded data. No route or API change.
3. In `FirstPath.tsx`, `CapacityReports.tsx`, `Workflow.tsx`, `Corrections.tsx`, and `Schedule.tsx`, apply the shared saved-evidence/current-workflow labels consistently. Preserve all current warnings, eligibility behavior, retries, and state changes.
4. Review at real narrow and wide browser widths with representative existing fixtures before accepting the visual change. This study did not run the application, build, or tests.

## Existing contracts preserved

The proposed presentation keeps the current architecture intact: React/Vite frontend, FastAPI API, SQLite persistence, relative `/api/*` calls, scoped IPv4/IPv6 identity, immutable saved calculation runs, and fixed approval flows. It does not introduce a UI library, charts package, design dependency, new endpoint, or separate frontend metrics logic.
