# F1–F7 implementation contract

Lead-approved under the [audit-response authorization](handoffs/audit-response-authorization.md), agreed directly with Stage 3 and Stage 4 after reading existing callers. This specifies implementation, not runtime acceptance. Existing contracts continue except where changed here. Original fixture bytes and geometry remain frozen.

## Schema ownership

Stage 4 alone authors explicit schema v5 and `store.py`; Foundation retains CLI/state compatibility. Stage 3 owns backend behavior; Stage 4 owns app endpoints and frontend integration. Startup never migrates automatically. V5 adds one correction table, a pool history token and additive exception fields. Preserve existing runs, evidence, allocations, audits and scheduling. New preservation checks enumerate actual tables/columns instead of freezing the historical count of 15.

## F1: top-level registration

Support one new top-level intended prefix inside an existing managed perimeter, justified by an anomalous saved `ghost_scope` or `unregistered_managed_route` finding. It must contain at least one concrete source discrepancy. Do not widen original prefixes, alter observations, infer route policy or perform external remediation. Keep direct child editing and allocation approval.

`correction_requests` stores `id`, `actor_id`, `idempotency_key`, `payload_hash`, `payload_json`, `scope_id`, `source_run_id`, `source_finding_id`, reviewed `baseline_version`, `state` (pending/approved/rejected), nullable `prefix_id`, `created_at`, nullable `decided_at`, `decision_actor_id`, `decision_hash`, `decision_reason`, `approved_baseline_version`, `result_run_id`. Actor/key is unique; scope/source/result-run/prefix references use foreign keys. Source finding remains pinned inside its immutable run. Before/after audits link the request.

| Interface | Contract |
|---|---|
| `GET /api/correction-context?run_id=…&finding_id=…` | Original run/finding, current scope/baseline, actors, synthetic flag, limitations; reject unsupported/non-anomalous finding |
| `GET /api/correction-requests` and `GET /api/correction-requests/{id}` | Request/decision, payload, original finding, linked result and resolution state |
| `POST /api/correction-requests` | Exactly `actor_id`, `idempotency_key`, `scope_id`, `cidr`, nonblank `owner`, `purpose`, `reason`, `expected_baseline_version`, `source_run_id`, `source_finding_id`; top-level only, empty new tags/custom fields |
| `POST /api/correction-requests/{id}/decision` | `actor_id`, action approve/reject, reason; authorized independent actor |
| Existing ordinary/scheduled reconciliation | Calculate from actual stored inventory/evidence and link outcome; no second reconciliation engine |

Stage 3 supplies inventory-command helpers `correction_context`, `list_corrections`, `get_correction`, `create_correction`, `decide_correction`; mutating create/decision return result plus replay flag. Reuse the API's immediate transaction and failure-audit wrapper. Pending/rejected requests leave inventory unchanged. Approval rechecks reviewed version, scope/family, perimeter containment and overlap; exact prefix, decision and successful audit commit atomically. Terminal requests are immutable and retries cannot duplicate effects.

Link the first saved run after approval whose ledger version is at least the approved version. Evaluate its finding for comparability; a missing or incomparable finding yields unknown. This retained first result is historical, not a guarantee of health. Show original, first-result and latest inspection distinctly. Current resolution uses the newest post-approval run: missing or incomparable latest evidence is unknown, without falling back to an older healthy match. A subset correction can leave the perimeter anomalous. Only healthy comparable evidence earns `resolved_by_evidence`; other states include not approved, pending reconciliation, still anomalous and resolution unknown. New prefixes without policy retain unknown missing-route results. Feed compatibility stays enforced.

Central's managed perimeter is `10.80.0.0/16`, original root `10.80.0.0/20`. Persistent ghost `10.80.240.10` needs registration; cycle 6 adds `10.80.243.10`, with both active. New top-level `.240.0/24` and `.243.0/24` cover these chosen subnet demonstrations without widening original space. Persistent route `.241.0/24` is separate; register it only when demonstrating that correction. Cycle 7 Central evidence is stale, so never claim a healthy absence result there. All addresses in the chosen cycle must be accounted for.

## F2: metadata evidence

