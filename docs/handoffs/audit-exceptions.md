# F5 exception lifecycle handoff

Status: READY FOR PROJECT-LEAD REVIEW — audit follow-up F5. This is a backend
lane result; integrated API/UI acceptance remains with the shared integration
owner and Main Lead 2.0.

## Source and ownership

- Worktree: `/Users/yuganthareshsoni/Downloads/Ip_inventory-audit-exceptions`.
- Branch: `codex/audit-exception-lifecycle`, based on
  `a279f32df0ac7d2147b580dbff36dd88772bdeb2`.
- Owned files: `backend/ipam_demo/workflow.py`,
  `tests/test_exception_lifecycle.py`, and this handoff.
- Service commit: `e34b3b4f8a9f16ea8a28333bc894b049bb82cc00`.
- Focused test commit: `646dd63`.
- Exact centrally owned schema dependency merged:
  `7dc057c6b18b0b3f0c0425bb17d0b427c4908969`.
- Exact rules dependency head merged:
  `682cd3680fa9d5781b2719249b9532b36ee0f847`, including helper commit
  `096076cb7e9663f761ed7dcaf719c8f92e9160b7`.
- PR target: `codex/audit-shared-integration`. Schema, store, routes, and frontend
  changes belong to the central Stage 4 owner; their merged dependency files
  were not authored in this lane.

## Implemented behavior

The original `run_id`, `finding_id`, and `finding` remain the initial anomaly.
`original_finding` is an explicit alias. Each new saved reconciliation updates
`latest_run_id`, `latest_finding_id`, and `latest_finding` independently. Reusing
the current run or replaying an older saved run does not alter case state.

`latest_comparable` uses the shared rule/version and subject identity/geometry
guard. Only a comparable healthy result establishes `evidence_resolution:
resolved`. Comparable anomalies are `active`; unknown, not-applicable, missing,
incomparable, or not-yet-refreshed migrated evidence is `unknown`. A prior
healthy result does not make a later unknown result look resolved.

Evidence resolution does not silently close an owned case. Its owner can
explicitly `close` after current comparable healthy evidence, or `reopen` a
closed case. `lifecycle_state` is `open|closed`, separate from the retained
operational `state` (`open|acknowledged|escalated`). Closed cases reject other
operations with `EXCEPTION_CLOSED` until reopened. Closing without resolution
fails visibly with `RESOLUTION_NOT_ESTABLISHED`.

Known semantic discrepancy keys accumulate within an unresolved episode.
Repeated observations, changing generated IDs, reordered/duplicated inputs,
and temporarily omitted known discrepancies do not create new notifications.
New semantic keys do; a comparable anomaly after a definitive healthy result
starts a new episode. Both clear acknowledgment and reopen a closed case while
retaining owner, handoff, and escalation. Incomparable evidence cannot establish
resolution or manufacture a material-change notification.

The response exposes `notification_version`, `notification_reason`,
`episode_count`, and `material_keys`. Notification reasons are `initial`,
`new_discrepancy`, `recurrence`, `handoff`, or `owner_reopen`. A closed case or a
current comparable healthy result has no pending notification. Migrated cases
with null latest pointers visibly say they have not been refreshed; the first
real sync derives their original semantic baseline without inventing a second
initial notice. A genuinely new discrepancy on that first sync still notifies.

An immediate exact action retry succeeds only when the current version is the
submitted version plus one and the canonical actor/action/reason/version/
recipient payload hash matches the immediately preceding successful action.
This check follows actor authorization and precedes the current-owner check,
so the original owner can safely retry a handoff. An intervening evidence sync
or action makes the retry stale. Action responses include `replay`. Successful
state changes and audits use the caller's transaction and roll back together.

## Observed validation

Eight focused standard-library unittest scenarios passed in 0.301 seconds:

1. Resolution, explicit close/reopen, unknown/missing evidence, and recurrence
   preserve original evidence, ownership, handoff, and escalation.
2. New semantic discrepancies notify once; partial omission does not forget
   previously known discrepancies.
3. Unknown, missing, not-applicable, and incompatible rule/geometry evidence
   cannot establish resolution.
4. Immediate exact handoff retry by the former owner succeeds without another
   audit; changed payloads and intervening sync/actions are stale.
5. Same-run and historical replay cannot reapply evidence or regress the case.
6. A simulated migrated null sentinel does not fabricate an initial notice.
7. Audit refusal rolls back both an owner action and an evidence transition.
8. An actual inventory metadata correction followed by actual reconciliation
   makes the latest metadata-gap evidence healthy without rewriting the first
   finding or saved run.

Command, run from this worktree:

```sh
PYTHONPATH=/Users/yuganthareshsoni/Downloads/Ip_inventory-audit-exceptions/backend:/Users/yuganthareshsoni/Downloads/Ip_inventory-audit-exceptions/fixtures/evolving /Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-artifacts/run-20260919-O8RVgx/environment/bin/python -m unittest discover -s tests -p test_exception_lifecycle.py -v
```

Every test created a fresh synthetic store in a temporary directory. The
existing Python environment was used as a runtime only. Retained Stage 5
stores, fixtures, and evidence were not modified. Seven cases use saved
controlled findings to isolate lifecycle behavior; the eighth uses the actual
metadata edit and rule evaluator. The migration sentinel case is not a full
upgrade test of an old database; central migration coverage belongs to the
schema owner. No frontend build, browser run, cloud, VM, or container operation
was performed in this lane.

## Integration handoff

The Stage 4 owner received the additive API fields/enums and closed-case policy
directly. Merge through `codex/audit-shared-integration`, review the focused
tests with the F1/F3 collection, and validate the connected API/UI lifecycle
before claiming global F5 acceptance. Keep notification and evidence labels
separate in the interface; acknowledgment and explicit closure do not rewrite
historical evidence.

Draft next prompt: Review the exact F5 PR head and its schema/rules dependencies,
merge it into the audit integration collection, then exercise the original
finding to current resolution to explicit close to recurrence flow together
with stale retries on disposable synthetic stores. Report connected validation
separately from this lane's observed unit results.
