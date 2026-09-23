# T023 stopped state and recovery evidence

Owner: Muse1.3 high in OpenCode, after reviewed T017A. Lease: only
backend/ipam_demo/state_ops.py and backend/ipam_demo/__main__.py. Astra and
independent Sol challenged this boundary against existing C-O/C-A and whole-SQLite
state operations. Preserve the existing copy, lock, validation, no-clobber,
preserved-old-store and atomic replacement algorithm. No packaging edits or new
HTTP client/server. No execution before T025.

## Snapshot evidence

Existing backup/restore already consumes shared SCHEMA_VERSION and
MIGRATABLE_SCHEMA_VERSIONS, and copies all database tables. Preserve schema7 notice
bindings/receipts, reservation/release history, assessment decisions, durable
ticket attempts/effects/receipts, scoped presets and historical configuration
references without rewriting them. Legacy1..6 stays its actual version until
explicit migration. Unknown schemas fail visibly. Update stale CLI migrate help.

Add a separate JSON manifest at the deterministic path <snapshot>.recovery.json
when a new backup is created. It records format_version=1, snapshot_sha256,
snapshot_bytes, schema_version, captured_at (aware UTC), and configuration:
status=observed or unavailable, revision, digest and policy_revision. The three
configuration values are all present for observed and all null for unavailable.
Observe configuration through existing load_reviewed_configuration using the
separately provisioned IPAM_ACCESS_CONFIG. Do not serialize the configuration,
principals, token digests, source paths, recipient identities or credentials.
This is configuration observed at capture, not proof that every saved row was
created under it. Historical row references remain authoritative for their history.

Bind the manifest to the exact closed standalone snapshot bytes with SHA-256 and
size, not a caller-entered digest. Publish privately with no overwrite and existing
file-safety patterns. Validate both destination paths before publishing. A manifest
failure after snapshot publication must report output_published and
manifest_published accurately, retain the published snapshot, and return failure;
never overwrite/delete it or claim clean backup success. No automatic retry.

## Restore classification

Use the deterministic sidecar for an input snapshot when present; absent sidecar
permits explicit legacy/data-rescue restore with configuration_recovery=unverified.
A supplied/present malformed, unsafe or hash/size/schema-mismatched manifest refuses
before active replacement. Parse exact allowlisted fields and types, reject duplicate
keys, invalid UTC/digests/versions and incoherent null/status combinations. Protect
against the input changing between validation and copying using existing file
identity checks plus input hash revalidation after the SQLite copy. SQLite backup
may change file bytes, so do not require the candidate file to share the input
file hash. Do not classify unrelated bytes from a stale earlier hash.

Compare saved observed revision+digest to freshly loaded current reviewed config.
configuration_recovery is like_for_like only when both are known and equal,
changed_configuration when both known and unequal, otherwise unverified. This
field classifies configuration evidence only; it is never full recovery readiness
or business acceptance. Missing/invalid current configuration does not prevent
rescuing recognized data; mark unverified and require separate readiness. Do not
infer equality from any historical policy/route/assessment reference. Preserve
normal staleness and reauthorization; no global refusal for old historical revisions.

Return sanitized saved/current configuration identities, manifest availability and
classification with existing operation progress fields. Do not copy config, code,
UI, feeds, tokens or secrets into SQLite or treat them as snapshot contents.
Document these output semantics in concise CLI help/result guidance. Keep existing
CLI interfaces and confirmation requirements compatible.

## Remaining gates supplied to the package owner

Result guidance requires authenticated selected-domain GET /api/readiness with
HTTP200 and all six booleans true: process_ready, schema_ready, data_ready,
static_ready, configuration_ready, domain_state_compatible. State commands do not
call the endpoint or manufacture those results. A separate selected-domain
business-state/evidence comparison and actual human signoff are still required.
No task may promote restore success, an equal config digest or six booleans into
portable/human evidence. The user reassigned unstarted operator preparation to agents; see delivery/operator-preparation-ownership.md. Actual T026 human evidence remains separate. T025/T028 unchanged.
