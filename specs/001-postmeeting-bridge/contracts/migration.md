# C-M: Immutable migration assessment

Q021–Q032; FR-002/005/014. Reuse POST /api/imports and retained receipt/records. Domain operators submit only wholly
selected-domain intended inventory with reconcile_after_import=false; reject any observation,
mixed/unmapped scope/source or callback=true before persistence; no privileged delegation.
No new parser: versioned canonical JSON only, 10 MiB and 10,000-record bounds preserved.
Only supported intended-inventory groups are compared; unsupported input fails visibly.

## Proposed interfaces
- POST /api/migration-assessments: source batch ID, expected baseline, mapping/authority/
  policy revisions, idempotency key, reason; current operator and domain from C-A.
- GET /api/migration-assessments and /{id}: scoped assessment/current-staleness information.
- POST /api/migration-assessments/{id}/signoff: expected assessment/revision digest,
  active-only acknowledgement, reason and idempotency key; independent approver.
- GET /api/migration-assessments/{id}/export: sanitized same-assessment result.
There is no activate/promote/cutover endpoint. A new local allocation is a separate request.

## Comparison result
Pin a transactionally consistent active snapshot, source hash, mapping and policy revisions.
Retain immutable derived rows with source references, stable matching key, candidate and
active values, disposition and reason. Identity uses scope/family plus existing object key;
normalization reuses canonical parser rules. Changed owner conflicting with a current
approved assignment is conflict, not ordinary replaceable change. Conflicts take precedence.
Input receipt: accepted/rejected/duplicate counts sum to input. Accepted comparison classes:
added/changed/unchanged/conflicting sum to accepted. Active-only rows reported separately,
never deletion proposals. Missing source rows do not establish available addresses.

Intended-inventory staging is all-or-nothing under existing _stage_inventory validation:
invalid or duplicate intended rows reject the whole envelope before any staged receipt.
Successful staged receipts have accepted=input and rejected=duplicate=0. Whole-batch replay
returns the original receipt; it is not a per-row duplicate count. Existing partial/rejected/
duplicate row receipts apply only to coordinator-authorized observation imports, not the
ordinary intended-candidate path. No new partial intended-inventory parser is added.
A coordinator observation receipt with partial rows is not a migration assessment candidate. Sign-off requires zero rejected rows,
explained duplicates, approved mapping, no conflicts, reconciled counts, acknowledged
active-only objects, unchanged baseline and governing revisions. Stale sign-off is retained
but noncurrent. Same source-run ID with changed canonical normalized JSON content conflicts; whitespace/key-order
equivalents replay the original receipt. Raw-byte checksums are provenance only; corrections use new identity
and supersedes/reason lineage. A new mapping is reviewed offline, not edited in a UI.

## Failure and privacy
Tier A retains the global app_meta.baseline_version. Hold-changing and intended-inventory
commits may stale assessments across domains; re-assess before signing. This conservative
invalidation reveals no foreign objects/counts/error details. Evidence imports do not
bump the baseline. T025 sequences a successful assessment before lifecycle writes and
then independently observes staleness; there is no new per-domain version algorithm.

Whole-envelope refusal returns a visible error/request ID, creates no receipt/assessment
or staged records, and leaves active state unchanged. It is not a rejected-row receipt.
The existing import path retains successful staging audit only; request/error logging
does not establish a durable refusal audit. No raw rejected envelope, untrusted ownership
or unrestricted error detail is persisted to scoped audit under this contract.

Scope denial precedes protected record disclosure. Conflict details never reveal another
domain. Abandoning assessment review changes no persisted state; all receipts/assessment history remain. Only coordinator-authorized observation import can reconcile; its commit followed by
reconciliation failure remains visible to that coordinator, never leaked in a domain receipt. A stopped
database restore is disaster recovery, not migration candidate undo.
Future evidence: exact candidate/source hash, all count equations, conflict/partial/stale/
denial cases and active-state invariance, plus actual human recipient acknowledgement where claimed.
