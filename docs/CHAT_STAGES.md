# When to start a fresh implementation chat

**User-authorized lead replacement, 2026-09-19:** [Main Lead 2.0 transfer](handoffs/main-lead-2.0.md). Receiver `01a0bb80-cf0d-7f60-8e46-1e825f42d276` is registered; the outgoing lead is reference-only. This is an explicit exception to the ordinary stage-transition rules below, not a new implementation stage. Existing worker ownership and accepted evidence carry forward.

The existing project-lead chat remains responsible for oversight across the whole build. The user wants fresh implementation chats for the stages, not a replacement lead each time. See [PROJECT_OVERSIGHT.md](PROJECT_OVERSIGHT.md). Agents must surface checkpoints themselves and generate handoff prompts; do not wait for the user to reconstruct context.

**Find the active implementation boundary and generated prompt in [CURRENT_HANDOFF.md](CURRENT_HANDOFF.md).** The first boundary is planning → Stage 1. Keep this original chat as persistent project lead; it reviews worker reports and updates global status/handoff pointers.

## Stage map

Hours are approximate elapsed lead working hours from implementation start, not a new 20-hour allowance per chat. Stages describe implementation work supervised by the persistent lead; the six parts describe ownership and can run in parallel.

| Stage / suggested chat title | Work | Checkpoint required before the next chat |
|---|---|---|
| 0 — IPAM planning and architecture | Questionnaire mapping, contracts, ownership and development rules | Decisions merged; Stage 1 scope and pickup prompt generated. This checkpoint is reached |
| 1 — IPAM foundation | Hours 0–2: backend/UI entrypoints, dependency locks, scoped inventory schema, minimal synthetic seed and runtime/data/static/health contracts | Owned foundation code pushed, actual entrypoints/dependencies documented, interfaces usable by the next lane, missing commands and verification state explicit |
| 2 — IPAM first complete path | Hours 2–6: source import → stored evidence → one calculated finding → browser detail | Connected code on an identified integration/dependency baseline; one fixture and result explained. Record observed evidence if authorized; otherwise mark runtime evidence pending. Cut optional breadth if the path is still disconnected around hour 6 |
| 3 — IPAM main capabilities | Hours 6–11: six rules and unknown controls, shared forecast, inventory/IPv6/history additions, local allocation/audit, exception queue | Required lanes integrated or exact unmerged dependencies listed; questionnaire changes and gaps recorded; actual workflow records available before claiming persistence evidence |
| 4 — IPAM scheduling, integration and freeze | Original hours 11–14 integration window, now including the user's required evolving synthetic feed, configurable six-hour scheduling and Run now under SCHEDULING_CONTRACT.md; integrate ready dependencies and resolve concrete clashes | Freeze unrelated additions; record exact scheduler/feature candidate, ownership, missing package/evidence and bounded acceptance plan. Preserve final integration reserve; do not restart the weekend budget |
| 5 — IPAM acceptance and delivery | Hours 14–20: repair, authorized focused acceptance, recipient startup/persistence, evidence ledger and runbook | Record the exact release/candidate and actual outcomes/limits. If checks were not authorized or successful, retain pending evidence; do not claim the release passed. Generate a maintenance handoff rather than inventing another build stage |

A checkpoint can be **code ready, runtime evidence pending**. That permits a new chat to continue independent implementation; it does not satisfy a runtime acceptance gate or waive merge rules. Do not stay in one chat indefinitely waiting for another lane. Hand off a real blocker and the exact work that can proceed.

Spencer starts Part 6 documentation/package preparation alongside Stage 1. `PART6_READY` is set when real core prerequisites exist, not when the calendar reaches Stage 4. Core supplies database/state-command correctness. G27 persistence acceptance additionally needs G21/G22 allocation/audit records. No presentation work is assigned to Spencer.

## Automatic callout at a boundary

At the end of every implementation turn, compare actual progress with this stage map. When the checkpoint is reached, or context is repeatedly causing lost constraints and a safe checkpoint is available:

