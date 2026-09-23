# T022 — Recipient validation and preparation pack (template, source-only)

Task: **T022**. Author: Muse 1.3 high (OpenCode), accountable to Astra / Main Lead 5.0
(`01a0ccc7-6219-73c1-bd3b-1521bb71a837`). Independent reviewer: GPT-6 Sol high.
Leased paths: this file and `configuration-example.json` only. No other edits.
Ownership basis: the user confirmed Spencer had never been assigned this prepared work
and explicitly directed agents to do it; see
`delivery/operator-preparation-ownership.md`. The prepared Spencer worktree
(`ab005d8b…`) remains untouched; no acknowledgement is inferred.
T021 (Opus, offline API) runs in parallel; T024 follows reviewed T021/T022/T023.
No planning restart, no unleased changes.

**Stated shared reviewed base:** `cc4e281756b1847b1312d6b260b3f57bd7df0d98`
(as directed; not re-derived here — no Git/shell execution is leased to this task).
**Inspected source pins:** application assembly
`a2b567b670129671f85498729753c4d577d4768e` (source-reviewed T018 notice/occupancy
UI + T023 stopped recovery) and T020 integration-matrix source `1123146ce60ac3636d9a38af8be90467c1df90bf`
(Sol source-closed, PR94). **All runtime is unverified: no application checks,
builds, imports, database or browser execution ran for this pack.** T010/T015/T017A
source prerequisites are accepted as stated; schema 7 is current, historical
schema 6 is frozen. T025 independent observations and T026 actual human evidence
are pending and separate.

**What this pack is:** a complete, usable recipient handoff template — one target
declaration (§2), prerequisites (§3), protected-readiness rules (§4), a
shape-exact reviewed-configuration example (§5), recipient procedures with blank
evidence fields (§6), restore/history rules (§7) and a blank human-acknowledgement
record (§8). **A template cannot claim readiness.** Every observation field below
is blank or explicitly PENDING until T025/T026 fill it on the exact pinned
candidate.

## 1. Source pins and future-hash ledger

Inspected (source review only, runtime unverified):

| Pin | Value | State |
|---|---|---|
| Shared reviewed base (stated) | `cc4e281756b1847b1312d6b260b3f57bd7df0d98` | Source only |
| Application assembly | `a2b567b670129671f85498729753c4d577d4768e` | Source-reviewed through T018/T023; runtime unverified |
| T020 integration matrix | `1123146ce60ac3636d9a38af8be90467c1df90bf` (PR94) | Sol source-closed; runtime unverified |
| Schema | 7 current (`store.SCHEMA_VERSION = 7`); 1–6 migratable; schema 6 frozen, never rewritten | Source only |
| Feed authority | `FEED_VERSION = ipam-evolving-v1`, 9 pinned asset hashes + 16 registered source/scope grants in `feed_adapter.py` | Source only |

Future hashes are recorded separately when they exist. Today all are PENDING —
nothing below invents them:

| Future hash | Value today |
|---|---|
| Exact T025 candidate source | PENDING (T025 prerequisite-gated) |
| Built image digest | PENDING (T024 packaging, then T025) |
| Built UI asset hash | PENDING |
| Feed asset hashes at observation time | PENDING (pins above are source pins, not observations) |
| Enabled reviewed-config revision + digest | PENDING (example in §5 is shape-only, disabled) |
| Schema version at observation | PENDING (expect 7; 8+ reserved for Tier B) |
| Evidence bundle hash | PENDING |

Actual executable readiness and target observations are pending T025. T024 is
source/package preparation only — no execution is authorized before T025 — so
observed versions (including any Compose plugin version) belong to that later
authorized gate, not to T024; this template records no version.

## 2. Target declaration — one Linux amd64 target, presently UNAVAILABLE

| Field | Value |
|---|---|
| Declared target | Linux amd64 (sole Tier A packaged target; ARM64 is stretch and unclaimed) |
| Host identity | **UNAVAILABLE / UNSELECTED** |
| Recipient identity | **UNSELECTED** (no recipient named; never agent-as-recipient) |
| Recipient acknowledgement | **PENDING** (see §8; T026 owns actual human evidence) |
| Prior target state | The earlier disposable VM and all dedicated provider resources were destroyed and verified absent; prior evidence stays tied to its exact historical candidate only |

