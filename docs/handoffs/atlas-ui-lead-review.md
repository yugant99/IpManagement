# Atlas UI lead acceptance

Main Lead 3.0 accepts the bounded Atlas frontend follow-up under the [user authorization](atlas-ui-authorization.md). [PR #60](https://github.com/yugant99/IpManagement/pull/60), final worker head `04b4deecbee61be98fef247f4fc5a8252c885aff`, merged normally at `116afdc6a58d28a4a872ec565c775070f45d3eb1`. Accepted production source is `0cf2f3e1f444d8199cd203d740ec87e9928c0f80`; later worker changes are documentation only. Contributor history and branch are retained.

## Review outcome

The lead read the complete frontend diff and the final handoff. The change preserves existing component state, API calls, permissions, reports and saved evidence. Atlas uses the selected light paper/white direction with grouped navigation and literal evidence labels. There are no backend, schema, fixture or dependency-lock changes and no invented metrics or placeholder actions.

Review closed three concrete issues: the first pass used the unselected dark Console treatment; sticky navigation could leave the destination heading above the viewport; and a populated saved-run selector overflowed a 390px viewport. The worker also corrected panel gutters, stale navigation wording and startup provenance. No blocking finding remains in this bounded review.

## Actual evidence

- Worker: Node 24.21.0 TypeScript no-emit and Vite build passed after the final CSS change. Final native preview uses Python 3.12.10 and frozen dependencies, FastAPI 0.141.1/Uvicorn 0.50.1. Early baseline/Vite observations are distinct from this final rich preview.
- Worker: fresh rich inventory loaded 60 prefixes; scope/domain/region/family/IP filters worked, including containing parent and child; opt-in DHCP import accepted 750 rows and reconciled; manual acquisition committed cycle 1. Reports, source catalog, current workflow/audit, 11 open exception records, corrections and schedule controls were inspected. See the [worker's exact flow](atlas-ui.md).
- Lead: desktop and 390×844 layout inspection, rail keyboard movement, skip-link followed by Tab reaching the active view's refresh button, and populated-view overflow checks. The corrected Capacity selector is 358px wide; the document is 390px wide with no horizontal page overflow. Other inspected populated narrow views also stayed within 390px. Tables retain their local horizontal scrolling.
- Lead: from Acquisition schedule at document scroll 815px, selecting Reconciliation returned scroll to 0 and placed its heading at 127.5px. Existing view data stayed mounted. The worker separately observed prefix-detail close returning focus to its source row.
- Lead: the compiled app loaded 60 prefixes, and the real Saved run control selected `32ef5528-2b16-4050-ad5e-533dde438289` and displayed its summary. The CSV action reported a download request without a visible error; its revision-bound endpoint returned HTTP 200, `text/csv`, a matching preset-revision header and 173 rows, all tied to that run. The browser automation download-event wait timed out, so a locally saved CSV file is not claimed by this observation. Earlier accepted export evidence remains separate.
- Lead: `/healthz` reported process/schema/data/static readiness and schema 5 on the retained compiled UI/API preview. No broad backend suite or historical E2E cycle was repeated. This review is not exhaustive keyboard/accessibility, crash/endurance, performance or cross-browser certification.

## Try the retained disposable preview

Open **http://127.0.0.1:8000/** while the owned preview remains running.

1. **Inventory:** search `10.40.2.1`, then open a matching prefix. Both its containing parent and child remain available. Close the detail and clear the filters.
2. **Reconciliation:** inspect **Imported-source catalog** and expand **Open a saved calculation run** to inspect saved findings. Import controls expose **Reconcile after this import**.
3. **Capacity:** select the cycle-1 entry in **Saved run** (ID above). Review **Saved-run summary**, occupancy/history and evidence limits. **Export displayed preset (CSV)** uses the saved preset; changing filters alone does not replace that preset.
4. **Requests and exceptions:** inspect current requests, the exception queue and audit history. **Corrections** is the separate independently reviewed inventory-correction workflow.
5. **Synthetic acquisition:** inspect cycle 1 and the disabled automatic schedule. To advance this disposable demo, choose **Rowan** under **Named demo actor**, fill **Run reason**, and use **Run now**. A new saved run is created; return to Capacity, reload the run list and select it.

The preview is owned by the Atlas worker in `/Users/yuganthareshsoni/.codex/worktrees/f234/Ip_inventory`: API PID 64292, terminal session 44304, store `/tmp/ipam-atlas-f234-rich-20260921`, frozen environment `/tmp/ipam-atlas-f234-uv-rich`, compiled assets `frontend/dist`, feed `fixtures/v1`. The old Vite process was stopped; the lead observed only the API listener on 8000. Stop the owned preview with Ctrl-C in its terminal. PID values are historical: inspect ownership before stopping a process later.

For a stopped preview restart, without seeding or rebuilding:

```sh
cd /Users/yuganthareshsoni/.codex/worktrees/f234/Ip_inventory
IPAM_DATA_DIR=/tmp/ipam-atlas-f234-rich-20260921 \
IPAM_STATIC_DIR="$PWD/frontend/dist" \
IPAM_SYNTHETIC_FEED_DIR="$PWD/fixtures/v1" \
/tmp/ipam-atlas-f234-uv-rich/bin/python -m ipam_demo serve --host 127.0.0.1 --port 8000
```

The [fresh setup recipe](atlas-ui.md) creates separate disposable data. Original presenter-ready stores, snapshots and acceptance artifacts were neither replaced nor promoted.

## Preserved limits

All nine easy wins remain accepted. Questionnaire accounting is unchanged at **38 Demonstrated / 17 Partial / 10 Documentary / 46 Missing = 111**. Historical Stage 5 and its addenda remain unchanged. Portable startup/persistence, packaged recovery and recipient proof remain unverified, `PART6_READY=no`. No Docker, image pulls, VM/cloud provisioning, deployment or spending occurred. PR #9 remains OPEN / NO MERGE. Oversight stays PAUSED with the original expiry.
