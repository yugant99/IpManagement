# Phase 3 UI browser validation

Date: 2026-09-25 UTC. Candidate: `codex/part-4-ui-inventory-shell`, isolated worktree and port 18852. The app used a disposable copy of the synthetic SQLite store and access config; the existing demo server on port 18841 was not changed. The browser used the existing synthetic core-domain access token only to enter `demo-core`. Spencer's login/OIDC work was outside this pass.

## Presenter journey observed

- Sources landing: 12 mechanisms in three planes; three carry synthetic evidence and nine say not connected. The sample EMS is labeled `Cable EMS Lab DEMO-1.0`, with no live endpoint/read. Per-scope disclosure and capability status remained accessible.
- Inventory: selecting `North · vrf-north` returned 15 intended prefixes. Opening `10.40.0.0/16` showed owner, purpose, scope and source references. The inventory view did not infer a live observed state.
- Reconciliation: opened saved domain run `3c2215d5-56ae-48ff-9739-5841d4dfc76a`, filtered to eight anomalous findings, then opened the Coastal `10.60.4.0/24` missing-route finding. Its policy, source coverage, validity interval, limitations and raw-record action were present.
- Capacity: selected the same saved run and saw six saved DHCP pool calculations, separate from current static IPv4 occupancy. The table showed capacity, lease occupancy, 30-day p95 and forecast. Missing DHCP calculations for the North static pool showed their reason in the overview after the review fix.
- Acquisition: the first isolated schedule attempt returned `SYNTHETIC_FEED_UNAVAILABLE` because the test process lacked `IPAM_SYNTHETIC_FEED_DIR`. After restarting with the pinned `fixtures/v1` path, cycles 3 and 4 succeeded, creating runs `5281e0eb-c4c5-43ed-99de-7003d58a4fcd` and `67c59de4-f032-419f-b53f-83f394f062c5`. While Sources remained open, its 15-second poll displayed the cycle-4 run and demo clock `2026-09-02T00:00:00Z` without a page refresh.
- Reconciliation's **Reload runs** exposed the new cycle-4 run with nine anomalies, up from eight. Filtering North plus Anomalous showed `10.40.1.0/24` as a missing expected route. Capacity's saved-run comparison marked that same finding healthy → anomalous, **new anomaly**.
- At 390px, Sources, Inventory, Reconciliation and Capacity navigation worked with no document-level horizontal overflow. Sources cards reflowed into one column. At 980px, the Sources grid also had no document-level horizontal overflow. The compact navigation remains horizontally scrollable to reach later views.

## Checks and limits

`npm run build` passed with the bundled Node 24 runtime after the UI and review fixes. The only console error during the earlier browser pass was a missing favicon. After declaring the local Dodona image as favicon and rebuilding, a final browser reload reported zero console errors or warnings. Browser evidence is local synthetic evidence, not Rogers connectivity, production portability or Spencer's sign-in validation. The local test server/store and Playwright session can be discarded after the final check.
