# F1 inventory correction approval

Stage 3 retained worker `01a0b8f0-7036-74d1-81c1-e388d17b4cf4`, under registered Main Lead 2.0. Feature branch `codex/audit-inventory-corrections`; isolated worktree `Ip_inventory-audit-corrections`. Code checkpoint `2de7e67b888f306746eec4808042aa983ddf04fe` follows normal merges of central v5 schema `7dc057c6b18b0b3f0c0425bb17d0b427c4908969` and metadata/comparability dependency `682cd3680fa9d5781b2719249b9532b36ee0f847`, from main `a279f32df0ac7d2147b580dbff36dd88772bdeb2`.

Owned changes: `inventory_commands.py`, `reconciliation.py`, the narrow comparable-evidence guard in `reports.py`, `tests/test_inventory_corrections.py` and this handoff. Stage 4 owns schema/store/seed prerequisite, application routes and frontend. No fixtures, audit source files, customer material, state commands or retained evidence were changed.

## Behavior and interfaces

- `correction_context(connection, run_id, finding_id)` returns the original saved anomalous ghost/unregistered-route finding, current scope/baseline version, actors and limitations. Unsupported findings, mismatched run/finding IDs, different scope/family/perimeter and targets that contain no reviewed discrepancy are refused.
- `create_correction(connection, payload)` accepts exactly actor, idempotency key, scope, CIDR, owner, purpose, reason, expected baseline version and source run/finding IDs. It returns `(record, replay)`. The bounded operation creates a top-level prefix; no parent, original-prefix resize, route policy or external effect is implied. Pending proposals leave inventory unchanged. Reused keys with different payloads conflict.
- `decide_correction(connection, id, {actor_id, action, reason})` requires a different authorized actor. Approval rechecks current ledger, scope, containment and overlaps, then persists the prefix, terminal decision and before/after audit in the caller's single transaction. Rejection leaves inventory unchanged. Exact terminal retries return the recorded outcome without another prefix or success audit.
- `get_correction`/`list_corrections` distinguish the original finding, first subsequent run (`result_run_id`, `result_finding`, `resolution_state`) and newest post-approval run (`latest_run_id`, `latest_finding`, `latest_resolution_state`). The first result remains historical even when later corrections resolve the perimeter. A missing or incomparable newest finding is unknown; it never falls back to an older healthy result.
- `create_run` links the first subsequent run after insertion in the same transaction. Resolution requires a comparable healthy finding: same rule/version and scoped subject identity/geometry. Approval is not resolution. Saved runs and the original source finding remain unchanged. The same comparability guard prevents run comparison from resolving an old anomaly against changed rule/subject geometry.

Current API wiring is supplied by Stage 4: correction-context, paginated correction-requests, per-request detail/decision, followed by the ordinary saved-run endpoint. No special reconciliation endpoint or scheduler is added here.

## Focused observed evidence

The user explicitly authorized focused local tests, builds and disposable local rehearsal for F1–F7. Five stdlib unittest cases passed against fresh temporary rich stores using actual import/feed/scheduler/reconciliation/inventory service functions, in 20.899 seconds. After adding the report comparability guard, the affected newest-result test passed again in 1.494 seconds. Tests used the existing local Python environment with `PYTHONPATH=backend:fixtures/evolving`; no dependency installation, retained-store mutation or fixture regeneration occurred.

1. Pending proposal leaves 60 prefixes; independent approval adds one; creation/decision retry preserves one prefix and one successful approval audit; same-clock rerun resolves the complete ghost finding. New prefix route policy remains unknown; scheduled advancement remains eligible afterward. Original saved JSON remains byte-identical.
2. Rejection and retry leave inventory/version unchanged. Unauthorized/self approval, changed idempotent payload, stale review, scope/perimeter mismatch, unrelated target and overlapping root are refused.
3. Injected success-audit refusal rolls back prefix, ledger and decision together; a later valid attempt succeeds. This exercises the service transaction boundary; HTTP failure-audit behavior belongs to Stage 4's check.
4. At real feed cycle 6, current ghost addresses are `.240.10` and `.243.10`. Registering only `.240/24` leaves `.243.10` anomalous. A separately reviewed `.243/24` correction yields healthy; the first partial result remains retained. Cycle 7 is unknown because Central is stale; cycle 8 is healthy again. Original geometry and feed assets remain untouched.
5. A newly saved run omitting the comparable finding, or changing its rule version, yields current unknown despite an earlier healthy result. Run comparison also refuses false resolution for changed definitions.

These are bounded local service checks, not browser, recipient or production acceptance. Later integration may add owner checks; historical Stage 5 remains 14 passes/two partial within its original scope. Questionnaire classifications and scenario catalog completion remain lead-owned.

## Next owner

Stage 4 combines exact backend features with the agreed API/UI, then Stage 5 rehearses the final candidate once. The lead owns review and main integration. Keep the source-first/result/latest distinctions visible and preserve the Central cycle plan; no blanket perimeter resolution is inferred from approving one proposal. F4/F6/F7, native demo recovery and portable recipient gates are outside this backend slice.
