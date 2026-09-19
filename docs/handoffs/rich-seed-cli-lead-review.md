# Core CLI and state source reviews

Date: 2026-09-19. Persistent lead: `01a0b845-6c8d-7021-a5c9-15e673db07c9`.

## PR #12 decision

[PR #12](https://github.com/yugant99/IpManagement/pull/12) at **`d7b1fd580b88f875883dbde975c9504ead58a6a9`** is accepted as a **source checkpoint**, not runtime acceptance. Exact base: rich helper `1d67cc45ffcf72409aad37555b996ccfefe882b6`. Code checkpoint: `0b64a3be26f666dd31af483a3b887cb0aa663b07`; later commit publishes the worker handoff. It was unmerged when reviewed. GitHub now records it merged into `codex/stage-3-main-capabilities` at `32d751fac381aef8bd53dcfdaa1f27639a64dc07`; application code remains outside main.

The lead and an independent reviewer inspected the complete two-file diff, current helper signature and call sites. No actionable findings: `--scenario` remains required; rich missing/empty `--inventory` and baseline with any `--inventory` fail before data-directory/helper access; helper dispatch and common error/nonzero handling are retained. Only `backend/ipam_demo/__main__.py` and the dedicated handoff change. No PR #10 state commands are introduced by this feature.

No tests, parser execution, Python import/compilation, builds, runtime, state or infrastructure commands were run. Actual exits/error output, seed input failures, initialized-state refusal, locking, transactions and resulting inventory remain unverified. Source acceptance gives no demonstrated questionnaire credit and does not set `PART6_READY`.

## Active Stage 3 and concrete compatibility issue

Stage 3 task `01a0b8f0-7036-74d1-81c1-e388d17b4cf4` owns its isolated application integration branch. Its first dependency merge is `5578431c85ffa18071d6262d08a49a251b072afd`. Schema v3 is published at `f241b0752c0e2aa46b3cbde7a67f30c6f5e6541e`; `STAGE3_API.md` at `08e9f0dad09dd872adeb0e465d7ca887e70ce26b`; shared `MIGRATABLE_SCHEMA_VERSIONS=(1,2)` at **`01550ab8b84936e289b4bbb74dfbfce9d6272940`**. The lead read the published helper and interface document. Module integration remains in progress; these are intermediate source artifacts, not Stage 3 acceptance.

PR #10 `state_ops.py` currently calls `require_schema` for v1 or the current schema only. Raising the current version to 3 therefore rejects recognized v2 stores and snapshots. The agreed repair uses the store owner's explicit migratable-version list plus current version, preserving identity/table, integrity/FK and exclusive-access checks. Legacy restores report `migration_required`; they do not migrate automatically. Both existing owners received this finding and agreed interface direction.

## Exact approved compatibility pickup

Owner: **Foundation 1**, task `01a0b8ae-bd65-7331-b548-da5dca1e0d5e`. Keep PR #10 and PR #12 branches unchanged.

The worker published combined base **`f1d7ce14eaba079626938fad9a1c9ee7a9303228`** before compatibility edits. The lead read its two exact parents and pushed branch; the normal merge preserves `01550ab8b84936e289b4bbb74dfbfce9d6272940` and `0e139a85b445f7d07968c855e770c525c5e4d91c`. The later fix review is recorded below. This approved recipe is historical pickup context, not a request for another worktree or repeated merge.

1. Create isolated `/Users/yuganthareshsoni/Downloads/Ip_inventory-state-schema-compat` on `codex/part-1-state-schema-compat` from exact **`01550ab8b84936e289b4bbb74dfbfce9d6272940`**.
2. Normally merge exact unchanged PR #10 **`0e139a85b445f7d07968c855e770c525c5e4d91c`** on that feature branch, preserving commits. The lead explicitly approves this source-dependency combination. It is not acceptance of PR #10 or permission to merge an application PR into main. PR #12 remains a separate dependency.
3. Record and push the actual resulting combined-base SHA before the compatibility delta. Do not invent the future SHA. The pinned recipe is already approved; another permission round is unnecessary unless a conflict changes another owner's files or the agreed behavior.
4. Own only `backend/ipam_demo/state_ops.py`, `docs/STATE_OPERATIONS.md` and `docs/handoffs/part-1-state-schema-compat.md` for the fix. Consume the shared version list; do not duplicate the historical-version policy, broaden acceptance to arbitrary versions or edit store/schema/CLI/fixtures/UI/packaging.
5. Publish a dependent PR against `codex/stage-3-main-capabilities`, separating inherited PR #10 changes from the narrow fix and exact combined base. Report source findings and pending execution evidence to this lead. No tests, builds, state/runtime/infrastructure commands or PR merges are authorized.

The lead remains responsible for application PR review and eventual integration. Combining CLI and state lanes later must retain rich seed, backup/reset/restore, serve and explicit migrate together; never replace the entire CLI with one branch's copy. Spencer retains packaging and operator ownership. The denominator remains 111 with partial/documentary limits intact.

## PR #16 source decision

[PR #16](https://github.com/yugant99/IpManagement/pull/16) at **`e6029d855abf13581b95fda20ade52f5a6c5792e`** is accepted as a **source checkpoint**, including the inherited state operations reviewed in this corrected v3 context. The narrow code/docs fix is `1177d2029c1f6283afb5ed6e993a10678a77b4e9`; the final commit adds the worker handoff. It was unmerged when reviewed. GitHub now records it merged into Stage 3 at `75a2e1395dd7a47bd40b2aa7343f8eb0f636b6f2`. PR #10 remains unchanged/open; PR #12 is merged into Stage 3. None is integrated into main.

The lead inspected the exact three-file compatibility delta and inherited CLI wiring. An independent backend reviewer read the full inherited `state_ops.py`, shared schema/migration helpers, CLI/error paths and state docs. No actionable source findings: explicit legacy versions use the store-owned allowlist, current schema remains checked, unknown versions fail, and restore reports migration requirements without upgrading. Snapshot validation, stopped-service locking, preservation before replacement, confirmation/refusal paths and post-publication progress/error flags are coherent by source inspection.

No state/application command, migration, test, build, Python import/compilation, syntax/type check, browser or infrastructure action was executed. This review does not prove actual round-trips, data preservation or failure behavior. Required evidence remains v1/v2/v3 backup/restore/reset, populated workflow/audit/exception/preset content and IDs, legacy restore followed by explicit migration, current restore over an existing v2 target with original retention, invalid/foreign/unsupported input refusal, lock/confirmation behavior, WAL/recovery handling and copy/permission/replace/sync failure outcomes. `PART6_READY=no`; no demonstrated questionnaire credit.

The lead permitted normal history-preserving combination of exact PR #12 and PR #16 source checkpoints on Stage 3's isolated feature integration branch. PR #16 already inherits PR #10. Those combinations are complete; the core owner resolved the reserved CLI import conflict and migration help text. The lead read the resulting CLI and confirmed that rich seed, state commands, serve and migrate remain wired in source. No runtime behavior was exercised.

Correction to the earlier integration instruction: pushing normal Git merges into the PRs' target branch caused GitHub to mark the component PRs merged. The earlier assertion that those PRs would remain open was wrong. This records actual branch/PR state; it does not grant main integration or runtime acceptance. See the Stage 3 lead review for the resulting application checkpoint and remaining evidence.