One `metadata_gap` per intended prefix: missing/blank owner or purpose is an explained warning; both present is healthy. Save evaluated metadata, prefix/ledger versions and original/current audit provenance. Never invent values or read fixture expected answers for detection. Audited correction plus a new run resolves the gap through existing comparison; old runs stay unchanged. Untouched rich baseline adds 60 findings to the former 113 (one Lab gap/59 controls); observe new totals without rewriting old evidence.

## F3: history and concurrency

Keep existing prefix/pool/baseline concurrency bumps. Add `pools.capacity_history_version`, positive integer default 1, for historical eligibility. Metadata-only owner/purpose/tags/custom-field edits leave it unchanged. Supported child creation or bounds changes bump affected own/ancestor pools, conservatively withholding unsupported historical p95/forecast. Top-level creation affects no unrelated pool.

Migration sets 1 only if legacy pool version and attached prefix version are both 1, otherwise 2. It does not reconstruct previously invalidated history or fabricate a geometry timeline. All freshness/completeness/calculation gates remain.

`edit_context.history_impact` supplies `metadata: []` and `structural: [{pool_id,name,cidr}]`. UI warnings identify affected pools, including ancestors, for supported structural actions. Do not claim current occupancy necessarily disappears, positive leases stop disproving the zombie conjunction, or saved runs are erased. Metadata edits do not display structural-history warnings.

## F5: evidence and exception lifecycle

Keep case key `[rule_id,scope_id,family,subject_id]` and original `run_id`/`finding_id`. Add nullable `latest_run_id`/`latest_finding_id`, `last_definitive_state` (anomalous/healthy, default anomalous), nullable `material_keys_json`, positive `notification_version` default 1, `notification_reason` default initial, positive `episode_count` default 1, nullable `closed_at` and `last_action_hash`. Retain operational disposition open/acknowledged/escalated; closure and calculated evidence are separate.

Migration leaves latest evidence null: explicitly not refreshed/unknown until a new run. First sync derives original material keys from a null sentinel without inventing historical notifications or notifying again merely for unchanged original evidence.

| Event | Policy |
|---|---|
| New anomalous subject | Open case, original/latest evidence and first notice |
| Healthy comparable result | Evidence resolves; preserve original and operational history; no external-remediation claim |
| Missing/unknown/not-applicable/incomparable | Resolution unknown; never healthy by absence |
| Owner close | Latest healthy comparable evidence, current version and reason required |
| Owner reopen | Explicit version/reason action; no invented anomalous evidence |
| Anomaly after definitive healthy | New episode, reopen, renew notice and clear acknowledgement; retain owner/handoff/escalation history |
| New material member during unresolved episode | Renew notice once; union notified members through partial/unknown views |
| Unchanged anomaly or subset/removal | Update evidence without duplicate notice |

Comparable identity retains rule version and subject scope/family/kind/CIDR; do not require equal ledger/metadata versions across a legitimate correction. Stable material keys normalize ghost address, route CIDR, conflict address plus sorted client pair, pool mismatch address/client, missing metadata field, or rule condition/policy branch. Preserve opaque principal strings. Generated IDs, ordinary timestamps/renewal windows, output order, wording and numeric jitter alone do not create incidents. Healthy ends an unresolved episode. Repeated sync of the same run is inert.

API retains old `finding` alias and adds explicit original/latest finding, latest evidence state, resolution, lifecycle and notification fields. Pending notice accounts for current healthy evidence and closure, not acknowledgement alone. Every new run increments the exception version to prevent stale closure. Immediate exact action replay requires matching canonical payload hash (including actor) and current version equal to submitted version plus one; intervening sync/action requires refreshed review. Recognize an exact successful handoff replay by its original actor before current-owner mutation permission, because the successful handoff itself changed ownership; a different payload or actor cannot mutate without current ownership. Successful actions stay audited and owner-restricted.

## Integration and acceptance

Publish schema first for Stage 3/Foundation pickup; integrate owned slices preserving coherent commits; check changed contracts and migration/state preservation; independently review and repair the connected candidate. Stage 5 receives one exact reviewed candidate for focused final rehearsal and dedicated state/runbook, reusing sufficient owner checks. New missing-case observations stay separate from historical Stage 5. Lead updates F6/F7 from observed evidence, preserving the separate 15/16/111 denominators and portable/customer-phase gaps.
