# Stage 3 evidence and shared calculation lane

**READY FOR PROJECT-LEAD REVIEW — Stage 3. Source implemented; runtime evidence pending.**

Owner: Stage 3 subagent `/root/evidence_calculations`. This is a bounded worker report, not global stage acceptance. Worktree: `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-3-evidence`. Repository: `yugant99/IpManagement`. Branch: `codex/stage-3-evidence-calculations`. Owned paths: `backend/ipam_demo/imports.py`, `evidence.py`, `calculations.py`, `rules.py`, `reconciliation.py`, and this report.

Code checkpoint: `bbe4a3bf811488f49ea9159b28c96d2f1a7bfd81`. The later report commit publishes this checkpoint; inspect the branch head for the report's own SHA. Integration base is `5578431` (the coordinator's exact accepted PR #8 + PR #7 + current main documentation integration). This lane depends on the coordinator's schema v3 migration adding `dhcp` and `inventory_staged` to the existing source-kind constraint; it does not modify schema/store/app/seed/UI, fixtures, state commands or packaging. Core seed `_validate(envelope)` and `_ranges(values, network)` signatures are reused.

## Implemented source behavior

- Typed DHCP uses the existing bounded JSON import, immutable envelope/raw rows, canonical replay identity, rejection accounting and scope completeness rules. Original lease bounds and observation time are preserved, normalized values use explicit timezone/millisecond precision, ends remain half-open, and future ends remain valid. DHCP source authority is `observed`, requirement `dhcp_history`. Source metadata is now present in new observation/policy receipts as well as original envelopes.
- Baseline-shaped intended-inventory uploads call the seed validator and remain `inventory_staged`, with `application_status: staged`. Raw rows are retained with their collection identity; no intended rows, allocations, versions or active source coverage are changed. Invalid candidate envelopes return a visible 422 rather than partly promoting inventory. The fixed demo clock must match the initialized ledger. Fresh rich setup remains the coordinator's explicit seed helper, not this importer.
- `evidence.selected_views(connection)` selects newest ingestion per source and declared scope, including partial replacements. Staged candidates do not participate. Multiple sources for a scope are unknown authority in rules/calculations. Clock equal to coverage end is a current assertion cutoff, not lease/route expiry.
- `evidence.active_dhcp_claims(connection, scope_id, family, address, clock_text)` returns `{claims, unknown_reasons}` inside the caller's transaction. Fresh positive current claims include typed lease plus `input_reference`; all latest sources contribute conservative positive blocking claims even when authority is ambiguous. Missing/stale/partial/ambiguous evidence is reported separately. DHCP silence never proves an address available; the local static ledger remains allocation authority. The workflow lane accepted this interface directly.
- `calculations.calculate_pools(connection, views, clock_text)` computes occupancy/history/forecast once before rule evaluation. Assignable capacity is interval arithmetic after exclusions; occupancy deduplicates active addresses. Complete 30-day p95 requires exactly 720 eligible hourly samples and nearest-rank selection. Daily OLS uses 14–30 consecutive complete UTC days, 24 samples each, through the last completed day. Current occupancy, latest daily baseline and slope are saved separately. Forecast includes unavailable, exhausted, no-positive-growth, available and beyond-one-year states; distant estimates retain numeric basis without a invented calendar date.
- `reconciliation.create_run` persists one run with existing G13 logic plus pool pressure, oversized, zombie candidate, managed ghost DHCP usage, unregistered managed announcement, concurrent DHCP client conflict and the contract-required out-of-range pool assignment discrepancy. Pressure consumes the shared metric and uses three-valued `p95 >= 80 OR forecast < 60`; oversized is complete p95 below 50. Positive observations can support anomalies in partial batches; absence cannot. Zero leases requires a complete interval, not merely zero sampled occupancy. No rule reads expected-outcomes labels.
- Pool out-of-range/excluded current claims remain `out_of_range_observations` and an explained `pool_assignment_discrepancy`; they never alter capacity. Candidate-space totals union assignable IPv4 intervals per scope from oversized/zombie candidates. They are addresses in candidate pools, with `released_addresses: "0"`, not recovered-space claims.

## Saved result contract

