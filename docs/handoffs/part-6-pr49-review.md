# Part 6 PR #49: lead review and bounded compatibility repair

Reviewed 2026-09-20 by Main Lead 2.0 (`01a0bb80-cf0d-7f60-8e46-1e825f42d276`).

**Verdict: needs changes; no merge or portable acceptance.** Spencer's PR #49
head `c123a39fee8943418deac3c71e6d6ff74213b72c` is a source-only packaging
checkpoint based on Stage 2 `8a1a122737618748c58c5a8fc31b58a3b5f6f37e`.
Its own handoff explicitly records no image build/start/persistence evidence.
The accepted main is `376dd52f9457dd0b7fecc8d83a3e0d6970bb487e`, runtime-equivalent
to application candidate `289f53c7c5db1bd414c938add1ea207d591f9e64`.

The user authorized this review, a separate small-fix PR and merge only when
required evidence supports acceptance. Docker/VM/cloud execution, spending,
external collaborator messages and larger rewrites remain outside this turn.

## Findings and small fix

Original PR line references below refer to `c123a39`, not the repaired file.

| Finding | Original evidence | Action |
|---|---|---|
| P1: excluded build input | `.dockerignore:64` excludes `README.md`, but `Dockerfile:35` copies it and project metadata requires it | Keep README in context |
| P1: runtime depends on absent build source | `Dockerfile:37` uses editable `uv sync`; line 60 copies only its environment, without `/build/backend` | Install non-editably; consume unchanged locks with uv 0.7.13, the accepted native tool version |
| P1: current producer and immutable inputs absent | Build copies only backend at line 36; runtime lines 60–67 omit the producer, nine pinned feed assets and feed directory setting | Copy the declared producer package into build; package rich inventory plus policy/eight observation inputs; set `IPAM_SYNTHETIC_FEED_DIR` |
| P2: unsafe lock-recovery advice | `docs/RUNNING.md` instructs removal of the lock file after `DATA_IN_USE` | Explain kernel lock release and identify the actual holder; never replace the lock inode to bypass it |
| P2: stale dependency claims | Runbook says reset/backup/restore do not exist and migration is only v1→v2 | Record available schema-5 core interfaces and separate missing package procedures |
| P2: private local material not explicitly excluded | `.dockerignore` omitted local `audit/` and `outputs/` | Exclude both from the build context |

Source confidence is high for these concrete path/contract discrepancies. No
container failure was reproduced and no container success is claimed. The
non-editable installation choice follows [uv's Docker guidance](https://docs.astral.sh/uv/guides/integration/docker/#non-editable-installs);
build-context exclusions follow [Docker's context rules](https://docs.docker.com/build/concepts/context/#dockerignore-files).

The fix branch `codex/part-6-build-compat-fix` starts from accepted main and
merges the exact Spencer head locally before the repair, preserving his three
commits. A separate draft PR carries this combined candidate; it does not
authorize merging either PR. No backend/frontend/fixture/lock content changes.

## Focused evidence actually obtained

Using existing native CPython 3.12.10 and uv 0.7.13, an offline disposable build
copied the same Python source/metadata set and ran
`uv sync --frozen --no-dev --no-editable --offline`. After moving the build
source directory away, isolated Python imports resolved both `ipam_demo` and
`ipam_synthetic_feed` from the installed environment. The real feed adapter
loaded and hash-validated all nine original rich-v1 envelopes. CLI help exposed
`serve`, `seed`, `migrate`, `backup`, `restore` and `reset`.

Retained disposable probe: `/tmp/ipam-part6-package.J52kFK` (temporary, local;
not a portable artifact). No service, timer, app database, Docker command,
image pull or infrastructure was started. This verifies native package
independence and input compatibility only. `git diff --check` passed.

Independent review was requested in an app-visible GPT-6 Astra task at low
reasoning, in the registered project's isolated worktree. At publication the
app returned only queued client ID `client-new-thread:d67f1095-f7ba-4995-8d1e-f0feb9c7ea6b`;
no completed independent verdict is claimed.

## Remaining Spencer work and release gates

This is larger than the small build repair: one remaining Part 6 operator/state
delivery slice plus an authorized target-host evidence session, not a core
application rewrite. Preserve Spencer's ownership. Required outputs:

1. Consume current main/schema-5 and the fixed package. Replace stale Stage 2
   pickup instructions in the lane handoff and ops README. Keep the historical
   provenance distinguishable from current instructions.
2. Supply the accepted rich-demo setup/acquisition procedure. Existing
   `seed.sh` defaults to the older foundation baseline, so that quickstart
   alone does not reproduce the accepted rich demo.
3. Wrap/document stopped-service backup/restore/reset with explicit confirmation,
   usable snapshot paths across host/container boundaries and retained replaced
   state. Core commands already exist; no competing SQLite implementation.
4. Finish consistent operator guidance: `start.sh` currently suggests seeding
   after starting even though the service holds the lock; `logs.sh --no-follow`
   examples and the claimed legacy Compose fallback require correction or
   evidence against a declared supported Compose version. Complete the promised
   dependency/license inventory at the agreed scope.
5. Publish exact image/source identity, host OS/architecture and results for
   image build, UI/API/health and setup-needed behavior, rich-feed operation,
   restart preserving actual G21/G22 allocations/audit, populated snapshot
   recovery/reset and actionable data-path refusal. Record recipient/operator
   reproduction. Seed-only restart and native macOS evidence are insufficient.

No second architecture/host expansion, new core features or broader pipeline
is assigned here. `PART6_READY=no`, questionnaire accounting remains
32 Demonstrated / 22 Partial / 10 Documentary / 47 Missing out of 111, historical
Stage 5 stays 14 passes/two partial and customer DOCX Phase 1/2 gaps remain.
PR #9 remains NO MERGE. Post-Part-6 UI wording/search polish remains deferred.
