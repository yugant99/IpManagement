# Demo document drift vs tracked frontend — 2026-09-24

`docs/DEMO_STORY.md` and `docs/DEMO_RUNBOOK.md` are treated here as the
already-recorded native rehearsal's history. They are **not** edited and
**not** repurposed as the new Sources/Reconciliation demo script. Each row
names an outdated UI instruction, the exact current-frontend evidence, and a
proposed replacement sentence for a future (separately authorized) doc update.

Evidence actually read: `docs/DEMO_STORY.md`, `docs/DEMO_RUNBOOK.md`,
`docs/RUNNING.md`, `fixtures/SCHEMA.md`, `backend/ipam_demo/imports.py`,
`backend/ipam_demo/source_catalog.py`, `frontend/src/App.tsx`,
`frontend/src/FirstPath.tsx`, `frontend/src/Schedule.tsx`,
`frontend/src/Workflow.tsx` (lines 1–829), `frontend/src/Corrections.tsx`,
`frontend/src/CapacityReports.tsx`, `frontend/src/InventoryEditor.tsx`,
`frontend/src/MigrationCompare.tsx`. Direct fetch verified the Kea, ISC,
dnstap, and BIND references cited in the companion interface memo; the Cisco
page fetch did not verify a MIB-table operation.

## Outdated UI instructions

