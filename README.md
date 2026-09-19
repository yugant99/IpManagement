# IpManagement

An IP address inventory and reconciliation demonstration using synthetic data, with real local calculations and persistence.

**Current state:** Historical Stage 5 bounded local acceptance remains **14 observed passes, two partial scenarios, no observed application defects**. PR #44 is merged at `7eb3e8516ee63a5e803bad23dd7e44c161bc67fc`; PR #47 native procedural evidence is merged at `e4b57ac1edfac98379d173fda9fb23ca22b1676f`. Final bounded accounting is **32 Demonstrated / 22 Partial / 10 Documentary / 47 Missing** across 111 rows. Human presenter/recipient practice, portable packaging and customer-phase acceptance remain separate limits. Read [current status](docs/STATUS.md), [readiness and integration](docs/handoffs/accepted-candidate-integration.md), and [accepted evidence limits](docs/handoffs/stage-05-lead-review.md).

## Agent pickup

**Current work: [stage and generated pickup prompt](docs/CURRENT_HANDOFF.md).** Main Lead 2.0 is the registered [persistent project lead](docs/PROJECT_OVERSIGHT.md). The [chat-stage guide](docs/CHAT_STAGES.md) has workers report checkpoints and the lead publish each next-stage prompt; prior worker chats remain available for branch follow-ups.

Read [AGENTS.md](AGENTS.md), [development rules](DEVELOPMENT_RULES.md), and [the pickup guide](docs/START_HERE.md). The lead owns integration; contributors own bounded parts on separate branches.

| Part | Outcome | Task |
|---|---|---|
| 1 | Scoped inventory and API | [Inventory](docs/parts/01-inventory.md) |
| 2 | Synthetic sources and assessment | [Sources](docs/parts/02-sources.md) |
| 3 | Reconciliation with evidence | [Rules](docs/parts/03-reconciliation.md) |
| 4 | Capacity dashboard | [Dashboard](docs/parts/04-dashboard.md) |
| 5 | Approval and local allocation | [Workflow](docs/parts/05-workflow.md) |
| 6 | Runnable portable handoff | [Spencer's part](docs/parts/06-portability.md) |

Spencer's agent first reads the [current candidate addendum](docs/handoffs/accepted-candidate-integration.md#spencers-current-candidate-and-remaining-evidence), then [the Part 6 handoff](docs/handoffs/part-6.md). No prior chat or private customer attachment is required to understand that engineering package.

## Planning references

- **Current scope:** [questionnaire priorities](docs/QUESTIONNAIRE_PRIORITIES.md), [all 111 rows and gaps](docs/QUESTIONNAIRE_ROW_MAP.md), and [scope changes](docs/QUESTIONNAIRE_SCOPE_DELTA.md). Final bounded current-candidate accounting: **32 Demonstrated / 22 Partial / 10 Documentary / 47 Missing = 111**. Historical 65/67/68 planning bundles and the 51 candidate evidence IDs are not fully satisfied-row counts. Retain the separate [customer phase gaps](docs/PHASE_COVERAGE.md).
- [Architecture decisions](docs/ARCHITECTURE.md) and [shared contracts](docs/CONTRACTS.md).
- [75-question agent review](docs/GRILL_75.md) and [adopted implementation details](docs/IMPLEMENTATION_DECISIONS.md).
- [Original twenty-hour coverage baseline](docs/COVERAGE.md), [original goal manifest](docs/GOALS.csv), and [original requirement links](docs/REQUIREMENT_COVERAGE.csv). These preserve the 53-row baseline; the current row map takes precedence for priority.
- [Work sequence](docs/PLAN.md) and [bounded skill playbook](docs/SKILLS.md).

The demo scorecard and full external questionnaire have different denominators. Neither a planning target nor a simulated integration is proof of delivered requirement coverage.

## Runtime

The accepted candidate supplies one Python API serving a compiled React UI, local SQLite state, deterministic synthetic acquisition, calculations, allocation/audit and scheduling. See [runtime contracts](docs/CONTRACTS.md), [schedule API](docs/STAGE4_API.md), [state operations](docs/STATE_OPERATIONS.md) and the accepted [core schema/reset supplement](docs/handoffs/part-1-state-schema5.md). The [Stage 5 report](docs/handoffs/stage-05-report.md) records macOS arm64 observations; it does not establish Docker/Compose/Linux or recipient operation. External provisioning is simulated. Historical Stage 5 observed v3-to-v4 migration; later core checks at `d6197df` observed genuine populated v4-to-v5 migration and scoped confirmed-reset, missing-confirmation, held-lock and missing-v5-column controls with old rows preserved. V1/v2 and direct v3-to-v5 migration, enabled-snapshot restore and deeper filesystem/crash branches remain unrun. `PART6_READY=no`; no package checkpoint or recipient-host evidence is registered.

Private source documents, detailed assessment extracts, credentials and runtime data stay outside Git. Public documentation contains generic engineering scope and synthetic examples.
