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
