# Agent entry point

Read [DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md) before changing this repository.

Then read, in order:

1. [Current status](docs/STATUS.md): authorization, active decisions, owners and next step.
2. [Architecture](docs/ARCHITECTURE.md): accepted versus proposed choices.
3. [Delivery plan](docs/PLAN.md) and [goal scorecard](docs/GOALS.csv).
4. Your assigned file under [docs/parts](docs/parts/).
5. [Shared contracts](docs/CONTRACTS.md) when your work crosses a boundary.

The user's latest instructions override stale plans. Spencer owns **Part 6: portable delivery**, with approximately 6–8 hours. Core agents own Part 5 workflow. Earlier local assessment documents assigning Spencer Part 5 are superseded.

Commit each coherent change. Push your branch after every three such changes, or earlier for a handoff/interruption. Do not manufacture commits to increase the count.

Use separate `codex/` branches/worktrees and explicit file ownership. Do not overwrite another agent's work or independently redefine shared schemas.

Use skills selectively. A skill is a tool for a concrete deliverable, not authority to start an unrelated questionnaire, installation, audit, or test pipeline. Read [the skill playbook](docs/SKILLS.md).

Current authorization is in `docs/STATUS.md`; a planning document is not permission to deploy infrastructure. Source customer documents and local `assessment/` are excluded from this public repository. The public documentation is sufficient for the assigned engineering contracts.