1. Finish or explicitly checkpoint the owned slice. Preserve dirty work; record unfinished files. Commit coherent changes and push before handoff even if fewer than three commits. If push fails, show the blocker and local SHA; do not call the handoff portable.
2. Read actual Git branch/HEAD/upstream status, integration base, worktree ownership and PR/dependency state. The worker updates its stage/lane report on its own branch and submits proposed global changes. Only the persistent lead updates `docs/STATUS.md` and `docs/CURRENT_HANDOFF.md` after review.
3. Generate the next prompt from those facts. Include the next stage's exact work and stopping point, not a generic "continue the project" instruction. Do not ask the user to write it.
4. Publish the handoff. Capture the final pushed code checkpoint separately from any later documentation-only publishing commit; do not try to place a document's own unknown future commit hash inside itself.
5. The worker ends with **READY FOR PROJECT-LEAD REVIEW — Stage N**, its SHA/PR and report, plus a draft next-stage prompt. The persistent lead reviews the claim and, when the next baseline is accepted, emits this callout and the final complete copyable prompt:

> **START A NEW IMPLEMENTATION CHAT — Stage N: title**  
> The previous implementation stage has reached its reviewed checkpoint. Keep its chat for related fixes; this project-lead chat continues overseeing the build.  
> State: implemented / demonstrated / unverified / blocked, as applicable.  
> Next chat: paste the generated prompt below. Handoff: link. Pushed checkpoint: branch + SHA.

Do not begin the next implementation stage in the old worker chat unless the user asks to continue there. The project-lead chat stays active as coordinator across boundaries. Do not create, archive or rename chats automatically; if the user separately requests a new chat, create it with the generated prompt. Periodic read-only oversight is a separately configured heartbeat, described in `PROJECT_OVERSIGHT.md`; stage switching itself creates no background process or token monitor.

## Required handoff facts

Use a short file named `docs/handoffs/stage-NN-description.md`; the lead publishes its accepted pointer/summary in `docs/CURRENT_HANDOFF.md`. The first real example is [Stage 1](handoffs/stage-01-foundation.md). Later files are generated at their checkpoints, not filled with invented future SHAs now.

- Source stage/chat purpose and next stage; repository URL and actual checkout/worktree location in the user-facing prompt.
- Exact code checkpoint branch/SHA, integration base SHA, contract revision, pushed status, PR/merge state, unmerged dependencies and dirty/untracked work that must be preserved.
- Implemented behavior versus actual observed behavior; synthetic/simulated paths, missing entrypoints, known failures and questionnaire row changes. No inference from a polished screenshot or a planning checkbox.
- Next outcome, owned files, other active owners, allowed independent work, explicit exclusions and exit checkpoint.
- Commands already run and their outcomes; check/runtime/infrastructure authorization carried from the current user's instructions. Never silently broaden permissions or turn an unrun check into a passing one.
- A complete next-chat prompt, with no placeholders the user must fill. One link is convenient, but the visible prompt must also identify the repository, stage and next deliverable so it can be pasted elsewhere.

When a handoff file contains an earlier code checkpoint followed by a docs-only publishing commit, the receiving agent inspects current remote state and confirms the recorded checkpoint is an ancestor. It starts from the current agreed baseline, not by resetting the user's checkout to an old hash. If new relevant work changes the scope, reconcile with the current lead before editing.

## Rules for the receiving and previous chats

The receiving agent reads applicable ancestor/root/nested `AGENTS.md` instructions, current Git state, `CURRENT_HANDOFF.md`, `STATUS.md`, the stage handoff and relevant contracts before editing. The latest user instruction is authority; status/handoff files record it and may be stale. A new chat is not a new planning interview or a new permission request for already-authorized work.

Use separate feature branches and isolated worktrees for parallel contributors. A chat is not a Git branch: one stage may coordinate several feature branches, and a small fix can continue in the same chat. Do not open a new chat for every commit, push, error or pull request. If the next feature needs an unmerged prerequisite, name its exact branch/SHA and coordinate the dependency rather than silently starting from an empty `main`.

The previous worker chat becomes available for explicitly assigned follow-ups. Before editing there, re-read current status/Git and coordinate shared-file ownership with the persistent lead. Fixes to an already merged feature use a new `codex/` fix branch from the current baseline; do not append work to a retired branch or force-push shared history. Report the fix SHA/PR and affected contract/evidence changes to the same project lead.

Keep the scope already agreed: synthetic data; one app/database; questionnaire-first accounting; three coherent changes per push; targeted skills; Spencer's Part 6 ownership; feature freeze at lead hour 14. The present user rule does not authorize adding/running application tests or smoke/verification commands unless explicitly requested. Cloud spending, container/VM operations and public deployment are not granted by a stage transition. Record pending gates without repeatedly asking the same permission question.