Do not invent a host, recipient or acknowledgement to fill this table. Until an
actual tracked `current-target-evidence` record exists, the target is
UNAVAILABLE: that blocks target-specific observed runtime, portable and human
claims (§9), but it does not block later authorized T024 source/docs
implementation, which needs no host selection merely to write source. Per the
user's explicit instruction, work STOPS before T024 and resumes tomorrow; no
target is selected and no actual observation exists.

## 3. Recipient prerequisites (all must hold before any observation)

- **One process**: a single FastAPI/Uvicorn application process serves the
  compiled frontend and `/api/*`. No second service, worker queue or event bus.
- **Local SQLite**: the API-owned database at `IPAM_DATA_DIR` (native default
  `./data`, image default `/data`). No PostgreSQL/DuckDB/NetBox.
- **Local volume**: data resides on a supported local filesystem / local Docker
  volume, never a network mount. Missing/unwritable paths fail visibly; no
  ephemeral fallback.
- **Loopback only**: default loopback HTTP; container internal port 8000. The
  all-interface serve option is for the container process only. Non-loopback
  exposure requires separate TLS/deployment authorization (not granted here).
- **Timer off**: the acquisition timer remains default off; only coordinator
  manual Run now / opt-in callback paths exist. No new per-domain clocks.
- **Isolated disposable synthetic data**: T025 uses disposable synthetic data
  only — seeded baseline plus the pinned evolving feed. No live sources, no
  customer data, no production access.
- **Protected configuration + credential provisioning/revocation**: the reviewed
  access configuration is provisioned separately outside the repository and
  snapshots (via `IPAM_ACCESS_CONFIG`), with permissioned offline issuance
  (`secrets.token_hex(32)`, exactly 256-bit tokens stored as SHA-256 digests),
  rotation and revocation. Fail-closed startup when configured authority is
  invalid. Stopped/reload revisions revalidate future operations.
- **Secret hygiene**: no auth secrets in URLs, CLI args, logs or the package.
  Browser token is memory-only; downloads use authenticated fetch + local blob,
  never an unauthenticated anchor or token-in-URL. No live tokens in the package
  or backup. Coordinator credential (fixed evidence acquisition) and domain
  operator credential are separately provisioned; the acquire wrapper never uses
  a browser operator token.

## 4. Protected readiness — six booleans, business comparison, human ack

`GET /api/readiness` requires Operator rights **and** an explicitly selected
permitted domain. HTTP 200 requires **all six** true; otherwise a failure status
with allowlisted generic reasons only (never raw startup details, paths, foreign
objects/counts or historical revision lists):

| Boolean | Meaning |
|---|---|
| `process_ready` | Application process is up and serving |
| `schema_ready` | Recognized schema (7 current; 1–6 explicitly migratable; unknown fails visibly) |
| `data_ready` | Initialized application data present (never silently re-seeded) |
| `static_ready` | Compiled UI assets present and served by the API process |
| `configuration_ready` | Loaded reviewed-configuration authority validates |
| `domain_state_compatible` | Prerequisites to interpret the selected domain's current state and enforce its permissions hold — **not** equality of every historical revision to current configuration |

`GET /healthz` is minimal non-sensitive process liveness only
(`{"process_ready": true}`); the container HEALTHCHECK uses it, while operator
readiness uses authenticated `/api/readiness` with all six booleans.

Two further gates are **independent of** the six booleans and of each other:

1. **Independent business comparison**: the operator separately compares the
   retained candidate/configuration against business-state evidence. Six
   booleans, a restore success or an equal config digest never promote to
   business-state recovery or portable/human evidence.
2. **Actual human acknowledgement**: the §8 record, filled by the real
   participant. Agent preparation or reproduction is never a substitute.

## 5. Reviewed-configuration TEMPLATE — `configuration-example.json`

### 5.1 Exact closed keys and types

