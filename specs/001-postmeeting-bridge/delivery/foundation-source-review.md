# First foundation review — source checkpoints only

## T002 source authority

Grok4.6 / OpenCode Go authored91e81506791214c186c10b0ab6ab0ed641655289 from6b66f943b7c7783285bfd1f70859ede42380bf60.
Grok4.7 actual session ses_f3509d265ffeggMSkbiL7emfDV reviewed that exact commit.
Its four bounded findings are retained below. A Grok4.6 correction attempt hit
provider.quota, HTTP429, “Go usage limit exceeded”, before editing. That call stopped
with exit1; no paid fallback/extra-usage activation was attempted. Sol in Codex replaces
that stopped scout for the four leased corrections under the user's escalation authority.
Draft PR68: https://github.com/yugant99/IpManagement/pull/68 . Review remains open.

**Bounded findings — not a source PASS.** This is not runtime proof and not lead acceptance.

Reviewed SHA: `91e81506791214c186c10b0ab6ab0ed641655289`  
Base: `6b66f943b7c7783285bfd1f70859ede42380bf60`  
File: `specs/001-postmeeting-bridge/delivery/source-authority.md`  
Model: Grok 4.7 (`opencode-go/grok-4.7`)  
Session: `ses_f3509d265ffeggMSkbiL7emfDV`  
Method: `git show` / `git grep` only. No checkout change, tests, builds, runtime, vendor research, or repo writes.

## F1 — Medium — Planned coordinator path recorded as existing source behavior; intended refusal persistence and audit omitted

**Where:** §1 last paragraph (“already encoded in source … coordinator partial observation receipts”); §2.2 `source_records.status` note; §6 “Intended invalid/duplicate rows”.

**What is wrong:** Partial/rejected/duplicate row receipts are the current observation importer (`imports.py` 444–520). `POST /api/imports` (`app.py` 460–477) has no coordinator or actor gate and audits as `system`. Coordinator-only observation is planned C-M (`contracts/migration.md` 3–5 and 31–33), not code at this base. §1 lists that contrast as already encoded in source.

Intended invalid or duplicate input raises in `_stage_inventory` before the receipt insert at `imports.py` 331–333, so refusal leaves no `source_batches` receipt. `app.py` 469–477 uses `write_operation`, not `audited_write`, and writes `source.import` only after a new non-replay receipt. Refusal currently leaves no receipt and no failure audit. §6 says only “Whole envelope refused”.

**Minimum correction:** In the existing-fields row, state that observation imports may persist partial receipts now, and that coordinator-only submission is planned C-M/C-A. In §1 and §6, state that intended refusal persists no receipt and writes no audit; only a new successful import audits `source.import`.

**Evidence boundary:** Documentary reading of importer and route. Not an executed rollback or audit observation.

## F2 — Medium — One-pool lock is not the lines cited for designated-pool authority

**Where:** §1 Allocated row; §2.1 `pools.allocation_authority` (“Local write authority only for static IPv4 designated pool” at `seed.py` 94–95 and `workflow.py` 119–120).

**What is wrong:** One static IPv4 allocation pool is `workflow.STATIC_POOL_ID` (`workflow.py` 19) plus `_pool` rejecting every other id (`workflow.py` 110–112). There is no configurable pool list. Lines 119–120 only recheck family, `management_mode=static`, and `allocation_authority=local` on that already selected id. `seed.py` 94–95 rejects local authority on a non-static or non-IPv4 pool; it does not select one pool. “North” is the seeded name (`baseline.json`, pool “North static”) and the error string, not the authority key. §1 names `_pool` but not `STATIC_POOL_ID`.

**Minimum correction:** Cite `STATIC_POOL_ID` and `workflow.py` 110–112 as the one-pool lock. Keep 119–120 as the attribute check. Do not cite `seed.py` 94–95 as the designated-pool lock. State that no extra pool list exists.

**Evidence boundary:** Source inspection of `workflow.py`, `seed.py`, and `baseline.json`. Not a runtime allocation attempt.

## F3 — Low — Static-to-DHCP relabel gate points at the wrong contract and task

**Where:** §2.1 `pools.management_mode` note: “Relabeling a static pool as DHCP is forbidden (C-T / planned T034).”

**What is wrong:** `contracts/ticketing.md` does not forbid relabeling. It keeps optional DHCP on a separate fixture. T034 (`tasks.md` 179–181) freezes that fixture distinct from local-static authority. “No static-pool relabeling” is T037 completion (`tasks.md` 193). No current pool-edit path for `management_mode` was found; the note is still in the existing-fields table with the wrong planned pointer.

**Minimum correction:** Mark relabel refusal as planned T037. Cite T034 only for fixture-versus-local-static separation. Do not cite C-T as the relabel rule.

**Evidence boundary:** Task and contract text. No runtime edit of `management_mode`.

## F4 — Low — Baseline authority is unlocated

**Where:** §2 existing field inventory; §5 C-M planned objects.

