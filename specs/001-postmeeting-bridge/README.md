# Post-meeting specification package

**State: Spec v0 checkpoint. Not locked. 0 of 100 questions answered.**
Owner: dedicated specification architect. Persistent lead and final acceptance authority:
Main Lead 3.0, task `01a0c0c1-3952-7720-93c8-ff49192b8e13`.

## Read order
1. [Source reconciliation](source-reconciliation.md) and [coverage matrix](coverage.csv).
2. [Spec v0](spec.md).
3. [Ambiguities](ambiguities.md).
4. [Interview control](interview.md), [Round 1](round-01.md), [question register](questions.csv).
5. [Quality checklist](checklists/requirements.md) and [toolkit provenance](toolkit-record.md).

The real Spec Kit v1.0.9 constitution/specify process created this draft. Toolkit-generated
skills/scripts/templates are project-local; runtime/cache is ignored. Constitution lives at
[.specify/memory/constitution.md](../../.specify/memory/constitution.md).

## Output state

| Deliverable | State |
|---|---|
| Constitution and sanitized Spec v0 | Draft complete; lead adoption and user decisions pending |
| Evidence/source reconciliation and requirement taxonomy | Inspected; distinct ledgers preserved |
| Ambiguity/decision register | Open, explicit conflicts and source interpretation limits |
| Q001–Q100 register | 100 meaningful candidate prompts; Q001–Q008 awaiting answers, Q009–Q100 unasked |
| Locked specification | Not created; requires 100 actual answers and resolved conflicts |
| Technical plan | Not run; gated after lock |
| Dependency-aware task graph | Not run; gated after lock |
| Agent routing/spawn annex | Agreed role constraints retained below; task-level annex after lock |
| Three-day roadmap | Requested lanes retained below; critical path/hours/drop order after decisions |
| Coverage matrix | All 111 rows mapped to candidate capability/evidence gates; tasks pending decomposition |
| Final project-lead review report | Not issued; package is not yet ready for final review |

## Fixed routing inputs for the post-lock annex

This records the user's routing, not dispatched work or model availability verification.

| Role | Assigned model/person | Boundary |
|---|---|---|
| Canonical decisions and acceptance | Astra / existing Main Lead 3.0 | Existing lead only |
| Requirements/integration sublead | Grok 4.7 | Adversarial API/schema/failure-mode review |
| Research/ambiguity/documentation scout | Grok 4.6 under Grok 4.7 | Bounded research and edge cases |
| Implementation sublead | Terra in OpenCode | Settled contracts and owned files |
| Leaf implementation | DeepSeek under implementation sublead | Bounded leaves only |
| Difficult/cross-cutting escalation | Sol | Escalation, not parallel duplicate ownership |
| Independent verification/evidence | Luna | Not default implementation fixer |
| Advisory review | Fable | After spec lock, before acceptance; no acceptance authority |
| Portability/operator handoff | Spencer | No shared-schema/core integration ownership |

At most three subleads, two workers per sublead and two levels below the lead. Final annex
must assign actual tasks/files, spawn conditions, prerequisites, observable completion,
required evidence, non-claims, escalation and exact handoff. No paid model invocation
or external dispatch is authorized by this task. A single bounded local source-recovery
subagent was used as directed by the grilling skill to inspect unavailable attachments;
it is not an implementation lane or a change to future routing.

## Spencer's fixed lane inputs

- Day 1: endpoint/integration documentation matrix, mock-versus-live boundaries.
- Day 2: migration/recipient validation pack, reconciliation, rollback/sign-off, sanitized configuration.
- Day 3: fresh-start/demo rehearsal, backup/restore, dependency/license notes, evidence capture, presenter/recipient handoff.

Actual execution and checks require their future authorization; no execution implied here.
The post-lock schedule must specify parallel dependencies, decision gates, risk reserve
and what drops first. Earlier 6–8 hours are historical until the user confirms availability.

## Owned paths and checkpoint
Assigned worktree only. Owned changes: `.specify/`, generated `.agents/skills/` and
`specs/001-postmeeting-bridge/`. No application, dependency lock, deployment,
global status or shared-contract changes. Baseline:
`04eba98cb8673406d1e5d38c5318fb963cc77ff7`.
Branch: `codex/postmeeting-specification`. Exact checkpoint SHA is reported in the task.
No implementation PR and no merge.

Document inspection: counted source labels and all 111 IDs; checked candidate FR coverage,
required card fields, 100 unique question IDs, blank answers, dependency ordering, draft
gates and committed-path privacy. No application tests, smoke tests, builds or runtime reads.
This is author document review, not independent final specification acceptance.

## Resume instruction
Read this package and the latest actual user response. Record only genuine answers in
questions.csv, including rationale/source/conflicts; update affected draft requirements.
Recompute the frontier and ask the whole next unblocked round. Preserve Q001–Q100.
Do not plan, decompose tasks or lock until every answer and conflict is reconciled and Q100
confirms shared understanding. Then run the real generated Spec Kit plan/tasks/analyze
workflows, add the required task-level routing/roadmap and submit to Main Lead 3.0.


Fresh-checkout note: Spec Kit deliberately ignores its local `.specify/feature.json`
pointer. Select `specs/001-postmeeting-bridge` as the feature directory in a receiving
checkout before invoking plan/tasks; do not create a second feature or infer a numbered
branch name. This worktree's local pointer is already set.
