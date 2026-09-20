# Core state compatibility with schema v5

**READY FOR PROJECT-LEAD REVIEW — Stage 5 audit follow-up.** Core storage evidence for G27 / RFP-018 and F1/F3/F5 dependencies; global acceptance and merging belong to Main Lead 2.0.

## Pickup and dependency

- Branch: `codex/part-1-state-schema5`; isolated worktree `~/Downloads/Ip_inventory-state-schema5`.
- Exact approved dependency: `7dc057c6b18b0b3f0c0425bb17d0b427c4908969` on `codex/audit-shared-integration` (Stage 4 owns store/schema/migration).
- Code and executed-test checkpoint: `d6197df8b7d78e1f1558f45c2c7c3e72c3121151`. The following documentation commit publishes these results; the PR head identifies that documentation revision.
- Genuine legacy v4 source: `a279f32df0ac7d2147b580dbff36dd88772bdeb2`, archived from Git into a new fixture directory. No existing acceptance store was copied or changed.
- User authorization: the F1–F7 audit-response request explicitly permits focused local checks on fresh disposable synthetic stores/copies. This supersedes the earlier source-only restriction for this slice. No cloud/VM/Docker/image pulls/public exposure/spending was used.

Core coordinated pickup and the exact shared schema with Main Lead 2.0 and Stage 4 before dependent edits. Stage 5 was told which storage evidence it can reuse. Core changed only migrate help, the two focused test files and owned state documentation. `state_ops.py` already consumes shared `SCHEMA_VERSION`, `MIGRATABLE_SCHEMA_VERSIONS` and `require_schema`, so no state algorithm or private table list was added. Schema/store/seed, imports/rules, frontend, root `fixtures/`, dependency locks and Spencer's files were not edited by core.

Read `AGENTS.md`, `DEVELOPMENT_RULES.md`, `docs/CONTRACTS.md`, `docs/IMPLEMENTATION_DECISIONS.md`, `docs/STATE_OPERATIONS.md`, this handoff, then the shared v5 source. Shared checkpoint code alone does not contain the complete new F1/F3/F5 application paths.

## Observed result

Three stdlib unittest scenarios passed in **2.088 seconds**, exit 0, on Python **3.12.10**, macOS. No HTTP server or timer thread started. The helper performs one real manual acquisition with the genuine archived v4 application, then its existing allocation approval, exception handoff/acknowledgement, preset and disabled scheduling operations.

| Focused scenario | Observed result |
| --- | --- |
| Fresh seed and populated legacy migration | Fresh v5 rich seed has eight pools/history version 1; repeated seed rejects without mutation. Current backup/restore retains v4 and reports migration required. Current schema check refuses that v4 store. Explicit v4→v5 migration preserves every original column/row/ID; both conservative history backfill branches and exception defaults match the agreed schema. Repeated migration changes nothing. |
| Populated v5 backup/restore | Snapshot equals the full current database. Restoring over a newer populated target recovers the baseline and retains the complete newer database at `preserved_database`. Input snapshot remains unchanged. Comparison dynamically discovers all tables and columns, includes table SQL and `sqlite_sequence`, and compares application/schema identity. |
| Refusals and scoped reset | Removing a required v5 column from a disposable snapshot yields `INVALID_SCHEMA` with target unchanged. Missing confirmation and an actually held application file lock are refused. Confirmed reset removes only the recognized main database in this fixture; the unrelated note, retained backup contents and lock file survive. |

Legacy population contained four scopes, 60 prefixes, eight pools, two allocations, one allocation request, nine source batches, 12 coverage rows, **2,266 source records**, one saved calculation run, 17 audit events, ten exceptions, one preset, one schedule row and one committed schedule operation. All original columns in all 15 application tables plus `sqlite_sequence` survived migration. The retained schedule was disabled, interval 12 hours, config version 2, cycle index 1 and null next due time. Both nontrivial pool-version and prefix-version backfill controls received capacity-history version 2; unchanged controls received 1.

V5 round-trip input added three **direct SQL storage sentinels** for pending/approved/rejected correction rows, populated the new exception fields, and changed a history version. Those values establish storage preservation only. They do not demonstrate proposal authorization, approval atomicity, actual inventory correction, evidence resolution, close/reopen or notification behavior. All earlier saved evidence remains intact.

## Retained evidence and reproduction

Raw local artifacts are outside Git:

