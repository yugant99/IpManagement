# Part 6 source acceptance and remaining portable evidence

Accepted by Main Lead 3.0 on 2026-09-20: **packaging/operator source integrated; container and recipient behavior UNVERIFIED**. `PART6_READY=no`. No new implementation stage or broad application E2E run follows.

## Exact source lineage and review

| Checkpoint | Exact identity |
|---|---|
| Original Spencer #49 | `c123a39fee8943418deac3c71e6d6ff74213b72c` |
| Build compatibility #50 | `3e129d9e8a6ba05e7a33f01632b976f9939b224f` |
| Spencer operator #51 before review | `7f79f38bbde62dd0b3c13f7892a48ccfb6a19038` |
| Corrective #53, lead-reviewed delta | `84b3cc7fa0bf6794c0255c8d0913f186582b404c` |
| #51 head after normal #53 merge | `acdc423cb4e7bfd6599dd95183369ef76fa5fd67` |
| Main after normal #51 merge | `65d435a1f22b1343a68b867a11ef3a2353b92f7e` |
| Prior main / lead registration #52 | `9805b5ba9c546ffbbbb82f4be01ae81b7359ad83` |

The existing **Part 6 — Spencer PR review** task (`01a0c097-5159-7fc2-80e3-e9e65af26e6e`, GPT-6 Astra/low) reviewed the complete #51 source and corrected its owned files. Main Lead 3.0 read the complete 14-file corrective delta, core data-lock implementation and packaging configuration before authorizing merge. The corrected tree and normal merge preserve Spencer's commits. Exact #49/#50/original #51/correction heads are ancestors of main; GitHub marks #49/#50 MERGED by inclusion. No separate merges or branch deletions occurred. PR #9 remains OPEN / NO MERGE.

Source blockers corrected:

- Snapshot copying depended on a service container removed by the documented stop command. Transfers now use a one-shot app-user container and the existing core data lock.
- Snapshot imports could overwrite files; transport now checks size/hash, uses private temporary files and publishes without overwrite. Linked files and SQLite companion files are refused; core restore still owns database identity/schema/integrity validation.
- Unrestricted filenames were interpolated into shell commands. Backup uses positional arguments and snapshot operations use argument values without executable shell interpolation.
- Compose status errors were hidden as stopped. They now fail visibly. Operator docs include source/image identity and offline save/load instructions, and current startup/state helpers request no image pulls.

This was source inspection only: no new application tests, builds, helper execution, Docker commands, image pulls, runtime or infrastructure operations. Spencer's reported shell parse checks and the earlier #50 offline native package check remain separate evidence. Native acceptance, historical Stage 5 and F1–F7 evidence remain unchanged. Questionnaire accounting remains **32 Demonstrated / 22 Partial / 10 Documentary / 47 Missing = 111**; the source merge earns no new runtime credit.

## Next gate and permission boundary

GPT-5.6 Luna at **medium** prepared the focused next evidence protocol. Its purpose is portable startup/persistence and recipient reproduction, not another application E2E cycle. The current user instruction prohibits Docker execution (including inspection commands), image pulls, VM/cloud provisioning, deployment and spending. Preparation does not supersede that decision; all steps below remain proposed and unexecuted. Do not ask for repeated Docker approval or silently switch to another host/provider.

Use [RUNNING.md](../RUNNING.md) for the exact supported commands and [STATE_OPERATIONS.md](../STATE_OPERATIONS.md) for core semantics. Existing [native evidence](../DEMO_RUNBOOK.md) supplies application behavior only. A later execution grant must identify the authorized existing Linux amd64 host/operator, exact source/image, disposable data and transfer locations, permitted container/image actions, cleanup owner and cost/public-exposure limits before starting.

## Proposed focused execution record — all unrun

Target prerequisites: existing Linux amd64 host, Docker Engine 24+ / Compose v2, Bash, curl, Python 3.11+ and GNU coreutils. Record actual versions only in an authorized session. Image is `ipam-demo:local`; pin its actual ID/platform after authorized build or load. Runtime uses loopback `127.0.0.1:8000`, read-only root, `/tmp` tmpfs and writable `/data` under uid/gid 10001. No network filesystem or public binding.

