# Agent entry point

Read [DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md) before changing this repository.

Then read, in order:

1. [Current handoff](docs/CURRENT_HANDOFF.md), [chat stages](docs/CHAT_STAGES.md) and [current status](docs/STATUS.md): stage, scope, owners and next step. Status records authorization; it does not override the latest user instruction.
2. [Questionnaire priorities](docs/QUESTIONNAIRE_PRIORITIES.md) and your IDs in [the 111-row map](docs/QUESTIONNAIRE_ROW_MAP.md): current scope and remaining gaps.
3. [Architecture](docs/ARCHITECTURE.md) and [delivery plan](docs/PLAN.md). The older [goal manifest](docs/GOALS.csv) is a work reference, not the primary coverage denominator.
4. Your assigned file under [docs/parts](docs/parts/).
5. [Shared contracts](docs/CONTRACTS.md) when your work crosses a boundary.

The user's latest instructions override stale plans. Spencer owns **Part 6: portable delivery**, with approximately 6–8 hours. Core agents own Part 5 workflow. Earlier local assessment documents assigning Spencer Part 5 are superseded.

Commit each coherent change. Push your branch after every three such changes, or earlier for a handoff/interruption. Do not manufacture commits to increase the count.

Use a separate `codex/` branch for each feature, isolated worktrees for concurrent agents, and explicit file ownership. Ready features go through a bounded PR review and lead-coordinated merge into `main`. Do not overwrite another agent's work or independently redefine shared schemas.

Use skills selectively. A skill is a tool for a concrete deliverable, not authority to start an unrelated questionnaire, installation, audit, or test pipeline. Read [the skill playbook](docs/SKILLS.md).

At a stage checkpoint, proactively generate the next-stage handoff and display **START A NEW CHAT — Stage N: title** with its paste-ready prompt. Follow `docs/CHAT_STAGES.md`; do not wait for the user to request the handoff. Preserve the old chat for assigned fixes and do not start the next lead stage here unless the user asks to continue here.

The current scope/permission record is in `docs/STATUS.md`; the latest user instruction governs, and a planning document is not permission to deploy infrastructure. Source customer documents and local `assessment/` are excluded from this public repository. The public documentation is sufficient for the assigned engineering contracts.
