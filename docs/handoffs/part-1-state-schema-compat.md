# State schema compatibility handoff

**READY FOR PROJECT-LEAD REVIEW — State schema compatibility.** Source-only checkpoint; no runtime acceptance, application PR merge or release claim.

## Exact pickup and publication

| Field | State |
|---|---|
| Repository | `https://github.com/yugant99/IpManagement` |
| Worker | `Foundation 1`, task `01a0b8ae-bd65-7331-b548-da5dca1e0d5e` |
| Isolated worktree | `/Users/yuganthareshsoni/Downloads/Ip_inventory-state-schema-compat` |
| Branch | `codex/part-1-state-schema-compat` |
| Stage 3 helper dependency | `01550ab8b84936e289b4bbb74dfbfce9d6272940`, `codex/stage-3-main-capabilities` |
| State-command dependency | [PR #10](https://github.com/yugant99/IpManagement/pull/10), `0e139a85b445f7d07968c855e770c525c5e4d91c` |
| Combined base, pushed before edits | `f1d7ce14eaba079626938fad9a1c9ee7a9303228` |
| Compatibility code/docs checkpoint | `1177d2029c1f6283afb5ed6e993a10678a77b4e9` |
| Dependent PR target | `codex/stage-3-main-capabilities` |
| Separate rich-seed CLI | [PR #12](https://github.com/yugant99/IpManagement/pull/12), unchanged at `d7b1fd580b88f875883dbde975c9504ead58a6a9`, not included |

The final published SHA and dependent PR URL are supplied in the worker response and PR description. This handoff follows the code checkpoint in a documentation commit. Read current refs before integration; do not reset another worker's checkout.

The persistent lead explicitly approved a new worktree from the exact Stage 3 helper SHA, followed by a normal merge of the exact unchanged PR #10 SHA. That dependency merge preserved both histories, had no conflicts, and was pushed/reported before the fix. It was a source-work dependency combination on this feature branch, not a PR merge into main or acceptance of PR #10. The original PR #10 and PR #12 branches/worktrees remain unchanged.

## Narrow fix versus inherited work

The compatibility delta owns only `backend/ipam_demo/state_ops.py`, `docs/STATE_OPERATIONS.md`, and this new handoff. No store/schema/fixture/UI/packaging/global-status files or CLI commands were edited by the fix. G27/RFP-018 state correctness is affected; zero questionnaire rows are demonstrated by source review.

PR #10 supplied the full backup/restore/reset implementation, its minimal CLI wiring, state documentation and original handoff. Those inherited files are visible in a PR diff against Stage 3 and must not be mistaken for newly authored compatibility code. The full state design and its original review/evidence limits remain in [the original state handoff](part-1-state-commands.md).

The new code changes one import and the schema selection in `_validate`. Previously the state lane accepted v1 or the current schema, so raising `SCHEMA_VERSION` from 2 to 3 would reject recognized v2 backup/reset/restore inputs, including an existing v2 database that must be preserved before restoring v3.

The selector now consumes the store owner's `MIGRATABLE_SCHEMA_VERSIONS` (1 and 2) and `SCHEMA_VERSION` (3). Declared legacy versions are passed explicitly to `require_schema`; all other values use the current-version check, which rejects unknown versions. The shared helper remains responsible for application identity and the required tables. State operations do not maintain a second list of supported versions or table requirements.

SQLite integrity/FK checks, stopped-service locking, confirmation, original-preservation behavior and all inherited CLI dispatch remain unchanged. Restore preserves the input schema version and returns `migration_required: true` for v1/v2; only the separate explicit migrate command advances it. Whole-database snapshots already include v3 request/audit/exception/preset tables when present; no selective-copy logic was added.

## Evidence and remaining gaps

Observed: exact dependency refs, conflict-free merge history, published combined base, authored narrow diff and independent source review. The reviewer found no actionable findings in version selection, retained checks or documentation. No application behavior was executed.

Not run: state/seed/migrate/serve commands, application installation/imports/compilation, tests, syntax/type checks, builds, smoke/browser checks or infrastructure operations. No tests were added and no application database was created. This pinned Stage 3 checkpoint also contains API wiring with its own pending module integration; the dependency combination is not a complete verified application candidate.

Remaining evidence includes v1/v2/v3 backup and reset behavior, legacy restore plus explicit migration, v3 restore over an existing v2 target with original retention, populated v3 table/content/ID round-trips, unknown/foreign/malformed-store refusal, confirmation and active-service refusal, WAL/recovery handling, permission/copy/replace/sync failure behavior and untouched unrelated files. All earlier state-command evidence gaps remain. `PART6_READY` is unchanged; no measured recovery objective or portable-release acceptance is claimed.

## Integration instructions

1. Review inherited PR #10 separately from this fix. The combined base `f1d7ce14eaba079626938fad9a1c9ee7a9303228` contains only the approved pinned dependency merge; compare it with `1177d2029c1f6283afb5ed6e993a10678a77b4e9` for the compatibility code/docs change, then read this later handoff commit.
2. Keep `01550ab8b84936e289b4bbb74dfbfce9d6272940` or a compatible descendant providing the shared constant. Do not apply the new state import onto the old Stage 2 store, which does not export that interface. Preserve both inherited histories and let the lead coordinate the dependent PR against Stage 3; this worker does not merge PRs.
3. PR #12 remains separate. When the lead combines it, preserve both its rich-seed parser/dispatch and the inherited state commands, along with existing serve/migrate behavior. No rich-seed CLI is implied by this branch alone.
4. The original state handoff describes its historical schema-v2 checkpoint. For this combined branch, [STATE_OPERATIONS.md](../STATE_OPERATIONS.md) and this report record the updated schema policy and evidence limits. Spencer retains packaging/operator files; runtime validation still requires explicit authorization.

Next owner: persistent project lead for bounded review and integration, coordinating the Stage 3 owner. No source blocker remains within this assigned compatibility delta. Keep the state owner available for concrete review fixes; no new stage or unrelated feature is started here.