**What is wrong:** Baseline and evaluation clock are the global `app_meta` row (`schema.sql` 2–11, `singleton=1` only): `baseline_version` and `demo_clock_at`. Imports, catalog, and workflow read that singleton. The register never names it. C-M’s create payload includes expected baseline (`contracts/migration.md` 10); §5 omits that field. Nothing in the file invents a per-scope baseline list, but the authority location is missing.

**Minimum correction:** Record `app_meta` `singleton=1` as the only baseline/demo-clock authority, and add expected baseline to the planned C-M object list as planned, not implemented.

**Evidence boundary:** Schema and call sites. Not a migration or promotion run.

## Held, not findings

In-scope RFP IDs match the FR-009/010/012/014/018/020 cards. Retained S3 classes match `docs/QUESTIONNAIRE_ROW_MAP.md`, not meeting Demonstrated labels. No vendor endpoint, product, version, ACL, or idempotency key is invented. Cisco stays documentation priority only. Allocated, leased, routed, and traffic stay separate, as do intended, observed, and staged, and static versus DHCP occupancy. The file does not add a configurable pool list. Fable is design-only and not a T002 blocker, which matches a completed FABLE-DESIGN pass with final advisory still separate. Schema v5 at this base is `store.py` `SCHEMA_VERSION = 5`.

Remaining boundary: documentary source review only. No test, build, runtime, live vendor, or lead acceptance.

## T003 schema

Terra / native Codex authoredfcac1d801749a005b96a683151e29814d7aafbc6 from source-adopted
e8bc0ed08a8b3734d5278578828c8eb58b9f5d52. Main Lead found that literal semicolons in new
SQL comments break the existing migration splitter. Terra corrected those comments in
17cf1f4d3e06b6f434e54752647257ef2ec7376c; no SQL was executed to establish this source finding.

Luna / OpenCode Go source review returned a missing durable readback/receipt-history
finding, corroborated by Terra and lead inspection. The lead also identified missing
exact-key persistence for several new operations. Terra is correcting the minimum schema.
Luna's suggested equality of attempt request_digest and immutable business_payload_digest
was rejected: C-T explicitly gives the attempt digest different inputs (route/scenario).
Do not add an incorrect equality constraint. Historical business identity remains pinned
through intent/effect foreign keys; handler-level canonical digest enforcement remains
required. The final corrected schema must receive independent source closure.

The Luna invocation used outer session ses_f3500d15dffeDbsId6lGHacezN and relayed a
same-model review from ses_f3500aff6ffeTNgf7mS9o8e3B8. This extra invocation was not
requested by the lead; future reviewer prompts prohibit redispatch. It is recorded rather
than presenting the outer run as a single direct source review. No repository edits or
application tests were performed by that review.

## Remaining gate

No application tests/builds/seed/migrate/runtime/recovery command has been run for this
foundation wave. T003 remains source-only and dependent handlers are not implemented.
T007/T025 and human/portable evidence remain open. Canonical main and accepted ledger
39/18/10/44 remain unchanged.

## Source closure and next leases

Main Lead closed T002 findings F1–F4 against Sol correction
ab005d8bf3b6c57e0a071707796d18514c278674 (parent91e8150). The current importer remains
ungated; coordinator restrictions are correctly labeled planned. Pool/baseline authority
and T037/T034 references are corrected. T002 is accepted as documentary source only.

T003 final source candidate9c73fd8e76c092b4d8297ec4475160b71574de7e contains the parser
fix, narrow exact-key receipts and durable lookup/acknowledgement history, plus explicit
non-NULL simulated acknowledgement and no-effect definitive-absence CHECKs. Independent
Astra source adviser /root/spec_review accepted the exact final delta from e8bc0ed with
no remaining source blocker. This supplements the earlier Luna review; it is not a Luna
runtime pass. PR69 retains all four coherent Terra commits, without rewriting history.

T004 is released to Terra in codex/bridge-t004-access from exact9c73fd8, with only
access.py/models.py leased. T019 is released to Sol replacing the quota-blocked scout
in codex/bridge-t019-qualification from exactab005d8, with only delivery/gaps-and-qualification.md
leased. Spencer's prepared codex/bridge-t020-matrix was fast-forwarded to exactab005d8;
T020's source prerequisite is available, but no human execution or acknowledgement is claimed.


## T019 documentary closure

Sol authored `af2f74a53668b52c31a200c50f2186b22a71cc88`. Independent Astra
source review found the missing RFP-019 recovery-point disposition. Correction
`4034c765fce8a68f8cd73195c73f9a3bdd185d24` retains its Missing class, requires an
approved backup policy and measured loss window, assigns the platform operator role,
and keeps the 24-hour snapshot-age planning assumption separate from that requirement.
Main Lead accepts this corrected document as source-only. No human owner acknowledgement,
runtime measurement, customer requirement fulfilment or ledger change follows.

## T004 access review in progress

