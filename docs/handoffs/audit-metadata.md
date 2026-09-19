# Audit follow-up: F2 metadata and F5 rule identity

Owner: Stage 3 rules subagent `/root/evidence_calculations`. Branch: `codex/audit-metadata-rules`; isolated worktree `/Users/yuganthareshsoni/Downloads/Ip_inventory-audit-rules`; integration base `a279f32df0ac7d2147b580dbff36dd88772bdeb2`. Owned paths are `backend/ipam_demo/rules.py`, `tests/test_metadata_gap.py` and this report. Main Lead 2.0 remains the lead; Stage 4 alone owns shared schema/store/app/frontend. No shared-file mutation, fixture change, retained-store modification or historical evidence rewrite occurred.

F2 implementation: `5f67e459db4a5c399bc2c856804272d3ad72e1e2`. Shared rule-identity helpers and focused checks: `096076cb7e9663f761ed7dcaf719c8f92e9160b7`. This later documentation commit publishes those exact code checkpoints. The coordinator records the reviewed/integrated candidate; these commits do not independently establish global audit closure.

## F2: actionable missing metadata

Each intended prefix now produces a `metadata_gap` finding, rule version 1 and warning severity. Blank or whitespace-only owner/purpose is anomalous; both nonblank is healthy. The rule inspects current intended state and does not depend on DHCP/routing completeness. It neither invents missing values nor treats nonblank text as proof of correctness.

The saved subject retains its prefix ID/scope/family/CIDR/version and original origin. `policy` stores required fields, missing fields, exact evaluated owner/purpose, evaluated prefix and ledger versions, current-intended evaluation authority, and a matching successful local metadata audit when available. References label creation provenance `original_inventory` and later local evidence `inventory_audit`. The audit lookup requires the actual prefix ID and matching owner/purpose values in the recorded after snapshot; no new metadata is falsely attributed to the original seed. The finding directs the presenter to the existing audited editor and a subsequent reconciliation.

Observed focused result on a fresh rich temporary store: **173 total findings**, including **60 metadata findings: one Lab `10.40.15.0/24` anomaly and 59 healthy controls**. The prior 113-finding rich shape gains one per prefix. The count formula is now two findings per prefix plus four per pool plus three per managed perimeter; a later supported prefix adds metadata and missing-route evaluations. Historical Stage 5's observed 113-row exports and its later populated-state counts remain historical evidence and were not changed.

An authorized audited owner/purpose edit followed by the actual reconciler was observed to make the metadata finding healthy, link its matching audit, and produce `resolved_by_evidence` in the existing comparison. The prior saved run JSON remained byte-for-byte unchanged. A purpose still blank after a partial edit remained anomalous. F2's new exception was observed through the existing queue creation path; F5 lifecycle extensions are separately owned and not claimed complete here.

## Shared F5 identity contract

`rules.discrepancy_keys(finding) -> list[str]` returns sorted, deduplicated canonical JSON atoms for an anomalous finding, or an empty list for healthy/unknown/not-applicable findings. It does not change the existing case key `JSON([rule_id,scope_id,family,subject.id])`, calculate notification state, or rewrite a saved finding. Each atom includes rule and canonical subject CIDR, plus:

| Rule | Material positive identity |
|---|---|
| `ghost_scope` | Canonical observed address |
| `unregistered_managed_route` | Canonical observed CIDR |
| `assignment_conflict` | Address and sorted distinct incompatible client IDs |
| `pool_assignment_discrepancy` | Address and DHCP client ID |
| `metadata_gap` | Missing field name |
| `pool_pressure` | Each known-true pressure branch and its fixed threshold |
| `oversized_pool` | Fixed p95 threshold and required sample count |
| `zombie_candidate` | Zero-lease-day condition and applicable route matching policy |
| `missing_expected_route` | Applicable route matching policy |

Run/finding/generated record IDs, renewal intervals, source-cycle IDs, provenance timestamps, observation ordering/duplicates, metadata/concurrency versions and numeric utilization jitter are excluded. Different scoped subjects remain separate cases. Unknown new rule IDs fail visibly until an identity is defined. All existing rules and the new metadata rule are covered.

The centrally agreed workflow policy retains a union of known positive keys through an unresolved episode. A newly observed key can renew notification; omitted keys under partial evidence do not erase prior knowledge. Healthy comparable evidence ends an episode; a later anomaly is a recurrence. Workflow owns these transitions and their schema/audit, not this pure helper.

`rules.comparable_findings(before, after) -> bool` checks that both findings exist and agree on rule ID/version and subject ID/scope/family/CIDR/kind. Absent `kind` defaults to `prefix` for old prefix findings. It ignores global ledger and subject concurrency versions so an audited metadata correction can resolve. This helper establishes identity/definition compatibility only: callers must separately require healthy evidence to resolve; missing/unknown/not-applicable evidence never resolves a case.

## Focused verification actually performed

Under the explicit local-test authorization, the following command ran against this worktree's modules, using the existing accepted Python environment and fresh `TemporaryDirectory` synthetic stores:

```sh
PYTHONPATH=/Users/yuganthareshsoni/Downloads/Ip_inventory-audit-rules/backend:/Users/yuganthareshsoni/Downloads/Ip_inventory-audit-rules/fixtures/evolving /Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-artifacts/run-20260919-O8RVgx/environment/bin/python -m unittest discover -s tests -p test_metadata_gap.py -v
```

Final result: **6 tests passed**. Three exercise actual seed/reconcile/edit/audit/compare/old-run preservation behavior; three exercise identity invariance, material additions and compatibility refusal across all current rules. The initial test harness incorrectly treated the store connection context manager as a direct SQLite connection; that harness setup was corrected before the successful runs. No application failure was observed in these focused cases.

No browser/build/scheduler/rehearsal/infrastructure commands were run in this lane. Existing stores, acceptance artifacts, source fixture bytes and private audit/customer material were preserved. Integration with F1 approval, F3 geometry/history changes, F5 close/reopen state, Stage 4 UI and the final local rehearsal remains for the respective owners and integrated acceptance.

Next owner: coordinator for bounded source review and integration; workflow worker consumes both helpers; Stage 4 renders the saved policy/provenance and updates current count expectations without altering historical records. Candidate questionnaire contributions include 037/063/069/071/072/082, but requirement classification and catalog-scenario closure require lead adjudication against the complete integrated evidence. Keep 15 catalog scenarios, 16 historical acceptance cases and 111 questionnaire rows separate.
