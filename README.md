# IpManagement

A planned portable IP address inventory and reconciliation demonstration using synthetic data.

**Current state:** documentation and agent coordination only. The application, container and runtime commands are not implemented yet. Start with [current status](docs/STATUS.md).

## Agent pickup

**Next: [current stage and generated pickup prompt](docs/CURRENT_HANDOFF.md).** The [chat-stage guide](docs/CHAT_STAGES.md) makes each lead generate a fresh-chat prompt at the next milestone and keeps prior chats available for branch follow-ups.

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

- **Current scope:** [questionnaire priorities](docs/QUESTIONNAIRE_PRIORITIES.md), [all 111 rows and gaps](docs/QUESTIONNAIRE_ROW_MAP.md), and [scope changes](docs/QUESTIONNAIRE_SCOPE_DELTA.md). Target 65 addressed rows, two conditional additions to reach 67; these totals include partial and document evidence.
- [Architecture decisions](docs/ARCHITECTURE.md) and [shared contracts](docs/CONTRACTS.md).
- [75-question agent review](docs/GRILL_75.md) and [adopted implementation details](docs/IMPLEMENTATION_DECISIONS.md).
- [Original twenty-hour coverage baseline](docs/COVERAGE.md), [original goal manifest](docs/GOALS.csv), and [original requirement links](docs/REQUIREMENT_COVERAGE.csv). These preserve the 53-row baseline; the current row map takes precedence for priority.
- [Work sequence](docs/PLAN.md) and [bounded skill playbook](docs/SKILLS.md).

The demo scorecard and full external questionnaire have different denominators. Neither a planning target nor a simulated integration is proof of delivered requirement coverage.

## Runtime

There is no working startup command yet. The intended delivery is a Python API serving a compiled React UI, SQLite stored outside the application image, deterministic synthetic inputs and documented reset/backup/restore. Do not treat planned commands in the contract as implemented software.

Private source documents, detailed assessment extracts, credentials and runtime data stay outside Git. Public documentation contains generic engineering scope and synthetic examples.