The example uses exactly the closed key set enforced by
`backend/ipam_demo/access.py::_load_configuration`; unknown extra fields,
malformed or duplicate entries fail configuration parsing. **No extra root,
principal, coordinator, mapping, route or recipient keys may be added** — in
particular this file carries no `_notes`/`_comments` key; all guidance lives in
this document. Types:

| Key | Type / rule |
|---|---|
| `revision` | Integer ≥ 1 (example: `1`; set the actual reviewed revision locally) |
| `effective_at` | Aware UTC ISO-8601, must not be in the future at load |
| `policy_revision` | Nonempty text naming the reviewed policy revision |
| `connector_mode` | `simulated` or `disabled` (example: `simulated` for `internal-ticket-simulator/v1`) |
| `reviewer_references` | Nonempty list of unique nonempty texts (independent review refs) |
| `principals` | Nonempty list of exact `{id, token_digest, token_bits, enabled, expires_at, roles, domains}`; unique ids **and** unique digests; `token_digest` 64 lowercase hex; `token_bits` exactly `256`; `roles` ⊆ viewer/requester/operator/approver/platform_admin; aware UTC `expires_at` |
| `evidence_coordinator` | Exact `{principal_id, grants:[{source_id, scope_id}]}`; the coordinator principal must have **empty** roles and domains; **grants must equal exactly the full `source_mappings` pair set** |
| `source_mappings` | `[{source_id, scope_id, domain}]`; one domain per scope_id; must cover every registered feed pair and invent no source |
| `routes` | `[{domain, action, revision, team}]`, unique by (domain, action); the live action is `allocation.request` |
| `notice_recipients` (optional) | `[{domain, scope_id, principal_id}]`, unique by (domain, scope_id); absent list means no routes; **no fallback** to creator, `owner_reference`, first Operator or request payload |

### 5.2 What is synthetic in the example (nothing usable, nothing real)

- All four principals are named `example-*`, **`enabled: false`**, with distinct
  visibly-dummy SHA-256-shaped digests (`aaaa…`, `bbbb…`, `cccc…`, `dddd…`).
  These digests correspond to no token, are not existing credential digests, and
  must never be enabled: a disabled principal fails authentication before any
  other check, so this file is fail-closed as shipped.
- `policy_revision`, route `revision`/`team` and `reviewer_references` are
  `EXAMPLE-…-REPLACE` markers. There is **no fabricated reviewed signoff**: the
  reviewer reference explicitly reads unreviewed until replaced.
- No real bearer token, no private attachment, no user state and no existing
  credential material appear anywhere in this pack.

### 5.3 Replace-locally-only procedure (authorized provisioning)

Replace every placeholder **locally only**, under explicitly authorized
offline provisioning, and never commit the enabled file:

1. Issue each principal a fresh 256-bit token via `secrets.token_hex(32)`;
   store only its SHA-256 hex digest in `token_digest` with `token_bits: 256`;
   convey the token to its holder through the permissioned channel (never
   URLs/CLI args/logs/package).
2. Set `enabled: true` only for actually provisioned holders; set the real
   `expires_at`, `roles` and permitted `domains` per holder.
3. Set the real `revision`, `effective_at` (not future), `policy_revision` and
   actual reviewer references from the reviewed revision record.
4. Keep the enabled configuration outside the repository and snapshots
   (`IPAM_ACCESS_CONFIG`); document issuance/rotation/revocation separately.

Do not generate, run or activate any config or credential as part of this
template task — no leased execution exists for it.

### 5.4 Coordinator, grants and source mappings (actual feed, no invented fields)

- The coordinator entry is separate with **empty roles and domains**; it holds
  no allocation/correction/reservation/approval/membership/ticket-delivery
  rights — only explicitly granted fixed feed `read/acquire/run/reconcile`
  operations across the registered pairs.
- `source_mappings` lists **all 16** `REGISTERED_SOURCE_SCOPE_GRANTS` pairs from
  `feed_adapter.py` (2 inventory sources × 4 scopes + 8 observation sources ×
  their scope), with scope→domain taken from the actual fixture
  (`fixtures/v1/inventory.json`): north→`demo-core`, lab→`demo-lab`,
  coastal→`demo-core`, central→`demo-core`. No source, scope or domain is
  invented. `evidence_coordinator.grants` repeats exactly the same 16 pairs, as
  the loader requires.
