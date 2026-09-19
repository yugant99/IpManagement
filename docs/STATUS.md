# Current project status

## Authorization and evidence

- Latest user direction: keep the original task as overseer; Stage 1 has handed off, Stage 2 is active, and synthetic data proceeds in parallel. Lead identity is `01a0b845-6c8d-7021-a5c9-15e673db07c9`, currently titled **Synthetic data builder**. Sidebar titles have changed; use task IDs/assigned ownership, not title wording, to route work. Do not duplicate workers or repeat planning.
- Status is a record, not independent authority. Current user instructions govern. Application tests/smoke/verification commands have not been explicitly requested; existing test limits remain. No container/VM operation, cloud spending or public deployment is granted by the stage handoff.
- Stage 1 source implementation is pushed in draft PR #5; runtime evidence and integration remain pending. The separate synthetic-data task is active. No application runtime, test, container build or deployment evidence has been accepted by the lead.
- Do not interpret a goal, command or contract in these documents as an implemented capability.
- Cloud rental/public deployment is outside the present work. Local source material remains outside the public repository.

## Integration

- Repository: `yugant99/IpManagement`.
- Project lead: original task `01a0b845-6c8d-7021-a5c9-15e673db07c9`, currently **Synthetic data builder**, persistent across all stages. It owns global status/acceptance/integration; worker chats own assigned implementation and reports.
- Stage 1 worker **Foundation 1**, task `01a0b8ae-bd65-7331-b548-da5dca1e0d5e` on host `local`, has submitted [draft PR #5](https://github.com/yugant99/IpManagement/pull/5). Published branch `codex/part-1-foundation` at `c6131c38a460c13c3a189ee64a530042b2a2bf0f`; source code at `ea51aa64b1780fa5c171e95ae59a619bf0109d52` plus report/next-stage draft. Integration base `50a1dce9406ea8e9e52c032c321bb6ebfea063f8`. Worker stopped at checkpoint and remains available for foundation fixes. The feature is unmerged; it is not present on documentation-only `main`.
- Lead source review found no actionable API/CLI, seed/store/schema or frontend/static-wiring defects at `c6131c3`. This checkpoint is accepted as an explicitly coordinated dependency for continued implementation, not as demonstrated runtime behavior. Main integration and runtime acceptance remain pending. See [lead review](handoffs/stage-01-lead-review.md).
- Stage 2 owner: **Implement Stage 2 first path**, task `01a0b8c2-f283-7cf1-9128-85e9164f5fe9` on host `local`, branch `codex/part-2-first-path`, isolated Stage 2 worktree. Lead approved the exact unmerged foundation dependency above, additive routing/policy imports, saved missing-expected-route results/evidence UI and explicit stopped-service v1-to-v2 migration. No runtime/check authority added. Shared interface choices are recorded by this worker before delegation.
- Synthetic-data owner: **Overseer**, task `01a0b8b9-82fb-7a11-bc50-ec3a5b234729` on host `local`, branch `codex/part-2-synthetic-data`, isolated worktree. Despite its current title, this task owns data generation, not project oversight. Initial lead subagent is stopped. Owns `fixtures/`, `docs/SYNTHETIC_DATA.md` and `docs/handoffs/part-2-synthetic-data.md`. It consumes Stage 1's seed shape/UUIDs and fixed clock `2026-09-01T00:00:00.000Z`; core retains packaged seed ownership. It coordinates a small first-path policy/routing subset against the existing six-prefix ledger with Stage 2. Richer inventory is not silently promoted into active state. See the [data pickup](handoffs/part-2-synthetic-data.md).
- Read-only oversight heartbeat: created for this project-lead task; 30-minute checks through Monday morning, 2026-09-21. It reports meaningful checkpoints/blockers only and performs no implementation, tests, merges or deployment. The app automation is the live schedule source.
- Initial integration branch: `main`, documentation bootstrap only.
- Feature branches: `codex/part-N-description`; Spencer's planned branch is `codex/part-6-portability`.
- Obtain the current baseline with Git at pickup; do not assume a hash from a prior chat.

## Decisions and ownership

- The initial two-round discussion was followed by 75 individual questions and actual answers across three dependent batches of 25. Corrections and decisions are integrated into architecture, contracts and part handoffs; see `GRILL_75.md`. No user questionnaire or confirmation gate remains.
- Persistent lead: contracts, integration coordination, acceptance, questionnaire evidence and global status. Stage workers implement their assigned portions, including Part 1, without replacing this role.
- Data lane: Part 2. Rules lane: Part 3. UI/calculation lane: Part 4. Core workflow lane: Part 5.
- Spencer: **Part 6, portable delivery**, approximately 6–8 hours. Earlier Part 5 assignments are superseded.
- Primary coverage is the 111-row questionnaire, not 22/30 internal goals. The revised row map targets 65 rows with concrete scoped demo/document evidence, two conditional additions to 67, and optional scheduling to 68. These include partial/documentary evidence, not whole-row compliance. No row has yet been demonstrated by this project.

## Readiness

| Gate | State | What is missing |
|---|---|---|
| Architecture decisions | 75-question pass and questionnaire reprioritization integrated | Bounded implementation refinements; no new runtime services required |
| Application build | Stage 1 source reviewed; Stage 2 implementing first path | Required runtime evidence, main integration and completed source-to-finding path |
| Synthetic scenario pack | Separate worker generating artifacts | Dataset/contract review; application import/rule evidence later |
| PART6_READY | No | Reset/backup/restore implementation and compiled UI/runtime/persistence evidence; serve/seed/health/locks exist in unmerged Stage 1 source |
| Portable release | Not built | Implemented application, packaging and recorded startup/persistence evidence |
| Questionnaire evidence | 0 rows demonstrated/substantiated by this project | Deliver planned behavior/documents and retain remaining gaps per row |

Next: follow the lead's `CURRENT_HANDOFF.md` decision and exact Stage 2 dependency. Do not start application work from documentation-only main or duplicate the active data lane. Use contract revision `demo-v2-questionnaire`; preserve the hour-14 freeze and integration reserve. Spencer can prepare packaging in parallel, but acceptance waits for real prerequisites/evidence. Workers submit pushed SHA/PR and reports to this persistent lead; the lead reviews claims, updates this status and generates the accepted next prompt. See `PROJECT_OVERSIGHT.md`.
