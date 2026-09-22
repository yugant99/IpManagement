# Implementation Plan: Post-meeting IPAM / Pool Watch bridge

**Branch**: `codex/postmeeting-specification` | **Date**: 2026-09-22 | **Spec**: [spec.md](spec.md)

**Input**: Agent-locked specification, Q001–Q100, constitution 1.1.0.
**State**: Design only, ready for lead review. No application implementation/execution authorized.

## Summary
Extend the existing single-process application with server-derived scoped identity,
immutable inventory assessment, narrow local reservations and one durable ticket simulator.
Preserve evidence semantics, local allocation transactions and stopped-service recovery.
A single implementation owner integrates shared schema and routes. No new service, queue,
database, UI framework or vendor connector is required.

Minimum success is the complete Tier A path in Q099, independently observed on an exact
future candidate. Assessment does not promote inventory. Local approval is independent of
ticket delivery. An uncertain ticket outcome remains uncertain until correlation readback.

## Technical Context
**Language/Version**: Application Python >=3.12,<3.13; TypeScript 7.0.2, React 19.3.
**Primary Dependencies**: Existing FastAPI 0.141.1, Uvicorn 0.50.1, Vite 8.3 locks; no upgrades.
Node >=22.12,<23 or >=24,<25, npm 10.9.2, as inspected in repository manifests.
**Storage**: Existing SQLite, schema 5 at base; one explicitly migrated schema 6 for Tier A,
single process and immediate write transactions. Single core schema owner reserves the
number against main before implementation; rebase/reassign if main advanced.
**Validation**: Existing repository tools plus exact scenario protocol in quickstart.md only
after explicit implementation/validation authorization. No test files or runs created now.
**Target Platform**: Existing bounded Linux amd64 operator target, loopback HTTP access.
Native application requires Python 3.12; Python 3.11+ in host wrappers is a different tool role.
Remote/public exposure, new infrastructure and TLS qualification are separate gates.
**Project Type**: Existing FastAPI/SQLite service and React web application.
**Performance Goals**: Preserve bounded 10 MiB/10,000-row imports; manual simulator attempt
observation <=5 seconds. Future scale goals in qualification.md are not current obligations.
**Constraints**: Existing read-only source envelopes/runs, no self-approval, domain checks
on all egress, visible partial failures, no external side effects, no raw private artifacts.
**Scale/Scope**: One local static IPv4 authority pool, explicit internal domains, one ticket
simulator, four user stories. All 111 RFP rows receive dispositions, not new capability claims.

## Constitution Check
Pre-research PASS for a planning candidate: source ledgers separated; scope/failure gates
resolved in 100 actual agent decisions; no vendor facts invented; no execution permission
inferred. Existing source scouting resolves architecture seams (source-seams.md).

Post-design PASS for planning: data-model.md and contracts preserve staged input, immutable
runs, transactions, distinct external states, fixed policies, scoped identity and independent
approval. Shared schema/routes remain one-owner. No implementation/runtime acceptance claimed.
External gates: lead adoption, implementation and validation authorization, available
future model routes, Fable advice or explicit lead waiver, recipient access/human sign-off.
These gates do not block documenting the selected local architecture.

## Project Structure
```text
specs/001-postmeeting-bridge/
  spec.md, questions.csv, agent-grilling.md, coverage.csv
  plan.md, research.md, data-model.md, qualification.md
  contracts/access.md, migration.md, lifecycle.md, ticketing.md, operator.md
  quickstart.md, tasks.md, task-graph.csv, agent-routing.md
  three-day-roadmap.md, analysis.md, final-handoff.md
backend/ipam_demo/
  app.py, store.py, schema.sql, schema_v6.sql [future], state_ops.py
  access.py [future], migration_compare.py [future]
  lifecycle.py [future], ticket_handoff.py [future]
  workflow.py, imports.py, inventory.py, reports.py, scheduler.py
frontend/src/
  api.ts, existing *Api.ts clients, App.tsx
  MigrationCompare.tsx [future], FirstPath.tsx, Workflow.tsx
  CapacityReports.tsx, InventoryEditor.tsx, Corrections.tsx, Schedule.tsx
scripts/ops/
  existing operator wrappers; future auth-aware acquire/readiness adjustments
```
New module boundaries are narrow domain responsibilities, not generic frameworks.
Terra owns app.py, schema/store/state operations and shared security integration.
DeepSeek backend owns migration_compare/lifecycle/ticket_handoff leaves and assigned
workflow changes after schema/access contracts; DeepSeek UI owns client/components.
Only one writer per file at a time; Terra integrates workers via isolated worktrees/PRs.

## Delivery phases
0. Lead adopts contracts/ownership and records actual availability/authorization; Fable
advice can occur any time after lock, before acceptance.
1. Trusted identity/all-egress controls and schema foundation. Fail closed on unmapped
legacy data; preserve raw artifacts. Auth-free shell/minimal liveness only.
2. US1 comparison and US2 local reservation/allocation plus correlated simulated handoff.
Backend and UI can proceed against frozen examples on different files.
3. US3 aging/alarms and current static occupancy, preserving saved-run arithmetic.
4. US4 operator/API/evidence pack and stopped recovery compatibility; independent review
and authorized observations at the integrated candidate. Human acceptance remains distinct.
5. Only after Tier A integration and protected reserve may lead schedule explicit Tier B.
No Tier B is on the three-day critical path.

## Integration and migration boundaries
The schema owner adds only the Tier A tables/columns described in data-model.md, updates
fresh seed initialization, explicit migration recognition and backup/restore validation.
No seed overwrites existing stores. Preserve old request/allocation IDs and immutable runs.
Legacy global presets are quarantined from domain users until explicitly classified; no
automatic copied exposure. Legacy tokens/actor strings are never valid authentication.
Access route integration covers operational wrappers as well as browser clients. Global
feed/clock/run/reconciliation stays service-only under a fixed explicitly scoped coordinator;
ordinary domain users cannot trigger it or request callbacks. Their imports are intended
candidates only and their refresh reads saved projections. No per-domain feed rewrite.
Store restore does not restore token/config/code/UI authority: operator manifest pins them.

## Complexity Tracking
No constitution violation proposed. A narrow durable ticket intent/result/attempt journal
is necessary to distinguish crash/unknown outcomes; it is not a background queue.
A narrow reservation ledger is necessary because pending requests intentionally do not hold.
Allocated release/reuse is excluded from Tier A to avoid changing every historical reader
and the existing unconditional allocation uniqueness/foreign-key contract prematurely.
