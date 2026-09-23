# Agent ownership of operator preparation — 2026-09-23

The user clarified that Spencer had not actually been assigned the prepared work
and explicitly directed the agents to do it, leaving a different Spencer assignment
for tomorrow. This supersedes the former Spencer dependency for T020/T022/T024.
The prepared Spencer worktree remains untouched at
`ab005d8bf3b6c57e0a071707796d18514c278674`, with no implementation or acknowledgement
inferred. No message was sent to Spencer and no tomorrow task is invented.

Astra/Main Lead 5.0 remains accountable. Complete feature assignments, each in a
new isolated `codex/` worktree with explicit owned paths and pinned prerequisites:

| Task | Author | Release condition | Owned output |
|---|---|---|---|
| T020 integration matrix | Muse 1.3 high, OpenCode | Accepted T002 and current source base | `integration-matrix.md` |
| T021 offline API | Opus 5.5 high, Claude Code | Reviewed T020 plus T009/T014/T017A | `offline-api.md` |
| T022 recipient preparation | Muse 1.3 high, OpenCode | Reviewed T020 plus T010/T015/T017A | `recipient-validation.md`, `configuration-example.json` |
| T024 operator/package implementation | Muse 1.3 high, OpenCode | Reviewed T021/T022/T023 | Nine narrowly bounded paths below; user hold before dispatch |

GPT-6 Sol high independently reviews each full result and shared invariants before
source integration. Native Luna high remains available for independent T025 or an
explained fallback; original authors retain fixes. Public tracked synthetic source
only may reach the existing paid-training Muse route. No private documents,
credentials, untracked outputs, account settings changes, purchases or resets.
Fresh preflight: Go rolling 3%, weekly 41%, monthly 21% used, credits disabled and
balance zero; Claude session 5%, weekly 31%, Fable 24% used, credit balance zero and
auto-reload off. Preserve the 20% reserve; exact sessions/bases go in first-wave.json.

This changes ownership, not task dependencies or the passing bar. T025 remains
blocked until the complete prerequisite candidate is source reviewed. No routine
tests/builds/imports/typechecks, database execution or application runtime before
that gate. T025 uses disposable synthetic data only; no deployment, new infrastructure
or customer access follows. T028 remains the next bridge-to-main merge.

T026 is still an actual human-evidence gate. Astra will record the true participant,
candidate, target and acknowledgement when available, or a pending disposition
limiting the package claim. Agent preparation or reproduction cannot manufacture
human receipt, business signoff or portable acceptance. Tier B remains locked and
all questionnaire ledgers retain their existing evidence classes.

## T024 user hold and bounded next lease

The latest user instruction is to finish T021/T022 and stop at T024-ready, then
pick up T024 tomorrow. T023 is already source-reviewed; it is not runtime-verified.
Do not dispatch or implement T024, or run T025, while this hold remains in force.
Resume only when the user continues the task. Refresh exact routes and usage then.

The future full T024 assignment remains Muse 1.3 high, independently reviewed by
GPT-6 Sol high, with one new isolated worktree and one exact source base containing
reviewed T021/T022/T023. Its bounded lease is:

- `scripts/ops/acquire.sh`, `scripts/ops/health.sh`, `scripts/ops/README.md`;
- `specs/001-postmeeting-bridge/delivery/operator-handoff.md`;
- `Dockerfile`, `compose.yaml`;
- `docs/RUNNING.md` for bridge readiness/auth/config instructions only;
- `scripts/ops/start.sh` and `scripts/ops/backup.sh` for textual readiness/actual-volume
  messages and comments only, without changing their operational flow.

The three added paths remove stale claims that `/healthz` establishes readiness or
that the data volume must be `ipam_demo_data`. This is a bounded lead lease decision,
not a new feature or permission to run packaging. Reuse existing helpers; do not
create a new ops framework or change `common.sh`.

Future Compose wiring must require an explicit `IPAM_DATA_VOLUME`. A candidate uses
a new, recorded disposable volume name; reuse is deliberate and recorded. A different
Compose project name alone does not isolate a globally named volume. Keep loopback,
read-only root, single process and separately provisioned reviewed configuration.
No token belongs in Compose environment, images, CLI arguments, logs or snapshots.
Observed host/Compose/runtime versions belong to the later authorized T025 gate,
not to T024 source preparation. An unavailable target does not prevent source work
once resumed, but prevents target-specific runtime/portable claims.
