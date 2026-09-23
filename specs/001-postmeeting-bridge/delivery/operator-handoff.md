# T024 — Operator handoff: portable package and manual operations (source-only)

Task: **T024** (bridge operator/package preparation). Author: Muse Spark 1.3
Contributor high in OpenCode, accountable to Astra / Main Lead 6.0
(`01a0cf70-c4e0-7ed2-b50b-834609e6d909`). Independent reviewer: GPT-6 Sol
high, which reviews this full result and the shared invariants before
integration. Lease: `scripts/ops/acquire.sh`, `scripts/ops/health.sh`,
`scripts/ops/README.md`, this file, `Dockerfile`, `compose.yaml`,
bridge auth/readiness/config text in `docs/RUNNING.md`, and
readiness/actual-volume messages and comments in `scripts/ops/start.sh`
and `scripts/ops/backup.sh`. No `common.sh` changes, no new ops
framework, no backend/UI/schema/lockfile changes.

**Reading rule.** Where this handoff, the T020 matrix, a contract or an
older runbook disagree, the pinned application source and the T021/T022
wires are decisive. Every command below is source preparation, not an
observed run: **no application checks, builds, imports, typechecks, lint,
SQL/DB execution, servers, browser checks or runtime probes ran for T024.**
All observation fields are PENDING until the authorized T025 gate fills
them on the exact pinned candidate. Nothing here claims a build, a
host/Compose version, license clearance, runtime acceptance or human
acknowledgement from source.

Prerequisites (reviewed, source-closed, runtime unverified): T021 offline
API (`offline-api.md`), T022 recipient pack (`recipient-validation.md`,
`configuration-example.json`), T023 stopped recovery
(`contracts/state-recovery-wire.md`).

## 1. Pinned references

| Pin | Value | State |
|---|---|---|
| Application assembly | `a2b567b670129671f85498729753c4d577d4768e` (T018 notice/occupancy UI + T023 stopped recovery) | Source-reviewed; runtime unverified |
| T021 offline API source | `3007bf33dd3481f1b85723b0a1c4971036b5f089` (PR96) + Sol source closure | Source only |
| T022 recipient pack source | `c231663ef9a9747c83288523da9ede93977bef42` (PR95) + Sol source closure | Source only |
| T023 stopped recovery source | `adb2dc18fe747d4ff97a90f1a21bcdc4382f9fea` (PR92) + Sol source closure | Source only |
| T024 candidate source | This branch `codex/bridge-t024-spark-operator`; exact SHA recorded at review | Source only |
| Schema | 7 current; 1–6 migratable; schema 6 frozen, never rewritten | Source only |
| Feed authority | `FEED_VERSION = ipam-evolving-v1`; 9 pinned asset hashes; 16 registered source/scope grants (`feed_adapter.py`) | Source pins, not observations |
| Package bases | `node:22.12.0-bookworm-slim` (UI build), `python:3.12.10-slim-bookworm` (runtime), `ghcr.io/astral-sh/uv:0.7.13` (build helper only); target `linux/amd64` | Declared references, not observed builds |
| UI assets | Compiled Vite bundle served by the single API process from `/app/static` (`static_ready`) | Source only |
| Reviewed-config shape | `specs/001-postmeeting-bridge/delivery/configuration-example.json` (disabled, dummy digests; shape only) | Template, authorizes nothing |
| Enabled reviewed config | Separately provisioned outside the repository; revision + digest observed at T025 | PENDING |
| Built image digest | Observed at the authorized T025 build of the exact candidate | PENDING |
| Host / Compose versions | Observed at T025, never taken from source text | PENDING |

## 2. Target and provisioning

One Linux amd64 target; the actual recipient target remains UNAVAILABLE
until selected, which blocks target-specific portability and human
observations but not this source preparation nor technical local T025 on
its own explicitly pinned disposable synthetic local target.

Before `docker compose up`, the operator provisions two things outside
the repository and outside every snapshot:

1. **Explicit data volume.** Export `IPAM_DATA_VOLUME` with the recorded
   disposable volume name for this candidate. A new candidate records a
   NEW name; reusing a prior volume is deliberate and recorded. Compose
   refuses to start when the variable is unset or empty. The name is
   global to the engine: a different Compose project name alone does not
   isolate data.
2. **Reviewed access configuration.** Export `IPAM_ACCESS_CONFIG`
   pointing at the enabled reviewed file (closed key set per T022 §5;
   `revision`, `effective_at`, `policy_revision`, `connector_mode`,
   `reviewer_references`, `principals`, `evidence_coordinator`,
   `source_mappings`, `routes`, optional `notice_recipients`). Compose
   mounts it read-only at `/run/ipam/access-config.json` and refuses to
   start when the variable is unset or empty. Replace it only through the
   reviewed stopped-service procedure; later requests are evaluated
   against the new configuration, and in-flight authority checks do not
   fence the file beyond their own check.