| # | Recorded instruction (history — do not edit) | Current frontend evidence | Proposed replacement sentence |
|---|---|---|---|
| 1 | `docs/DEMO_STORY.md:13` + `docs/DEMO_RUNBOOK.md:98-104`: open the app at a loopback URL, check `/healthz`, use "Reconcile stored inventory" vs "Run now". | `frontend/src/App.tsx:411-420`: entry is a "Pool Watch access" token form then "Select a permitted domain"; `App.tsx:260-280`: rail views are Inventory / Reconciliation / Capacity / Requests and exceptions / Corrections / Migration assessment / Prefix planning / Synthetic acquisition. No "Reconcile stored inventory" or "Run now" labels exist in the tracked views. | "Sign in with an access token, select a permitted domain, then use the named rail view (e.g. Reconciliation); global reconcile/acquire controls are not in this domain session." |
| 2 | `docs/DEMO_STORY.md:26`: "'Reconcile stored inventory' does not advance the scenario clock; 'Run now' acquires the next cycle. Do not enable the timer." | `frontend/src/FirstPath.tsx:312-313`: "The evidence operator manages global reconciliation. This view reads permitted saved domain projections." `frontend/src/Schedule.tsx:3-9`: domain session shows a read-only notice — "Global acquisition, timer, schedule and callback controls are managed by the evidence operator." | "In a domain session there is no Run-now or timer control; open a saved domain run, and leave global acquisition to the evidence operator." |
| 3 | `docs/DEMO_STORY.md:13,20`, `docs/DEMO_RUNBOOK.md:106-116,119`: presenter-ready cycle-1 copy, pinned preset, deliberate cycle 1→7 acquisition plan with fixed run IDs (`docs/DEMO_RUNBOOK.md:26`). | `frontend/src/FirstPath.tsx:142-154`: runs open via collapsible "Open a saved calculation run" with per-domain projections (`FirstPath.tsx:219-221`: "Totals come from this saved run's selected-domain projection … New imports do not change this result."); `FirstPath.tsx:315-318`: "Awaiting saved evidence … The browser does not calculate findings." The single report preset is now saved per run/filters/columns from Capacity and reports ("Report preset saved with this run, filters and columns", `frontend/src/CapacityReports.tsx:117-125,210-212`). Cycle clocks/IDs are recorded history, not live UI state. | "Treat cycle-1…7 run IDs and the pinned preset revision as saved history; open the named saved run and confirm its selected-domain projection instead of acquiring cycles live." |
| 4 | `docs/DEMO_RUNBOOK.md:11-30,44-100,124,150-174`: candidate SHA/PR, absolute `/Users/…` checkout/root paths, port `18892`, snapshot SHA256 values, `backup`/`restore`/`seed` shell templates with `DEMO_*` variables and per-cycle run/preset IDs. | `docs/RUNNING.md:6-13` records the actual bounded VM execution that was observed; `RUNNING.md:53-86` gives the current package path (`scripts/ops/build.sh`, `seed.sh`, `start.sh`, `health.sh`, `acquire.sh` with coordinator token file, stable key, and reason); `RUNNING.md:230-326` documents the real stopped-service state commands (seed/migrate/backup/restore/reset via `scripts/ops/`). The serve/seed/backup/restore operations are real — the drift is that the old runbook's machine-specific paths, port, snapshot hashes, and IDs are that rehearsal's provenance, not reusable instructions. | "Follow `docs/RUNNING.md` (`scripts/ops/` build/seed/start/health/acquire plus stopped-service state commands) for any new run; treat the old runbook's absolute paths, port `18892`, snapshot hashes, and run/preset IDs as that rehearsal's history, not as current setup steps." |
| 5 | `docs/DEMO_STORY.md:15,18`, `docs/DEMO_RUNBOOK.md:133-139`: "propose `10.80.240.0/24` as requester, switch to an independent approver, approve"; "request the displayed available address, switch actor and approve". | `frontend/src/Workflow.tsx:768-800`: allocation create requires `actor_id`, fresh idempotency key, `pool_id`, `pool_version`, `baseline_version` (plus optional reservation link fields); decision posts `actor_id` + reason with an expected outcome, guarded by recovery-pointer/idempotency state (`Workflow.tsx:61-118,594-606,619-739`). "Switch actor" alone omits keys, versions, and uncertain-outcome readback. | "Create the request with current reviewed versions and a fresh idempotency key, then decide it as a different actor with a reason; on timeout or connection loss, read back the saved receipt by its key before retrying." |
| 6 | `docs/DEMO_STORY.md:15-17`: ghost/raw inspection, metadata-gap fix, exception close/reopen told as one continuous presenter flow ("select the saved anomaly, propose `10.80.240.0/24` as requester, switch to an independent approver, approve and reconcile"). | Corrections is now its own four-step view (`frontend/src/Corrections.tsx:289-366`): 1. review saved discrepancy evidence from a saved run (`Corrections.tsx:303-321`, ghost-scope / unregistered-route anomalous findings only); 2. propose a missing top-level prefix with CIDR/owner/purpose/reason (`Corrections.tsx:323-333`, "Pending proposals do not change or reserve inventory"); 3. review and decide a saved proposal with an independent Approver (`Corrections.tsx:335-349`); 4. inspect later saved evidence via the evidence operator (`Corrections.tsx:363-366`, "Approval alone does not establish finding resolution"). Prefix-metadata fixes live separately in Prefix planning (`frontend/src/InventoryEditor.tsx:118-148`, metadata-only edits preserve p95/forecast eligibility). | "Show each step in its own view — saved finding plus raw record in Reconciliation, staged receipt without auto-recalculation, then the separate Corrections / Requests-and-exceptions action — naming the saved run at each step." |
| 7 | `docs/DEMO_RUNBOOK.md:68,91-94`: `IPAM_SYNTHETIC_FEED_DIR=fixtures/v1` with eight observation envelopes; `seed --scenario rich`. | `backend/ipam_demo/imports.py:370-381`: domain imports accept only `routing`/`dhcp`/`inventory_policy` envelopes declaring `fixture_contract: ipam-synthetic-v1` + `synthetic: true` (plus staged inventory via `scenario`); `FirstPath.tsx:273-274,304-305`: "Only staged intended-inventory candidates can be imported from this domain view … No automatic reconciliation." Feed-dir acquisition is an operator path, not a domain upload. | "Domain upload accepts only a staged intended-inventory candidate and reconciles nothing; synthetic-feed acquisition and seeding are evidence-operator steps against the pinned contract." |
| 8 | `docs/DEMO_STORY.md:17,37`, `docs/DEMO_RUNBOOK.md:133,142-144`: exception escalate/handoff/acknowledge/close told with refreshed versions; "F5 closure" prose. | `frontend/src/Workflow.tsx:148-829` implements notices, handoffs, reservations, releases, readbacks, and acknowledgement as distinct versioned operations with quarantine/recovery semantics; exact close/reopen labels and version-refresh wording in the recorded docs do not match these tracked control names one-to-one. | "Perform each exception/notice/handoff action under its tracked control name with the current version shown in the UI, and describe closure and evidence resolution as separate facts." |

## Source-only limits and unverifiable items

- Not readable (permission denied), so not used as evidence:
  `docs/CURRENT_HANDOFF.md`, frontend directory listing,
  `frontend/src/api.ts`, `firstPathApi.ts`. `Workflow.tsx` lines past ~829
  were outside the read window; ticket, notice, and release button labels past
  that point are unverified.
- `Corrections.tsx`, `CapacityReports.tsx`, `InventoryEditor.tsx`, and
  `MigrationCompare.tsx` were read in full for this correction pass and are
  cited above; no file is claimed unreadable that is in fact readable here.
- Vendor docs: direct fetch verified the four URLs cited in the companion
  memo (Kea agent, ISC leases, dnstap slides, BIND reference); Infoblox and
  Cisco URLs are lead-supplied pointers and version-specific behavior stays
  explicitly unverified. No R3 polling work was started.

Files written by this task: `docs/integrations/dhcp-cmts-dns-interfaces.md`,
`docs/plans/demo-doc-drift-2026-09-24.md`. No code, fixture, or other file
was edited. The lead will commit reviewed outputs.
