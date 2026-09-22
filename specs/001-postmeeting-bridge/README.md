# Post-meeting specification package

**State: 100/100 actual agent decisions resolved; agent-locked candidate for Main Lead 3.0 review.**
No application implementation, tests, smoke runs, builds, infrastructure changes or paid model calls.

## Start here
1. [Locked specification](spec.md): minimum bridge, 22 capability cards and explicit deferred scope.
2. [Actual decisions](questions.csv) and [agent grilling](agent-grilling.md): proposals,
   challenges, initial lock refusals, corrections and final confirmation.
3. [Plan](plan.md), [data model](data-model.md) and [contracts](contracts/access.md).
4. [40-task graph](tasks.md), [machine-readable assignments](task-graph.csv),
   [agent routing](agent-routing.md) and [three-day roadmap](three-day-roadmap.md).
5. [All 111 row dispositions](coverage.csv), [source reconciliation](source-reconciliation.md),
   [analysis](analysis.md) and [lead handoff](final-handoff.md).

## Architecture selected by the agents
Trusted internal-domain access on every egress; immutable JSON migration assessment without
cutover; local static IPv4 reservation/allocation and unused-reservation release; one durable
simulated ticket handoff; same-candidate operator, evidence and stopped-recovery package.
Global feed acquisition/run/reconciliation stays with a fixed evidence coordinator explicitly
authorized for every configured synthetic source/scope. Ordinary domain users cannot trigger
or delegate those jobs. Their refresh reads scoped saved projections and their imports are
intended candidates only, without callbacks.

Allocated release/reassignment, synthetic DHCP and extra prefix proposal UI are gated Tier B.
Live vendors, DNS writes, enterprise identity, customer tenancy, HA/scale, licensing
enforcement and configurable workflow/IaC remain documentary or deferred. The three-day
schedule is conditional on real capacity, with 20% reserve and Spencer 2h/day plus up to 2h
contingency if available. A missing Tier A gate means bridge incomplete, not a smaller pass.

## Evidence and authority
Accepted repository baseline remains 39 Demonstrated / 18 Partial / 10 Documentary / 44 Missing.
The meeting workbook's 92 Demonstrated labels remain a separate target ledger, not new proof.
All 111 rows have FR/task/evidence dispositions. Task coverage is not capability satisfaction.

Spec Kit v1.0.9 constitution/specify/plan/tasks/analyze workflows were applied using the real
local toolkit. [Toolkit record](toolkit-record.md) records commands and source commit.
Spec v0 is preserved in [spec-v0.md](spec-v0.md); [round-01.md](round-01.md) is historical
and explicitly superseded. No routine architecture question remains assigned to the user.

Persistent lead: Main Lead 3.0, task 01a0c0c1-3952-7720-93c8-ff49192b8e13.
Only that lead adopts shared contracts, coordinates acceptance/merge and changes global status.
Fable advice, future execution/validation authority, actual model availability, target access
and human/business evidence remain explicit gates. Agent agreement is not runtime acceptance.

Owned paths: .specify/, generated .agents/skills/, specs/001-postmeeting-bridge/.
Branch: codex/postmeeting-specification; original base
04eba98cb8673406d1e5d38c5318fb963cc77ff7. No global-status/application files changed.
Fresh checkout: select the existing feature before invoking toolkit scripts; do not create a
second feature. From the repository root, run:

```sh
export SPECIFY_FEATURE=001-postmeeting-bridge
export SPECIFY_FEATURE_DIRECTORY="$PWD/specs/001-postmeeting-bridge"
bash .specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
```

The first toolkit script call recreates the local ignored `.specify/feature.json` pointer.
