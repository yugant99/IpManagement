# Validation and handoff criteria — observations recorded separately

This guide defines the required observations; its example commands are not evidence or
permission to execute them. T025 is in progress under the user's scoped native disposable
synthetic authorization. Actual candidate-bound results belong in
`delivery/independent-evidence.md`, not in this checklist. T025 has not yet passed.
Package/recipient execution and human contact retain their separate authorization gates.

## Prerequisites and candidate
Main Lead records implementation/validation authorization, exact candidate SHA and the declared
disposable synthetic technical target. A separately pinned native local T025 target is permitted;
the unavailable recipient Linux amd64 target remains a separate portable/human evidence gate.
Pin UI/feed assets, schema/config revision, fixture hash and isolated data directory/volume;
record an image digest only if an image was actually built under applicable authority.
Native execution uses application Python3.12 and the committed dependency locks. The future
Linux amd64 package target requires Docker Engine>=24 with the Compose plugin (record the
actual version), Bash/curl/Python3.11+ host tooling. No dependency upgrades.
Use an explicitly isolated disposable synthetic store; changing Compose project alone is
insufficient because the current volume name is global. Never point recovery exercises at
the user's live store. Provision separate requester/operator and independent approver tokens
via the reviewed offline procedure; no token content in evidence or command history.

## Packaged operator command sequence (only on an authorized declared package target)
This package sequence does not authorize Docker or provision a recipient target. For the
reviewed wrapper interface and recovery policy, read `delivery/operator-handoff.md`,
`scripts/ops/README.md` and `docs/RUNNING.md`. Set explicit `IPAM_DATA_VOLUME` and
`IPAM_ACCESS_CONFIG` first; provision protected token files separately. Never use the
user's existing data volume. Native local T025 records its own exact commands in evidence.

```sh
scripts/ops/build.sh
scripts/ops/seed.sh --scenario rich
scripts/ops/start.sh
scripts/ops/health.sh --readiness --token-file /protected/operator.token --domain demo-core
scripts/ops/acquire.sh --token-file /protected/coordinator.token --key bridge-initial-acquisition --reason "Initial synthetic T025 acquisition"
```

The T024 wrappers use separate coordinator and domain-Operator token files; only file paths,
never token contents, enter arguments. If state already exists, seed must refuse; do not reset
or reseed as a readiness fallback. Acquire retries retain the same key and reason after an
explicit operator decision; ambiguous outcomes remain unknown until exact replay evidence.
Check all protected readiness booleans and compiled UI, not HTTP200 alone. The timer stays off.

## Independent acceptance observations
1. Enter scoped operator credentials in browser memory. Compare allowed domain list/detail/
   export with foreign IDs, mixed raw envelopes, scoped saved-run projections and errors.
   Repeat after revocation/config reload. Confirm domain callers cannot create global runs,
   acquire/schedule or request import callbacks; domain refresh only reloads saved projections. No hidden counts/links or token artifacts.
2. Import wholly selected-domain canonical intended-inventory JSON with reconciliation disabled within 10MiB/10k bound; retain receipt and candidate hash.
   Produce C-M comparison, check both count equations and active-only set. Inspect whole-envelope invalid/duplicate-row refusal, canonical whole-batch replay,
   comparison conflict and stale examples; valid intended staging has accepted=input and
   rejected=duplicate=0. Partial observation receipts are coordinator-only and not part of
   the migration assessment. Independent sign-off only when valid.
   Retain active-state revision before/after assessment: unchanged.
3. Create exact local IPv4 reservation with 24h default; available capacity decreases by one.
   Request allocation against its exact version and matching owner/service; another permitted
   principal approves. Reservation converts atomically, no double count. Concurrent/stale/
   wrong-domain/self-approval actions must fail visibly with preserved state.
4. Separately reserve another unused local address, request release and independently decide.
   Release checks no allocation/external effect; refused release leaves hold. Historical due
   fixture shows alert/alarm timing and acknowledgement without automatic free/clear.
   Under the approved FR006 amendment, assign one reviewed synthetic Operator recipient
   per domain/scope. Observe denied other-Operator acknowledgement, missing/disabled/
   expired recipient, current-recipient exact replay and changed-reason conflict.
   Change the reviewed route: GET must not reroute, ack refuses until explicit evaluate,
   and combined alarm/route change creates only one new version. Retain the old own
   receipt and recover an ambiguous ack through its exact original-version GET after
   renewal. Confirm unrelated configuration revision with the same eligible recipient
   does not renew. Legacy schema6 Operator acknowledgements remain legacy, never
   recipient receipts; malformed legacy acknowledgement migration fails atomically.
5. Observe local request plus ticket intent, then manual simulated attempt/readback. Cover
   success, definitive failure, effect-committed/response-lost, no-effect-response-lost and
   disabled connector. Use same correlation/digest; unknown never shown successful and
   attempts never exceed three. Ticket failure does not erase local allocation.
6. Compare current static hold occupancy to its ledger and saved DHCP metrics to saved source;
   show exact units/time/completeness. Unknown evidence cannot clear finding-backed alarm.
7. Export same-candidate sanitized evidence/offline API pack. Every simulated ID/receipt says
   simulated, provisioning unsupported; no 92-completed or live integration claim.

Luna retains exact requests/redacted responses, candidate/schema/config revisions, prior
and resulting IDs/versions, failures, evidence hashes and limitations. The author cannot
self-accept. A correctly represented/recoverable unknown outcome is an expected case.

## Stopped recovery sequence (later, disposable target only)
Use a new snapshot filename; both backup and restore require stopped service:
```sh
scripts/ops/stop.sh
scripts/ops/backup.sh bridge-review.sqlite3
scripts/ops/snapshots.sh list
scripts/ops/restore.sh bridge-review.sqlite3 --confirm
scripts/ops/start.sh
scripts/ops/health.sh --readiness --token-file /protected/operator.token --domain demo-core
```
This package stop/start sequence is an instruction, not an execution claim. Snapshot restores state,
not code/UI/config/credentials; pin/provision those separately. Restore never implicitly
migrates: invoke scripts/ops/migrate.sh only for an explicitly recognized old schema under
the adopted upgrade protocol, still stopped. Retain rejected corrupt/nonstandalone/unsupported/
busy cases without damaging the prior store. Compare allocation/reservation/request/intent/
attempt/assessment/audit lineage and readiness plus representative business read afterward.
Include schema7 recipient notification/history in the comparison. Retain the separate
snapshot-bound sanitized recovery manifest and compare its source/config classification.
Observe matching, changed and unavailable configuration evidence; missing manifest is
unverified data rescue, while malformed/hash-mismatched present manifest refuses before
replacement. Manifest publication failures retain and identify any published DB snapshot.
All six readiness booleans are necessary but remain separate from business comparison.
Measure full declared incident boundary; historical 4.427 seconds is not this changed candidate.

## Human and business gate
One guided human rehearsal must have an actual participant/acknowledgement to claim handoff.
Agent reproduction supplies technical evidence only. Missing human/final independent review/commercial inputs
remain separately named gates. Main Lead accepts the evidence or returns bounded findings;
workers report exact SHA/PR, evidence, gaps and draft next prompt, never global completion.