- `routes` covers `demo-core` and `demo-lab` for action `allocation.request`;
  each entry's `revision`/`team` is the **current-config** team map (replace with
  the actual configured team). Historical revision references (assessment
  `authority_revision`, snapshot-manifest config identities, route assignment
  history) are **not** current config: they stay attached to their historical
  rows and are compared, never rewritten, on restore/readback.

### 5.5 Recipient entries and routing outcomes (shape-example vs enabled config)

The example's two `notice_recipients` entries are deliberate illustrations, not
an enabled routing table:

- `(demo-core, north-scope)` → `example-notice-recipient`: resolves
  **unroutable/`disabled`** (principal disabled) while remaining internally
  identified.
- `(demo-core, coastal-scope)` → `example-unknown-principal-NOT-PROVISIONED`:
  resolves **unroutable/`unknown_principal`**.

**Shape-example vs enabled reviewed config:** this file proves key/type shape
and documents every field; it authorizes nothing. An enabled reviewed config is
a separately provisioned file whose revision/digest the recipient verifies
through `X-IPAM-Configuration-Revision/Digest` pins and `GET /api/readiness`
(`configuration_ready`). Unknown-recipient, missing-mapping, disabled and
expired mappings stay **visible** in projections with their allowlisted reasons
(`missing_mapping`, `unknown_principal`, `disabled`, `expired`,
`not_operator`, `wrong_domain`) — there is no default-owner inference and no
fallback to descriptive `owner_reference`. Only a currently enabled, unexpired,
selected-domain Operator binding resolves `assigned`.

## 6. Recipient procedure — steps and blank evidence fields

Conventions: `_______` = fill at observation time on the pinned candidate.
`T025:` = observed by the independent verifier, not by this template.
`T026:` = actual human evidence only.

### 6.1 Canonical intended staging (all-or-nothing identity and counts)

1. Submit the intended-inventory candidate envelope (`POST /api/imports`,
   wholly selected-domain, `reconcile_after_import=false`).
   Identity: canonical-JSON replay — same identity + hash replays the original
   receipt; changed content under the same identity is a 409 conflict.
2. Record the receipt counts and verify the equations (T025: _______):
   `input = accepted + rejected + duplicate`; on the ordinary
   intended-candidate path a successful staged receipt has
   `accepted = input`, `rejected = duplicate = 0`.
   Whole-envelope refusal creates no receipt and changes no state; it is not a
   rejected-row receipt.
3. Coordinator observation imports may carry partial/rejected/duplicate rows;
   such a receipt is **never** a migration-assessment candidate.

### 6.2 Immutable assessment comparison, conflict and active-only accounting

4. Create the assessment (`POST /api/migration-assessments`) with the four
   required fields `source_batch_id`, `expected_baseline_version`,
   `idempotency_key`, `reason`; `supersedes_id` and `supersedes_reason` are
   optional and only together. Record assessment ID _______ and immutable
   digest (`ipam.assessment_digest.v1`, `sha256:` + hex) _______.
5. Verify accepted-class accounting (T025: _______):
   `accepted = added + changed + unchanged + conflicting`, with conflicts taking
   precedence (a changed owner conflicting with a current approved assignment is
   `conflicting`, never an ordinary change).
6. Verify active-only rows are reported separately and are never deletion
   proposals; missing source rows establish no available addresses (T025: _______).
7. Cross-check the digest anchor: recomputed on read, compared to the creation
   receipt anchor; missing/mismatched anchors fail visibly with no silent
   repair (T025: _______).

### 6.3 Independent current signoff

8. An **independent approver** (different principal ID from the creator,
   regardless of role) signs (`POST …/{id}/signoff`, exact five-field body with
   `active_only_acknowledged: true`). Preconditions: zero rejected rows,
   explained duplicates, approved mapping, no conflicts, reconciled counts,
   acknowledged active-only list, unchanged baseline and governing revisions.
   Signer _______ / signed version _______ / digest matched _______ (T025: _______).
9. Stale signoff is retained but noncurrent; a historical success never overrides
   current staleness. **Abandoning review changes no persistent active state.**