Existing saved runs remain immutable. New run `rule_id` is `pool_watch`; `rule_ids` lists actual evaluated rule IDs. Existing finding fields remain. Pool subjects add `kind: pool`, `pool_id` and `prefix_id`; all required `id/scope_id/scope_name/family/cidr/version/origin` fields remain. Managed-perimeter findings use deterministic UUIDv5 identity over scope and CIDR, with `kind: managed_perimeter`; their `observations` array carries actual discrepancies and row references. Stable perimeter subjects keep healthy/unknown controls available after source replacement rather than disappearing with a random source-record UUID. G13 remains `missing_expected_route`, version 1.

New `run.calculations` entries contain pool/prefix/scope identity, name, family, CIDR, management mode, pool version, decimal-string capacity, selected coverage/references and:

- `current`: status, fixed-clock `at`, decimal-string-or-null occupied addresses, utilization percentage, accepted-positive address lower bound and optional reason.
- `p95`: status, occupied addresses, utilization percentage, eligible/required samples, 30-day window, `sample_interval_seconds: 3600`, method and optional reason.
- `forecast`: status, days to full, estimated full timestamp or null, slope, baseline, complete-day count, saved `daily_p95`, method and optional reason.
- `history`: hourly timestamps with decimal-string counts or explicit nulls; missing samples are not zero-filled.
- `lease_overlap_30d`: positive overlap true, complete zero false, insufficient absence evidence null; `out_of_range_observations`; limitations.

New `run.candidate_space` contains `by_scope` with decimal-string union totals and inclusive intervals, `released_addresses`, and the caveat label. Read dashboard/detail/export from this saved object rather than recomputing independently.

## Bounded decisions and limitations

The coordinator approved schema kinds and conservative historical invalidation on `pool_version > 1`; prefix version changes also invalidate history. This means even metadata-only edits can make p95/forecast unavailable until explicit reset/reseed. No fabricated historical capacity timeline or automatic revalidation is provided. Current positive claims remain visible.

Missing/partial/stale/ambiguous sources produce unknown where necessary. A positive lease makes zombie's zero-use conjunction false even when absence coverage is incomplete. An exact active route can establish zombie presence; missing/incomplete/ambiguous selected matching policy cannot manufacture covering-route permission or healthy absence. G13 continues to require its explicit complete policy snapshot.

Conflict detection compares distinct DHCP `client_id` values for the same scope/family/address over covered history and the current snapshot. Sequential leases and cross-scope reuse do not conflict. Inventory owner text is not a principal-equivalence mapping; the detector does not invent a DHCP-client/owner join. The local workflow separately blocks current positive DHCP claims. Managed perimeter subjects aggregate discrepancies; no per-address exception lifecycle is added.

All source data is synthetic. Hourly occupancy and this simple forecast are illustrative, not traffic measurement or calibrated production planning. No network discovery, actual DHCP/router write, release/reclaim execution, live integration or deployment is claimed. Staged import validation is whole-envelope validation using the existing seed contract; invalid candidate inventories do not receive a partial promotion workflow.

## Evidence and handoff

Questionnaire contributions: RFP-033/034/037/061/062/063/064/065/066/069/073/074/075/076/087/089, with supporting source/rule contributions to 029/054/085 and the coordinator's detail/history/UI rows. Work references G05–G07/G09–G15/G17. These are source implementations, not demonstrated row credit; the denominator remains 111.

Actually observed: source files/contracts/fixture generator recipes read; isolated branch/worktree created; coherent commits recorded and pushed in groups of three or before handoff. No tests, test additions, smoke checks, builds, type checks, generator execution, app/API/browser runtime, dependency operations or infrastructure commands were run. No runtime import, calculation, persistence or UI output has been observed. Fixtures and expected-outcomes JSON were not modified or used as detector input.

Next owner: Stage 3 coordinator for bounded independent source review, schema/seed/API/UI/report integration and normal merge preserving commits on the isolated integration branch. Persistent project lead retains main merge and acceptance authority. No main merge or global status update occurred in this lane.

Draft next prompt: Review the Stage 3 evidence lane at `bbe4a3bf811488f49ea9159b28c96d2f1a7bfd81` and its publishing report on `codex/stage-3-evidence-calculations`. Read this report, `imports.py`, `evidence.py`, `calculations.py`, `rules.py` and the bounded changes in `reconciliation.py`. Confirm schema v3 kinds, seed validator compatibility, workflow active-claim calls and saved run/UI/report fields by source inspection. Route concrete defects back to this lane; preserve the no-runtime/no-tests constraint. Integrate the coherent commits only into the coordinator's Stage 3 branch after bounded review, then report exact candidate and still-pending acceptance evidence to the persistent project lead.
