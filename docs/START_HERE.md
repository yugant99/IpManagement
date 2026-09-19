# Resume or join this project

Canonical repository: https://github.com/yugant99/IpManagement

## Read only what your lane needs

1. `AGENTS.md` and `DEVELOPMENT_RULES.md`.
2. `docs/STATUS.md`: current authorization, integration baseline and readiness.
3. `docs/ARCHITECTURE.md`, then the relevant portion of `docs/CONTRACTS.md`.
4. Your `docs/parts/NN-*.md` and linked goal IDs in `docs/GOALS.csv`.
5. Your handoff, if present. Spencer uses `docs/handoffs/part-6.md`.

Do not reread the entire local assessment or invoke a planning pipeline on every turn. Ask the lead for a missing contract; do not require the user to reconstruct the conversation.

## Before editing

- Identify the current branch, HEAD and unrelated local edits. Preserve them.
- Read status before deciding whether this is a documentation or implementation turn.
- Create/use the assigned `codex/` branch or isolated worktree from the recorded integration baseline.
- State owned files and first visible deliverable to the lead.
- The root agent coordinates shared contracts and app wiring. Two agents must not edit the same migration, navigation file or dependency lock independently.

## Work and checkpoint

Make one coherent change per commit. Push after three commits, and earlier when handing off or stopping. Include exact pushed branch/commit in the handoff; obtain it from Git, not memory.

Use skills for concrete outputs within the feature budget. Architecture grilling is agent-to-agent, not a user interview. Do not block implementation on tool onboarding or an unrelated checklist.

## Lane handoff format

Record in your handoff file:

```text
Owner / part:
Branch and commit:
Integration base SHA / contract revision:
Pushed: yes / no, with reason
Goal IDs:
Works now:
Simulated:
Unverified:
Changed files / interfaces:
Merged / unmerged dependencies and missing entrypoints:
Checks actually performed:
Blocker:
Next exact action:
```

Use relative paths and reproducible commands. Do not embed local credentials or require access to a specific developer's home directory.

## Scope facts

Data is synthetic. The app is portable and can run without paid cloud services. The planning budget is approximately 20 lead working hours with Spencer's 6–8 hours overlapping. Spencer owns Part 6 only, with no presentation assignment. Separate demonstration goals from full external requirement satisfaction.