10. There is **no activate / promote / cutover endpoint and no database
    rollback**: the assessment never promotes candidate inventory and a stopped
    restore is disaster recovery, not candidate undo.

### 6.4 Separate operational compensation (own action, own Tier block)

Any operational compensation (e.g., future allocated release/reuse) requires
its own supported, independently approved action under its own contract and its
own allocated release Tier block. Tier B (T029–T040) is **locked** until Tier A
passes at T025 with reserve intact and explicit lead selection. Nothing in this
pack authorizes, describes, or pre-approves such an action.

### 6.5 Local reservation / extension / allocation / unused release — vs the ticket simulator

Local lifecycle (designated static IPv4 pool only; pool
`8821c420-18ea-4caa-9d97-83a331c0c002`, family 4, static, local authority):

| Step | Record (T025: _______) |
|---|---|
| Reserve: Operator creates with exact candidate + pool/baseline versions + idempotency key; pending requests do not reserve | Reservation ID _______ / version _______ / replayed _______ |
| Extend: exact expected versions + reason + key | New expiry _______ / version _______ |
| Allocate: independent Approver decides; exact reservation identity (`reservation_id` + `service_reference` + positive `reservation_version`) converts the hold atomically | Allocation _______ / linked reservation _______ |
| Unused release: independent Approver; an **unlinked** hold releases normally; a hold linked to a pending/`routing_blocked`/`unknown` intent is conservatively refused until explicit ticket resolution | Decision _______ / reason _______ |

Ticket-simulator states are **separate facts** shown separately, never merged
into local state: local approval commits despite routing/delivery failure;
ticket approval never authorizes IPAM mutation; provisioning is
unsupported/`not_requested`. An `unknown` attempt outcome resolves only by
exact-correlation + business-digest readback finding the persisted effect
(`delivered` with the actual synthetic ticket ID) or by definitive absence
along the fenced-failure / zero-attempt path — readback never claims success
without a found effect. Limits: three total manual attempts, 5 s observation
deadline (not a sleep), no auto-retry/queue, no route change after any attempt
(reassignment: zero-attempt pending/`routing_blocked` only, current configured
team only). Attempt/readback/ack/reassign observations (T025: _______).

### 6.6 Configured per-version in-app notice receipt — vs actual human handoff

- One reviewed Operator recipient per (domain, scope); immutable binding per
  notice notification version recording recipient, configuration
  revision+digest and server UTC. Renewal only on new due episode,
  alert-to-alarm escalation, explicit manual evaluate with changed
  recipient/eligibility, or legacy renewal — one version bump per evaluate;
  GET never reroutes; unrelated config changes with the same eligible
  principal do not renew.
- Ack (`POST /api/reservations/{reservation_id}/notice`; body requires
  `notice_id`, `expected_notification_version` and `reason`, with optional
  `actor_id` matching the authenticated principal) distinguishes response
  classes per `app.py:1175-1199` and
  `lifecycle.acknowledge_reservation_notice`: missing or invalid credential
  fails at authentication (401) before the leaf; a foreign or unclassifiable
  target is a non-disclosing 404 (including a malformed `notice_id` or one
  bound to another reservation); an authenticated principal that is neither
  the bound nor the current recipient is refused 403 (`FORBIDDEN — only the
  bound notice recipient may acknowledge this version`); a missing child
  binding returns 409 `NOTICE_BINDING_MISSING`; a changed route where the
  caller is bound-but-no-longer-current or current-but-not-yet-bound returns
  409 `NOTICE_ROUTE_CHANGED`; a resolved notice returns 409 `NOTICE_RESOLVED`;
  a superseded version returns 409 `STALE_NOTICE`; any other ineligible state
  returns 409 `NOTICE_INELIGIBLE`; a version already carrying a different
  receipt returns 409 `NOTICE_ALREADY_ACKNOWLEDGED`. Same version/actor/reason
  replay returns the original receipt without a new write. Manual-evaluation
  renewal advice applies only to the specifically recoverable evaluation
  cases — `NOTICE_BINDING_MISSING` (evaluate first to create the child
  binding) and `NOTICE_ROUTE_CHANGED` (evaluate to bind the current eligible
  recipient) — never to 401/403/404, resolved, already-acknowledged or stale
  outcomes, which each keep their own disposition. After renewal, authorized
  exact-version `GET …/notifications/{version}` receipt readback proves the
  original own receipt only if that exact original immutable receipt is
  present; a missing record proves no absence of an in-flight write.
  Resolution never means delivery or acknowledgement; receipt history is
  immutable.
