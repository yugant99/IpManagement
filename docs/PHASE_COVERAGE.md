# Phased requirements: evidence and remaining gaps

Lead acceptance addendum, 2026-09-19. Both the phased requirements document and the questionnaire inform this project. **Neither customer Phase 1 nor customer Phase 2 is accepted as complete.** Engineering Stages 1–5 are our build checkpoints; they are not the customer's phases. The F1–F7 final rehearsal supplies focused procedural evidence, not a new customer-phase assessment.

The questionnaire denominator remains **111**. The accepted local ledger associates observations with **51 candidate rows**, not 51 fully satisfied requirements. [Final current-candidate questionnaire adjudication](QUESTIONNAIRE_ROW_MAP.md) records **32 Demonstrated / 22 Partial / 10 Documentary / 47 Missing = 111**; these classes do not establish whole customer/production compliance. The phase sections below are a separate view of the same evidence: do not add them to 111, count them as extra rows, or turn section mentions into a completion percentage.

This is a generic, project-owned coverage summary, not a customer assessment report. Section numbers refer to the private phased requirements document. Source attachments, extracts, network names and estate counts remain outside the public repository. The lead compared the source sections with the existing evidence; focused rehearsal evidence does not establish independent presenter/recipient acceptance, portable delivery or customer adoption.

## Evidence baseline

