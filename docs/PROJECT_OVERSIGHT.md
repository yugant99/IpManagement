# Persistent project oversight

**Leadership transfer authorized on 2026-09-19: Main Lead 2.0 replaces the outgoing lead.** Follow [the exact-state transfer](handoffs/main-lead-2.0.md). Receiver task ID is pending registration; the receiving task registers its actual ID before assuming coordination/global acceptance. Outgoing task `01a0b845-6c8d-7021-a5c9-15e673db07c9`, titled "Main Lead", becomes reference-only after publishing the transfer. Its heartbeat is paused pending reattachment. Titles alone never reassign ownership: "Overseer" (`01a0b8b9-82fb-7a11-bc50-ec3a5b234729`) remains the synthetic-data worker. Use STATUS.md for routing. Ordinary stage tasks remain workers and do not replace the lead.

## Ownership

| Owner | Responsibility |
|---|---|
| Persistent project-lead chat | Questionnaire evidence across all 111 rows; shared contracts; assignment and worktree coordination; independent review; merge coordination; stage acceptance; global status; final readiness and next-stage prompt |
| Stage implementation chat | Its assigned behavior, feature branches, local handoff/report, precise implementation/evidence claims and blockers. May coordinate bounded subagents inside its scope |
| Spencer / Part 6 | Package, persistent storage integration, operator instructions and recipient handoff. Core owns application/state-command correctness; no presentation assignment |
| User | Business priorities and decisions genuinely outside delegated scope, including additional spending/deployment permission or provider commitments |

The lead owns `docs/STATUS.md` and `docs/CURRENT_HANDOFF.md`. Workers submit changes or proposed updates through their branch/handoff; they do not race to replace global state. Only the lead accepts a stage or declares the project ready. A worker's final answer is a completion claim to review, not independent acceptance.

## How completion is decided

The worker finishes a bounded slice, commits/pushes, opens its focused PR and writes a stage report. The lead reads the actual diff/handoff and available evidence, reconciles dependencies and obtains a bounded independent review where needed. It records one of:

- **Accepted checkpoint:** identified code/documents are integrated or their exact dependency state is agreed; remaining runtime evidence is explicitly listed.
- **Needs changes:** concrete defects, missing contracts or incomplete behavior; assign them to the owning worker.
- **Evidence pending:** code may be ready, but the claimed behavior has not been established. Do not convert this into "works" or a completed requirement.
- **Ready for recipient/demo:** the candidate, essential source-to-finding path, calculations, allocation controls and portable persistence have the required actual evidence; limitations are disclosed.

Use the 111-row evidence map and remaining gaps rather than commit count, task completion messages or a 65/67 planning number. A completed chat, merged PR and green-looking dashboard are different facts. Existing test/runtime/infrastructure permissions remain in force; oversight does not authorize additional checks or deployment by itself.

## Worker report required at each checkpoint

Record this in the worker's stage/lane handoff, and include the summary in its final response:

```text
Stage / owner / task ID or exact task title:
Checkout/worktree and owned paths:
Questionnaire IDs changed:
Branch / exact pushed SHA / PR:
Integration base / unmerged dependencies:
Implemented:
Actually observed and evidence pointers:
Synthetic / simulated / partial / unverified:
Checks actually run and authorization:
Blocker / requested lead decision:
Suggested next-stage prompt:
```

Workers record their task identity when available; do not guess an ID. The lead can discover tasks by the recorded identity, project and branch. If a worker runs outside this app (for example Spencer's agent), its pushed branch, PR and repository handoff are the reporting channel; no access to a private external chat is assumed. Do not send Slack/email messages to collaborators without an explicit instruction.

The user should not have to relay an entire conversation. App-visible worker tasks can be read by the lead; published Git handoffs preserve the evidence independently of chat history. If neither a task nor pushed artifact is available, report that exact visibility gap.

## Monitoring versus authority

The persistent lead reviews progress when active. A separately configured thread heartbeat can inspect progress between user messages; ownership alone does not make the agent continuously run. The configured cadence and expiration are reported by the app automation, not inferred from this document.

The heartbeat is deliberately read-only: read registered/clearly relevant stage task summaries, repository handoffs and PR/branch status. Stay quiet if nothing actionable changed. Notify on a new checkpoint ready for review, a meaningful failure/blocker, an unsupported completion claim, or a decision that genuinely requires the user. No application tests, builds, fixes, branch changes, merges, task creation, deployment or external messages are implied by monitoring. The active lead handles the next review/integration action within existing authority.

A schedule is periodic, not real-time. Task visibility and the app scheduler must be available. If a run fails to inspect a source, report an access/monitoring limitation rather than treating missing data as completion. Stop reporting after final acceptance; do not keep a completed project noisy.

## Worktree and handoff rules

Every concurrent implementation worker uses its own feature branch and isolated worktree/checkout. The lead reads PRs/remote refs or its own checkout; it must not switch/reset the branch beneath a worker. The lead remains the same when Stage 1 hands off to Stage 2 and through Stage 5. A persistent-lead replacement requires an explicit user decision and its own exact-state handoff, not an automatic stage transition.

At a worker checkpoint, display **READY FOR PROJECT-LEAD REVIEW — Stage N** with the pushed SHA/PR and report. Draft the next prompt. After lead review, this chat updates the global pointers and displays **START A NEW IMPLEMENTATION CHAT — Stage N+1** with the accepted baseline and generated prompt. Independent next-stage preparation can proceed on a named dependency without pretending acceptance or runtime gates have passed.

Prior worker chats remain available for assigned feature fixes; fixes to merged work use a fresh fix branch. The project-lead chat remains the place to ask "what is done, what is missing, and are we ready?"