- **Configured per-version in-app receipt (`acknowledgement_kind =
  recipient_in_app`, `owner_signoff = false`) is not an actual human handoff.**
  The business owner is never inferred from `owner_reference`; the actual
  handoff/business-owner evidence is the §8 human record (T026), filled by the
  real participant — never the agent preparing this pack.
- Ambiguous-ack recovery retains only the minimal pointer (original
  principal/domain/config revision+digest, notice ID, notification version);
  authorized exact-version `GET …/notifications/{version}` confirms the original
  own receipt after later renewal. No silent replacement, no new key generated
  as another principal.

## 7. Restore, history preservation and snapshot classification

- On stopped restore, history and source authority are preserved: assessment
  decisions, ticket attempts/effects/receipts, notice bindings/receipts,
  reservation/release history, scoped presets and historical configuration
  references are kept without rewriting; legacy schema rows keep their actual
  version until explicit migration. Normal staleness and reauthorization apply
  after restore; no global refusal for old historical revisions.
- The `<snapshot>.recovery.json` sidecar classifies **configuration evidence
  only**: `like_for_like` (saved revision+digest equal current),
  `changed_configuration` (both known, unequal) or `unverified` (legacy/absent
  sidecar or unknown current config). It is never full recovery readiness or
  business acceptance. A restore under a different governing configuration is
  changed-configuration recovery: record the difference, apply normal staleness
  and reauthorization.
- **A snapshot is the SQLite database only.** Snapshots preserve historical
  actor and recipient principal IDs, receipts and audits as stored rows.
  Excluded is the separately provisioned current access-configuration
  principal directory and all token-digest/token material — plus code, UI,
  feed assets, configuration files and other secrets, which are never assumed
  to be snapshot contents. The manifest serializes observed config identity
  (revision/digest/policy) — never the configuration itself, recipient
  identities or credentials.
- Missing assets, invalid schema or failed readiness remain **blocking** and
  are never quietly re-seeded. Missing/invalid current configuration does not
  prevent rescuing recognized data (marked `unverified`, separate readiness
  required).

## 8. Actual acknowledgement record — PENDING, never agent-as-recipient

| Field | Value |
|---|---|
| Participant (actual human name/identity) | PENDING (T026) |
| Role (recipient operator / business owner / approver) | PENDING |
| Date / time (aware UTC of the acknowledgement act) | PENDING |
| Candidate source pinned | PENDING (exact T025 candidate SHA) |
| Target from §2 | UNAVAILABLE until selected |
| Enabled reviewed-config revision + digest | PENDING (shape example §5 is not this) |
| Procedure witnessed (assessment/signoff/restore/readiness per §6–§7) | PENDING |
| Observed outcome per step | PENDING |
| Remaining gaps disclosed to the recipient | PENDING |
| Explicit acknowledgement statement | PENDING — only the real participant's own words, recorded by Astra/Lead |

No agent — author, reviewer or lead — ever fills this table as recipient.
Agent reproduction of the steps is preparation, not receipt.

## 9. Blocking states — explicit, no reseed fallback

| Missing state | Disposition |
|---|---|
| Target (§2) UNAVAILABLE/UNSELECTED | Blocks target-specific observed runtime, portable and human claims; does not block later authorized T024 source/docs preparation (currently STOPPED per user instruction until tomorrow); T025 observations additionally need a selected target |
| Image/UI/feed/config/schema/evidence hashes (§1) PENDING | Blocks exact-candidate claims; source pins are not observations |
| Six readiness booleans not all true (§4) | Blocks operation claims; failure reasons stay allowlisted |
| Required technical restore / business-state comparison (§4/§7) absent | Blocks T025 and technical acceptance: the selected-domain comparison of retained candidate/configuration against business-state evidence is a required gate alongside the six booleans |
| Actual human rehearsal / acknowledgement (§8) pending | Limits the human-handoff claim to the technical package only; alone it does not block a technically validated merge (MAIN_MERGE_POLICY.md) |
| Snapshot sidecar absent/mismatched (§7) | Legacy/data-rescue path only (`unverified`), or refusal before replacement |