Initial Terra implementation `735df304060971e24a9156d1a73d0e951048ce73` needed
four source corrections: Viewer inheritance for Requester/Operator/Approver without
admin inheritance; a simulated/disabled connector-mode allowlist; duplicate JSON-key
refusal; and unambiguous domain ownership of a scope across source mappings.
The lead read the corrected diff at actual Git SHA
`aa5a387d063a73a00fc17a2374037bc8bf314871`. The worker's first full-SHA handoff
had an incorrect suffix; this verified Git identity supersedes it.

The Grok4.7 review attempt hit Go quota429 before returning findings. The latest user
explicitly replaced that review role with GPT-6 Sol and Terra implementation with
GPT-6 Luna. Independent Sol source review is now assigned to the corrected exact SHA.
Route/startup enforcement, configuration-versus-persisted-scope checks and client
integration remain T005/T006; no application execution has occurred.


### T004 final source closure

GPT-6 Sol found one remaining gap: token_bits was self-declared while arbitrarily short
matching bearer strings were accepted. GPT-6 Luna corrected it at
`c7a3bed6dfec31bd07abc613f52b64f1304a1349`: fixed 32-byte random offline issuance,
64 lowercase hexadecimal bearer format, token_bits=256 and SHA-256 over exact ASCII.
No actual token/configuration was created. Lead read the exact correction and accepts
T004 source only; the format does not itself prove random issuance.

Sol also reviewed the T005/T006 wire freeze. Lead adopted its two clarifications:
authenticate/revoke before comparing configuration pins, with no config headers on
unauthenticated responses; and match correction recovery to original actor and exact
proposal/approve/reject outcome, never another principal's decision.
T005/T006 and all runtime/independent QA gates remain open.


## T005/T006/T007 source closure

Main Lead4.0 accepts the bounded access source checkpoint after actual GPT-6 Sol
independent review and owner corrections. API author: GPT-6 Luna, `c4b367b3e51028ea70327ce9c62b9fb4598491e7`.
UI author: a separate GPT-6 Sol worker, `671dae8d2c74f1a426c9f29c3c1d8997d3096ad8`. Reviewed application assembly:
`aee0ade8bbeb6405aab4a6cf0c35079d76e6318e`. [Independent report](https://github.com/yugant99/IpManagement/blob/833c2c8676b205c97476ab71f4e3b2cff0a2c608/specs/001-postmeeting-bridge/delivery/access-review.md) publication: `833c2c8676b205c97476ab71f4e3b2cff0a2c608`,
with route allow/deny/projection/quarantine matrix and the initial findings/resolutions.
Draft PR73/API, PR72/UI and PR74/assembly preserve histories; main is unchanged.

The lead read both correction diffs and the report. Eight backend findings and the
ambiguous-retry/projection-UI findings are source-closed. Direct authenticated OpenAPI
JSON is the current reference path; interactive Swagger usability remains explicitly
with T021. Schedule configuration remains a stopped-service procedure, with T023 and
Spencer's artifacts retaining that responsibility. No anonymous documentation exception.

T007 source closure releases T008 only. No application tests, builds, server, browser,
database/config/token operations or runtime validation were performed. T025 remains
the independent runtime gate; portable/human gates, Tier B and all ledgers are unchanged.
The latest user instruction pauses all OpenCode attempts and settings work.

## T008 source closure

Main Lead accepts `776f32a3eaff2be9a5bd9d09a8f5dab62e4f5509` after GPT-6 Luna
corrections and independent GPT-6 Sol closure of all five reported findings.
[Migration review](migration-source-review.md) retains exact history, findings and
nonclaims. Draft PR75 remains unmerged. T009/T010 may proceed with a lead-frozen wire
contract; runtime validation and all external gates remain open.

## T005 coordinator transaction correction during T025

Candidate3 `0c20a7b` passed protected readiness but manual acquisition timed out with an unknown outcome; same-key retry returned STORE_BUSY. The request-held `database()` read transaction outlived the endpoint's separate writer and blocked its commit in rollback-journal SQLite. The same source pattern existed in global reconciliation. The verifier preserves the original disposable failure store/journal and key.

Retained T005 original author task `01a0cb1e-a711-70a3-a74d-5651989a0355` corrected only app.py at **`7975307e4210083ba7ea6d34e6b80c652c15002c`**. Both coordinator endpoints now use a brief closed preflight before the independent writer. Initialized state, trusted credentials/config pins/full feed grants and source-scope mappings remain checked; scheduler and reconciliation retain fresh in-transaction checks, denial/replay/lock/atomicity behavior. No schema/journal/timeout/isolation workaround was introduced. The author inventoried other writer call sites and found no other request-held read dependency spanning a separate writer.

Visible independent GPT-6 Sol task `01a0cf9a-ce88-7f90-8556-1fa4b131bf26` source-reviewed the complete affected delta and shared callers with no blocking finding. No author/reviewer application execution occurred. PR103 integrated at **`8eb3e231b7792fe8415455d2176e962b8f953d60`**. Separate visible Luna owns the affected exact-candidate rerun and remaining T025 evidence; source closure does not claim runtime success or T028 eligibility.