No token belongs in Compose environment, images, CLI arguments, URLs,
logs, snapshots or browser persistent storage. The reference browser
client keeps its token in memory only.

## 3. Credentials: two separately provisioned token files

| Credential | Holder | Scope | Used by |
|---|---|---|---|
| Coordinator token file | Evidence coordinator principal (empty roles and domains, exact full-feed grants) | Global evidence operations only: `POST /api/schedule/run`, `POST /api/runs`, observation imports, `GET /api/schedule` | `scripts/ops/acquire.sh` |
| Domain-Operator token file | Operator principal in one explicitly selected domain | Domain-local operations including protected `/api/readiness` | `scripts/ops/health.sh --readiness` |

Each file holds exactly 64 lowercase hexadecimal characters
(`secrets.token_hex(32)`, 256-bit, stored server-side as SHA-256 with
`token_bits: 256`), with at most one terminal newline. Both wrappers
enforce a regular non-symlink file, bounded size and owner-only mode
(any group/other permission bit refuses — no warning-only path), reject
internal whitespace instead of stripping it, and deliver the bearer
through a 0600 curl config file written directly by the validating
reader — the token never enters a shell variable, and inherited
`bash -x/-v` tracing is disabled on entry (caller debugging of the
wrappers is unsupported).
A `401` means the token is unknown, disabled, expired or revoked: clear
the session and all protected views, abort in-flight requests, and never
retry with the old token. A `409 ACCESS_CONTEXT_STALE`, or pins that no
longer match the server's current headers, means the configuration
changed: bootstrap again under the new pins and discard late responses
from the earlier epoch.

## 4. Manual acquisition (`scripts/ops/acquire.sh`)

```sh
scripts/ops/acquire.sh --token-file <coordinator-token-file> \
    --key <idempotency-key> --reason "<reason>"
```

1. Bootstrap WITHOUT a domain (`GET /api/access-context`, bearer only).
   The script verifies `is_evidence_coordinator` is true and captures the
   explicit current pins (`configuration_revision`,
   `configuration_digest`). A non-coordinator identity, malformed pins or
   a malformed key/reason fails closed before any POST.
2. `POST /api/schedule/run` with the ORIGINAL stable key AND reason, the
   explicit pins, and NO `X-IPAM-Domain` header and NO `actor_id` (the
   server derives the actor from the trusted bearer, so no mismatch is
   possible).
3. `201` with `X-Acquisition-Replay: false` AND body `replay: false`
   is a fresh acquisition; `200` with `X-Acquisition-Replay: true` AND
   body `replay: true` is the original replay — no new cycle advanced.
   The script validates the exact status/header/body triple and exits 0
   only on full agreement. A missing, malformed or contradictory triple
   exits 6 as UNKNOWN/inconsistent: the original key and reason are
   preserved, no new cycle is claimed, and nothing is retried
   automatically. Record run/cycle/operation IDs from the body.

No automatic write retry and no replacement key. A transport failure
leaves the outcome UNKNOWN: keep the SAME key and reason, and only after
an explicit operator-confirmed decision re-run the exact command to
observe the replay. `409 RUN_IN_PROGRESS` means busy — retry the same
key after the conflicting work finishes. `409 IDEMPOTENCY_CONFLICT`
means the same key with changed content — investigate, never silently
send a new key. `403` on `POST /api/schedule` is the permanent refusal
of schedule configuration over HTTP (stopped-service procedure only).

## 5. Liveness versus readiness (`scripts/ops/health.sh`)

```sh
scripts/ops/health.sh                                   # anonymous liveness only
scripts/ops/health.sh --readiness \
    --token-file <operator-token-file> --domain <domain>  # protected readiness
```

`GET /healthz` returns only `{"process_ready": true}` while the process
serves HTTP. It is the container `HEALTHCHECK` target (Dockerfile labels
record `ipam.healthcheck.scope="liveness-only"`). It proves nothing
about readiness or business state.

`GET /api/readiness` needs Operator rights and the explicitly selected
permitted domain. Success requires HTTP 200 AND all six exact booleans
true — `process_ready`, `schema_ready`, `data_ready`, `static_ready`,
`configuration_ready`, `domain_state_compatible` — with allowlisted
`reasons` otherwise. Viewers and the coordinator receive 403. Six true
booleans never promote to business-state recovery, portability or human
acceptance.

## 6. Stopped recovery and paired transfer