**Isolation must precede any wrapper execution.** Compose explicitly names the global volume `ipam_demo_data`; changing the project name does not isolate it. Wrappers also set their own `COMPOSE_FILE`, so an environment override alone is ineffective. Use an authorized disposable source copy with only `volumes.ipam_data.name` changed to a unique recorded volume name. Record the original source SHA, exact compose diff and modified file hash; preserve all other source. Alternatively use a dedicated authorized host/engine where the original named volume is proven absent and reserved for this run. Keep the original volume and acceptance stores untouched. Check existing port/process/container ownership before startup; unresolved ownership stops the session.

| Step | Bounded observation and evidence |
|---|---|
| Fresh rich startup | On a new isolated store, follow `seed.sh` → `start.sh` → `health.sh`, inspect rendered UI and `/api/docs`, then one `acquire.sh <new-idempotency-key>`. Capture readiness including static UI, rich seed, cycle/run/operation IDs and nine source envelopes. Confirm automatic scheduling remains disabled. Preserve the same key across an ambiguous retry. |
| One allocation and restart | Use the accepted UI/API workflow for one request and independent approval. Record scope/prefix/candidate, actors, request/allocation/audit IDs and simulated external outcome. Stop and restart the same store; retrieve the same allocation and audit. Reuse accepted business-rule checks, without another full workflow matrix. |
| Stopped backup and export | Stop the owned service and establish its exit. Back up to a new snapshot name, export to a new host path, retain raw command/JSON output, schema, byte count and SHA-256. A failed transfer must not be treated as a published usable snapshot. |
| Import, refusal and replaced-state recovery | In a second isolated store, establish and record recognizable prior initialized state, then stop it. Import the exported snapshot under a new name. Invoke `restore.sh <name>` once without confirmation: record actual wrapper stderr and exit 2, not a fabricated core JSON refusal. With explicit confirmation, restore and record `database_replaced`, non-null `preserved_database`, `migration_required` and schema. Confirm the preserved snapshot retains the prior target state and the restored allocation/audit match the backup. Start only the restored working copy. No reset or broad refusal matrix is required for this slice. |
| Recipient reproduction | Follow the offline handoff in RUNNING.md: transfer source/image identity, image archive and checksums, plus a separately hashed snapshot if used. An authorized recipient verifies hashes/image ID and repeats a small assigned startup, persistence and stopped recovery path on its own isolated volume. Record elapsed time and every undocumented intervention. Agent procedural reproduction and actual human recipient acceptance are separate outcomes. |
| Retention and cleanup | Preserve source/image/snapshot/evidence artifacts and both prior/working stores until the lead reviews results. Stop only session-owned services. Remove only explicitly authorized newly created disposable resources; never delete the global pre-existing volume, original acceptance stores, unrelated containers or contributor branches. Record retained paths and cleanup outcome. |

Each evidence entry records candidate SHA and compose diff/hash; image ID/platform; host/kernel/architecture/tool versions; operator; actual project/volume/mount/UID and container identity; command/time/exit/stdout/stderr or HTTP status/response; readiness/acquisition/allocation/audit identities; stop/restart times; source/image/snapshot hashes; restore progress/refusal details; retained paths and recipient signoff. Binary snapshot equality is a transfer check, not the required logical equality of a database after SQLite opens/restores it.

Stop on identity mismatch, unsupported target, unexpected/nonempty volume, unresolved runtime ownership, unwritable data, `DATA_IN_USE`, readiness failure, missing allocation/audit after restart, transfer hash mismatch, partial restore, or any attempt to overwrite an existing destination or touch retained stores. Preserve failure evidence and route the specific source defect to its existing owner; do not broaden into application E2E.

Complete dependency/container notices remain a separate documentary gap. Human presenter fluency/training, live integrations, scale/enterprise identity/crash endurance and customer Phase 1/2 acceptance remain outside this protocol. Nothing in this document records a successful portable or recipient execution.