Use the [Stage 5 lead review](handoffs/stage-05-lead-review.md) and pinned [scenario ledger](https://github.com/yugant99/IpManagement/blob/278868ad17e79d7f17699a38f3b069ed4d89597f/docs/evidence/stage-05/README.md). Application pickup is `117d05295473cf25d362adb320e6fef26ecdd74c`; evidence publication is `fe50cd6828016a25fee9086f499e2e865b4a16e4`, PR #27. The accepted result is 14 observed passes and two partial scenarios on local macOS with synthetic data. Scenario references below inherit every limit in that historical review, including S5-09/S5-15, representative v3-to-v4 migration only, fixed demo actors and simulated external actions; current state/reset evidence also includes the accepted [core schema/reset supplement](handoffs/part-1-state-schema5.md) for populated v4-to-v5 migration and scoped reset/control checks.

The sources require Phase 1 assessment of a selected customer scope, followed by initial Phase 2 implementation in that assessed scope and later onboarding waves. The approved customer subset has not been established here. Fictional demo scopes do not establish all-domain or customer-domain coverage.

## Customer Phase 1: current-state assessment

Phase 1 is assessment-focused; building a new dashboard does not itself complete it. The required result is a validated current-state assessment using customer sources and operational knowledge.

| Source section | Evidence available in the demo | Remaining customer outcome |
|---|---|---|
| 4.1 Source identification | Nine known synthetic source identities, canonical receipts and provenance (S5-03/15); selected refusal checks are partial | Complete in-scope repository catalog, accountable source owners, maintenance/update practices and validated authority ranking. Catalog UI was not independently observed |
| 4.2 Inventory and discovery | Scoped intended inventory, observed leases/routes, utilization and IPv4/IPv6 prefix operations (S5-05/06/11) | Real-source discovery and validation; complete customer address inventory, ownership and domain-level utilization |
| 4.3 Data quality | Selected overlap/conflict, missing-route, stale/unknown and scope controls; independent calculation comparisons (S5-05/06/07/11/15) | Customer completeness/accuracy/metadata assessment, quantified quality scorecard, severity and risk assessment across the selected estate |
| 4.4 Workflow assessment | One fixed request/approval/allocation/audit flow and exception handoff illustrate possible future behavior (S5-12/13) | Document and validate existing customer request, reservation, provisioning, update, reclamation, audit and DNS/DHCP processes, teams, controls and manual steps |
| 4.5 Integration assessment | Typed synthetic import/acquisition flow and engineering contracts (S5-03/07; [contracts](CONTRACTS.md)) | Actual system/interface inventory, end-to-end dependency and data-flow maps, integration risks and live interface access |
| 4.6 Discovery validation assessment | Eligibility, freshness, completeness and reconciliation behavior on known fixtures (S5-05/07/15) | Assess available customer discovery mechanisms, network validation, audit capabilities and interfaces |
| 4.7 Operational maturity | Local role checks, audit records and team handoff illustrate selected controls (S5-12/13) | Evidence-based assessment of existing governance, ownership, standards, tooling, automation, integration and operational discipline |
| 5 Deliverables and success criteria | Saved runs, selected findings and CSV exports can illustrate inventory/utilization/conflict portions (S5-05/06/07) | A validated customer Current State Assessment Report covering inventory, sources, workflows, integrations, quality, maturity, risks and recommendations; stakeholder acceptance and source completeness |

**Phase 1 status: selected assessment mechanisms demonstrated on synthetic inputs; the customer assessment and its completion criteria remain outstanding.** Demo exports are not the required validated customer report.

## Customer Phase 2: modernization and transformation

| Source section | Evidence available in the demo | Remaining customer outcome |
|---|---|---|
| 7.1 Lifecycle | Persisted request, independent approval, local allocation, audit and fixed-team exception handoff (S5-12/13) | Full lifecycle including real provisioning/validation, reservation and reclamation; ticket/change-control integration, escalation and adopted cross-domain processes |
| 7.2 Data and governance | Scoped address identity, hierarchy, versioned metadata, overlap guards, approval controls and audit (S5-05/11/12) | Customer normalization and adopted governance/ownership; security segmentation and trusted enterprise identity. Separate address scopes do not prove tenant access isolation |
| 7.3 Reconciliation | Synthetic DHCP/routing evidence, discrepancy detection, manual cycles and configurable controlled-time scheduling (S5-03–10) | Live subnet/IP/DNS/DHCP/CMTS integrations and continuous operational reconciliation. Controlled time does not establish elapsed-hour endurance; S5-09 remains partial |
| 7.4 Automation | API-driven fixed local allocation and reconciliation with retry/rollback guards (S5-03/04/10/12) | Reservation, real DNS/DHCP changes, service activation, compliance workflows and zero-touch external orchestration. External provisioning remains simulated; general import-triggered reconciliation is deferred |
| 7.5 Reporting | Lease-based occupancy, p95, conditional capacity forecasts, pinned results and one preset/export path (S5-05/06/07) | Customer reporting/KPI acceptance, reconciliation compliance and full data-quality reporting. Lease occupancy is not traffic; an inactivity finding is an investigation candidate, not safely reclaimable or released space |
| 7.6 Architecture | Central API/SQLite application, browser UI, hierarchy, scoped reuse, fixed actor controls and local workflow/audit (S5-01/05/11/12) | Target enterprise platform/integration acceptance, trusted RBAC, full lifecycle enforcement and production scalability evidence. HA and carrier-grade operation are unproved |
| 7.7 Normalization and migration | Canonical synthetic imports and validation; one historical application schema-v3 backup/restore/upgrade (S5-03/15/16) | Real-source consolidation, cleansing/deduplication, metadata normalization, migration planning, parallel validation and domain cutover. An internal schema upgrade is not customer data migration |
| 7.8 Implementation and deployment | Compiled local dashboard/API startup and populated local preservation/restart (S5-01/14) | Spencer's portable package and target-host/recipient evidence, customer integrations/workflow rollout, training and production transition. macOS proof does not establish Docker/Compose/Linux operation |
| 7.9 Operating model | Fixed-team ownership/acknowledgement, audit and reconciliation configuration illustrate controls (S5-08/12/13) | Adopted data/process accountability, audit procedures, change control, ongoing reconciliation ownership and continuous improvement practices |
| 8 Deliverables | Selected engineering architecture, data contracts, reconciliation/scheduling design, implementation and state-operation documentation | Accepted program deliverable pack, including lifecycle/governance, migration strategy, operator runbooks, reporting framework, training and executive roadmap; see the documentary limits below |
| 9 Program outcomes | Selected local mechanisms and synthetic calculation results above | Trusted customer inventory, live-network reconciliation, actual duplicate remediation, automated provisioning, adopted lifecycle/governance, measured operational improvement and scalable production operation |

**Phase 2 status: selected platform mechanisms demonstrated locally; customer implementation, operational adoption and program outcomes remain incomplete.** Detection of a conflict is not its elimination; an allocation approval is not successful external provisioning.

## Documentary evidence and final acceptance

Existing engineering documents provide bounded design material. They do not establish delivery of the entire Phase 2 section 8 pack or approval by customer stakeholders. Historical plans defer to the current [status](STATUS.md) for implemented and observed behavior. Track the 12 deliverables separately:

| Section 8 deliverable | Available material and acceptance limit |
|---|---|
| Target architecture | [Demo architecture](ARCHITECTURE.md) supplied; customer target-platform design/approval pending |
| Lifecycle documentation | [Fixed workflow scope](parts/05-workflow.md) and [contracts](CONTRACTS.md) supplied; complete adopted lifecycle pending |
| Governance framework | Local role/evidence rules documented; customer governance framework and accountable ownership pending |
| Normalized data model | [Demo data contracts](CONTRACTS.md) supplied; real-source mapping, cleansing and customer model acceptance pending |
| Reconciliation design | [Rule scope](parts/03-reconciliation.md), contracts and [schedule design](SCHEDULING_CONTRACT.md) supplied; live integration design/acceptance pending |
| Automation/orchestration design | Fixed workflow and scheduled synthetic acquisition documented; external orchestration design/acceptance pending |
| Migration strategy | Separate reviewed, unadopted delivery-method proposal in PR #9; customer-specific migration/cutover strategy pending |
| Implementation plan | [Weekend demo plan](PLAN.md) supplied; customer implementation/rollout plan pending |
| Operational runbooks | [Core state-operation instructions](STATE_OPERATIONS.md) and the accepted [native demo runbook](DEMO_RUNBOOK.md) supplied; Spencer's package/operator handoff and customer runbook acceptance pending |
| Reporting framework | [Demo dashboard scope](parts/04-dashboard.md) and actual saved-run/export evidence supplied; customer KPI/reporting framework acceptance pending |
| Training materials | Substantive user/operator guidance is supplied in the demo story, runbook and state-operation documents; delivered training, human practice and recipient acceptance remain unestablished |
| Executive roadmap | Separate reviewed, unadopted delivery-method proposal in PR #9; customer-approved roadmap/provider commitments pending |

Delivery-method PR #9 remains a separate proposed document, **reviewed documentary-only / NO MERGE**; see [the review and four bounded rows](handoffs/delivery-method-lead-review.md). Its migration/governance/roadmap proposals are not executed customer operations or provider commitments. Spencer retains portable delivery, operator instructions and recipient handoff; core retains state-command correctness. Neither lane is assigned customer discovery, a full migration program or additional features by this record.

Final lead acceptance must carry both views:

- The 111 questionnaire rows, each with its own demonstrated/partial/documentary/missing evidence and remaining clauses.
- The phase-section limits above, including the outstanding validated Phase 1 report and Phase 2 integration, lifecycle, migration, training, governance and production-transition outcomes.
- The exact application/packaging candidate and unmerged dependencies, plus actual target-host/recipient evidence before portable acceptance.

The unchanged accepted application has since entered main through PR #34. This addendum grants no new execution; Part 6 package/recipient gates remain in [CURRENT_HANDOFF.md](CURRENT_HANDOFF.md).