```text
~/Downloads/Ip_inventory-state-schema5-artifacts/run-w04Z5Z6U/
  test-output.txt
  state-schema5-is1r3_16/
    provenance.json
    legacy-source/                 # exact archived v4 code and synthetic fixtures
    legacy-populated/              # newly generated populated v4 store
    legacy-population.stdout
    legacy-population.stderr
    legacy-before.json
    migration-after.json
    roundtrip-baseline.json
    roundtrip-newer.json
    restore-result.json
    reset-result.json
    legacy-snapshot.sqlite3
    populated-v5.sqlite3
    roundtrip/                    # restored baseline + retained newer target
    refusals/                     # surviving unrelated note, backup and lock
```

`provenance.json` records the exact legacy/current SHA and Python version. Full JSON observations include actual values and IDs, not just counts. Source/DB artifacts are local synthetic evidence and are not committed. The original Stage 5 evidence remains a separate historical record.

The exact executed test invocation, from the isolated worktree after creating a new outer artifact directory, was:

```sh
IPAM_STATE_EVIDENCE_DIR="$HOME/Downloads/Ip_inventory-state-schema5-artifacts/run-w04Z5Z6U" \
PYTHONPATH="$HOME/Downloads/Ip_inventory-state-schema5/backend:$HOME/Downloads/Ip_inventory-state-schema5/fixtures/evolving" \
PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 \
"$HOME/Downloads/.venv/bin/python3" -m unittest discover -s tests -p test_state_schema5.py -v
```

The shell captured output with `tee` and `pipefail`. Do not rerun into that historical outer directory. If a relevant integration change requires a new check, use a **new** `mktemp -d` directory and an existing Python 3.12 environment. The test internally creates another unique directory; omitting `IPAM_STATE_EVIDENCE_DIR` instead uses temporary storage with cleanup. The pinned legacy Git object must be available. No dependency installation is required by this stdlib test file.

## Limits and integration

- No new service restart, timer, HTTP, CLI parsing or browser evidence at v5. The disabled-schedule fixture cannot establish enabled overdue startup or final F1/F5 business behavior.
- Invalid input coverage here is specifically a renamed required v5 column. It is not an exhaustive corrupt/foreign/unsupported-version/symlink test matrix.
- Comparisons include table definitions and every table value, but do not separately compare standalone index/trigger/view definitions. No forced copy/replace/fsync/WAL/crash/permission failures or cross-platform portability checks ran.
- V1/v2 migration and direct v3→v5 remain unrun here. Historical S5-16 demonstrates v3→v4 only; do not relabel it as v5 evidence.
- A source-only peer review found no actionable compatibility or test safety defect. That review did not execute additional checks. No broad suite or unchanged passing check was rerun.

Lead/Stage 4 integration: review this focused dependent PR against `codex/audit-shared-integration`. Preserve the approved shared schema checkpoint and merge the two core commits through lead coordination; do not copy a private schema policy into state operations. Migrate help adds v4 while keeping command dispatch unchanged. If the shared schema changes again, assess the concrete delta before rerunning only affected checks. Do not merge this lane directly to main ahead of its schema dependency.

Stage 5: reuse this exact checkpoint's storage observations. The final candidate still needs its separately authorized integrated correction/metadata/lifecycle/rehearsal evidence using a fresh disposable store. For recovery, stop the owned service, take the whole-database backup, restore into an owned copy, and preserve disabled scheduling plus the external pinned feed assets. Do not use these storage sentinels as the presenter demo or claim customer/portable acceptance.

Spencer: incorporate the current state interface and evidence limits in Part 6 under your ownership. No package runtime, recipient acceptance or `PART6_READY=yes` claim follows from this lane.

Draft integration prompt:

> Review codex/part-1-state-schema5 against the approved codex/audit-shared-integration dependency 7dc057c6b18b0b3f0c0425bb17d0b427c4908969. The executed code/test checkpoint is d6197df8b7d78e1f1558f45c2c7c3e72c3121151; read this handoff and the PR head for published documentation. Three focused disposable-store checks passed. Preserve shared schema ownership and old acceptance artifacts, distinguish v5 storage sentinels from feature acceptance, and integrate through Main Lead 2.0. Reuse the recorded storage evidence; run only checks justified by subsequent relevant changes. Do not self-merge, widen infrastructure permissions or overwrite Spencer's lane.
