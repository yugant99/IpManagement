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


## T008 lineage encoding and immutable digest — lead decision 2026-09-22

Schema6 is retained. `authority_revision` stores server-built canonical JSON with
exactly `config_digest`, positive-integer `config_revision`, and
`schema: "ipam.authority_revision.v1"`. Serialize sorted keys with compact separators
and UTF-8. Values come from one current reviewed configuration snapshot; never accept
an unverified client composite as authority. Pin policy_revision to that same snapshot.
Mapping revision identifies the reviewed source/scope/domain mapping, not a client
label. Where no separate reviewed mapping version exists, derive its tagged digest
from the sorted source/scope/domain triples in that configuration and use the same
algorithm for current-state comparisons.

The assessment digest is SHA-256 of a version-tagged canonical object containing its
immutable header (identity, source batch/canonical hash, domain, mapping/authority/
policy/baseline revisions, all receipt/classification counts, creator/time and
supersedes lineage), comparison rows sorted by source_record_id, and active-only rows
sorted by matching_key. Include their immutable matching keys, classifications,
reasons and stored candidate/active JSON text verbatim. Exclude mutable state/version,
signer/time/reason, acknowledgement, read-time staleness and row surrogate IDs.
The canonical object tag is `ipam.assessment_digest.v1`; expose `sha256:` plus lowercase
hex. Reject noncanonical/unsupported authority encodings rather than guessing.

Compute the digest after inserting immutable rows within the creation transaction and
anchor it in the existing assessment.create receipt result_json. Recompute on later
reads and compare to that anchor; missing or mismatched anchors fail visibly, without
silent repair. Sign-off must match both expected version and immutable digest, preserve
creator/signer independence, and require all governing revisions and the in-transaction
baseline to remain current. Acknowledgement binds to the exact active-only list through
that digest. Use the existing immediate transaction, conditional update and same-
transaction operation receipt. GET computes staleness without rewriting history.

Reauthorize the current principal, domain and target before any retry disclosure.
Matching-key replay returns the historical operation outcome without signing again;
it must distinguish that outcome from current assessment/sign-off currency. Current
readback reports subsequent staleness even when the original receipt records success.
Changed payload under a reused key is a conflict. No assessment operation promotes
candidate inventory or creates a cutover path.

## Frozen T009/T010 HTTP interface — 2026-09-22

This lead decision follows independent Sol source review. It concretizes the proposed
interfaces above against accepted T008 `776f32a3eaff2be9a5bd9d09a8f5dab62e4f5509`.
Reuse C-A authentication, configuration pins, AppError and immediate write transaction.
No application execution is implied.

- `POST /api/migration-assessments` accepts only source_batch_id,
  expected_baseline_version, idempotency_key, reason, and optional supersedes_id plus
  supersedes_reason. Reject unknown fields and invalid types. Actor/domain and
  mapping/authority/policy revisions are derived from trusted current server context.
- `GET /api/migration-assessments?limit=50&offset=0` returns the existing page fields
  items/total/limit/offset plus current positive baseline_version. Filter by selected
  domain before count and paging. Do not use the fixed workflow pool to obtain this
  version. The shared version pin conveys no foreign inventory counts or identifiers.
- `GET /api/migration-assessments/{id}` returns the T008 summary plus rows and
  active_only. Preserve receipt/comparison count layers, immutable digest, governing
  lineage, saved sign-off and independently computed current/staleness_reasons.
- `POST /api/migration-assessments/{id}/signoff` accepts only expected_version,
  expected_digest, active_only_acknowledged, idempotency_key and reason. Positive
  versions are strict integers, acknowledgement a strict boolean, digest the exact
  tagged SHA-256 shape. All business decisions remain in T008.
- Both POST responses have `{assessment: summary, replayed: boolean,
  original_signoff: object|null}`. Create uses null. Initial and replayed sign-off
  expose the same allowlisted receipt fields: assessment_id, assessment_digest,
  signer_id, signed_at, signed_version. Obtain them from the operation receipt in
  the same transaction. A historical success never overrides current staleness.
- `GET /api/migration-assessments/{id}/export` downloads the same sanitized detail
  as JSON. Authentication and ownership checks precede content/filename creation;
  use a fixed safe filename. No unauthenticated link or token in the URL.

Summary is the T008 projection. At the HTTP boundary, expose created_by/signer_id
only when equal to the current principal, otherwise null. Add
created_by_current_principal and signed_by_current_principal booleans derived before
redaction. Apply this projection to every list/detail/mutation/export/readback
response, including receipt outcomes. Stored identities and the immutable digest
remain unchanged; server-side independence checks use stored identities.

### Exact operation readback

Add only `GET /api/migration-assessments/operation-receipt?action=...&idempotency_key=...`
before the dynamic `/{id}` route. Allow actions assessment.create and
assessment.signoff only; key is a nonempty bounded string of at most 200 characters.
Require current Viewer access and selected domain. Query the existing receipt by
current authenticated principal, selected domain, exact action and key. Never accept
principal/domain from query parameters. Validate target_kind=migration_assessment
and target_id=result.assessment_id, then reauthorize/load the target through T008.
Return only `{found: boolean, action, assessment: detail|null,
original_outcome: object|null}`. The create outcome fields are assessment_id and
assessment_digest; sign-off uses the five allowlisted fields above. No generic
receipt JSON, request digest, foreign totals or other operation data is exposed.
No receipt gives found=false with both nullable fields null; it does not prove that
an earlier request cannot still commit. Corrupt receipts fail visibly and generically.

UI mutations keep the exact payload/key in memory while retrying. Before submission,
retain only a minimal sessionStorage recovery pointer: original principal/domain,
configuration revision/digest, action/key and optional target ID. No token, reason,
candidate JSON or protected response is persisted. Payload and protected views clear
on context change. After reauthentication of the same principal/domain under current
configuration, readback may resolve the pointer even when the revision changed.
Another principal/domain cannot resolve or resend it. Preserve an earlier ambiguous
outcome through a later definite retry refusal. A missing receipt or failed readback
keeps replacement blocked; exact in-memory retry or a confirmed authorized outcome
can resolve it. Storage failures block mutation rather than bypassing recovery.