All state commands require a stopped service (wrappers enforce it; the
container's exclusive `.ipam_demo.lock` enforces it server-side).
History and source authority survive restore without rewriting:
assessment decisions, ticket attempts/effects/receipts, notice
bindings/receipts, reservation/release history, scoped presets and
historical configuration references are kept; legacy rows keep their
actual version until explicit migration. Normal staleness and
reauthorization apply after restore; there is no global refusal for old
historical revisions.

Every backup writes a deterministic PAIR inside the explicit data
volume at `/data/snapshots/`: `<name>.sqlite3` plus its
`<name>.sqlite3.recovery.json` sidecar, which binds the exact closed
snapshot bytes (SHA-256, size, schema) to the observed configuration
identity (revision/digest/policy, or explicit unavailable). The manifest
never carries the configuration itself, recipient identities or
credentials, and snapshots never contain code, UI, feed assets,
configuration files or secrets.

**Honest paired-transfer procedure (script limitation).**
`snapshots.sh export`/`import` move one file per invocation, so the
operator transfers the pair manually: export `<name>.sqlite3` and
`<name>.sqlite3.recovery.json` under matching names, verify both
checksums, and import both before `restore.sh <name>.sqlite3 --confirm`.
Restore then treats the sidecar exactly per the frozen wire:
absent sidecar permits only explicit legacy/data-rescue with
`configuration_recovery=unverified`; a present malformed, unsafe or
hash/size/schema-mismatched manifest REFUSES before active replacement;
a present valid sidecar classifies `like_for_like` (saved
revision+digest equal current), `changed_configuration` (both known,
unequal — record the difference, apply normal staleness and
reauthorization) or `unverified` (saved or current identity unknown).
No classification is readiness and none is business acceptance; a backup
success alone establishes neither.

## 7. Separate gates after restore

1. **Protected readiness** (§5) on the selected domain: HTTP 200 with
   all six booleans true.
2. **Mandatory business-state comparison** (T025): the retained
   candidate/configuration is compared against business-state evidence
   by the authorized observation itself. Equal digests, six booleans
   and restore success never substitute for it.
3. **Actual human acknowledgement** (T026): the real participant's own
   record. Agent preparation or reproduction is never receipt, and a
   descriptive `owner_reference` on a reservation is never
   business-owner signoff.

## 8. Configured-recipient policy (settled)

One reviewed Operator recipient per (domain, scope); immutable binding
per notice notification version recording recipient, configuration
revision+digest and server UTC; explicit in-app receipt
(`acknowledgement_kind = recipient_in_app`, `owner_signoff = false`).
Renewal only on a new due episode, alert-to-alarm escalation, an
explicit manual evaluate with changed recipient/eligibility, or legacy
renewal. Unknown, disabled, expired, non-Operator and wrong-domain
bindings stay visible with their allowlisted reasons; there is no
fallback to creator, `owner_reference`, first Operator or request
payload.

## 9. Dependencies and license limitations

Per `docs/RUNNING.md`: Python `3.12.10-slim-bookworm` and locked
`fastapi==0.141.1` / `uvicorn==0.50.1` plus the transitive `uv.lock`
graph; Node `22.12.0-bookworm-slim` with the committed
`package-lock.json`; runtime apt additions `tini` and `curl`; build
helper `ghcr.io/astral-sh/uv:0.7.13` (not in the runtime image). No
per-package SPDX license inventory is published on this branch: license
text lives in each package's installed metadata and has not been
extracted here, and frontend notices have not been extracted or
verified. If a recipient needs a formal notices file, generate it
against the locked graph on the target host. This states the limitation;
it claims no clearance.

## 10. Presenter path (unexecuted)

Seed (rich, stopped) → start → protected readiness (§5) → manual
coordinator acquisition (§4) → UI/API walkthrough of the accepted rich
flows → stopped backup with its sidecar pair (§6). Each step's evidence
is recorded at T025 on the exact candidate; until then this path is a
plan, not an observed rehearsal. Same-host reproduction never
establishes a second independent engine, portable acceptance, or human
acknowledgement.

## 11. Blocking states — explicit, no reseed fallback

| Missing state | Disposition |
|---|---|
| `IPAM_DATA_VOLUME` / `IPAM_ACCESS_CONFIG` unset | Compose refuses to start (fail closed) |
| Six readiness booleans not all true | Blocks operation claims; reasons stay allowlisted |
| Snapshot sidecar absent | Legacy/data-rescue path only (`unverified`), or refusal before replacement |
| Snapshot sidecar present but malformed/unsafe/mismatched | Restore REFUSES before active replacement; never `unverified` |
| Snapshot sidecar present and valid, saved or current config unknown | `unverified`; separate readiness required |
| Business-state comparison absent | Blocks T025 PASSING and technical acceptance |
| Actual human acknowledgement pending | Limits the human-handoff claim to the technical package only |
| Image digest / host versions / enabled-config identity PENDING | Blocks exact-candidate claims; source pins are not observations |

There is no reseed fallback: a missing asset, invalid schema or failed
readiness never resolves to a quiet re-seed. Missing/invalid current
configuration does not prevent rescuing recognized data (marked
`unverified`, separate readiness required).
