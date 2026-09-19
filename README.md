# IpManagement

A planned portable IP address inventory and reconciliation demonstration using synthetic data.

**Current state:** documentation and agent coordination only. The application, container and runtime commands are not implemented yet. Start with [current status](docs/STATUS.md).

## Agent pickup

Read [AGENTS.md](AGENTS.md), [development rules](DEVELOPMENT_RULES.md), and [the pickup guide](docs/START_HERE.md). The lead owns integration; contributors own bounded parts on separate branches.

| Part | Outcome | Task |
|---|---|---|
| 1 | Scoped inventory and API | [Inventory](docs/parts/01-inventory.md) |
| 2 | Synthetic sources and assessment | [Sources](docs/parts/02-sources.md) |
| 3 | Reconciliation with evidence | [Rules](docs/parts/03-reconciliation.md) |
| 4 | Capacity dashboard | [Dashboard](docs/parts/04-dashboard.md) |
| 5 | Approval and local allocation | [Workflow](docs/parts/05-workflow.md) |
| 6 | Runnable portable handoff | [Spencer's part](docs/parts/06-portability.md) |

Spencer's agent starts at [the Part 6 handoff](docs/handoffs/part-6.md). No prior chat or private customer attachment is required to understand that engineering package.

## Planning references

- [Architecture decisions](docs/ARCHITECTURE.md) and [shared contracts](docs/CONTRACTS.md).
- [Twenty-hour plan and coverage](docs/COVERAGE.md), [demo goals](docs/GOALS.csv), and [full requirement tracking](docs/REQUIREMENT_COVERAGE.csv).
- [Work sequence](docs/PLAN.md) and [bounded skill playbook](docs/SKILLS.md).

The demo scorecard and full external questionnaire have different denominators. Neither a planning target nor a simulated integration is proof of delivered requirement coverage.

## Runtime

There is no working startup command yet. The intended delivery is a Python API serving a compiled React UI, SQLite stored outside the application image, deterministic synthetic inputs and documented reset/backup/restore. Do not treat planned commands in the contract as implemented software.

Private source documents, detailed assessment extracts, credentials and runtime data stay outside Git. Public documentation contains generic engineering scope and synthetic examples.