There is **no reseed fallback**: a missing asset, invalid schema or failed
readiness never resolves to a quiet re-seed. Failures are visible, recorded,
and re-attempted only through their supported, authorized path.

## 10. Later tasks and non-claims

- **T024** (Muse, after reviewed T021/T022/T023 — user-directed STOP before
  start, resume tomorrow; a hold, not a permanent prohibition): operator/
  package source preparation on the task-graph package/ops paths plus the
  narrow lead-settled lease expansion for stale docs/logs —
  `docs/RUNNING.md` for bridge auth/readiness/config text and
  `scripts/ops/start.sh` / `scripts/ops/backup.sh` for readiness/actual-volume
  comments and messages only. The exact leased file list lives in the latest
  lead-owned `delivery/operator-preparation-ownership.md` and the T024 pickup,
  which control over any file count stated here; those lead docs and all T024
  files are outside this task's lease. Future Compose requires an explicit
  `IPAM_DATA_VOLUME` (new disposable recorded candidate volume; deliberate
  reuse only as recorded). No execution runs under T024, so T024 records
  declared/packaged references only; observed versions belong to the later
  authorized T025 gate. Do not start T024 in this task.
- **T025** (Luna, independent): exact-candidate observations filling every
  `_______`/PENDING field above — success/denial/stale/replay/concurrency/
  unknown/aging plus stopped recovery — only after explicit validation
  permission, on disposable synthetic data.
- This pack creates **no new infrastructure, no deployment, no customer
  engagement and no license claim**. Dependency/license disclosure stays
  T024's deliverable (RFP-106); commercial terms, staffing, SLA/compliance and
  distribution rights belong to unassigned human roles. Questionnaire ledgers
  are unchanged by this documentary pack (accepted ledger stays 39/18/10/44).

## 11. Source assumptions and remaining gates

**Assumptions (source-read, unexecuted):** `access.py` closed-key parsing,
fail-closed bearer/digest/expiry logic, coordinator-grant equality,
`resolve_notice_recipient` reason taxonomy and redaction boundary;
`feed_adapter.py` 9 asset pins, 4 rich scopes and 16 registered grants;
`fixtures/v1/inventory.json` scope→domain map; `store.py` schema 7 with 1–6
migratable; C-A/C-M/C-L/C-T/C-O wires, `notice-recipient-wire.md` binding/ack/
recovery semantics and `state-recovery-wire.md` sidecar classification; T020
matrix row dispositions (§4 equations, simulator limits, readiness split);
T010/T015/T017A source prerequisites accepted as stated. Runtime behavior of
every cited path is unverified.

**Remaining gates:** Sol independent source review of this pack → Lead
acceptance → (user-directed STOP; T024 packaging resumes tomorrow) → T025
observations → T026 actual human evidence or pending disposition → T027
review → T028 merge decision. Tier B stays locked.

---

*Reporting: T022 / Muse 1.3 high (OpenCode) / leased paths
`specs/001-postmeeting-bridge/delivery/recipient-validation.md` +
`specs/001-postmeeting-bridge/delivery/configuration-example.json` /
stated base `cc4e281…df0d98`, inspected assembly `a2b567b…`, T020 source
`1123146…` / implemented: complete recipient template pack (this file) and
closed-key configuration shape example / actually observed: nothing (no
execution leased; all observation fields blank/PENDING) / synthetic or
simulated: all identities, digests, revisions, routes and recipients in the
example are visibly dummy placeholders; all procedures unexecuted /
checks run: none (none authorized) / blocker: none for source work; T025/T026
permission gates remain with the Lead / suggested next prompt: Sol independent
source review of the two T022 files against `access.py`, the recipient wire
and the T020 matrix, then T024 dispatch after T021 closes.*
