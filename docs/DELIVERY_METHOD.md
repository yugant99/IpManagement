# Delivery method — proposed

Draft for project-lead and product-owner review, 2026-09-19. This is a reusable process proposal for the synthetic IPAM demonstration and possible later adoption. It supplies documentary support, not an executed operating history, customer assessment, migration result, recipient acceptance or commercial commitment. No tests, builds or runtime operations were performed for this document.

Use the [questionnaire row map](QUESTIONNAIRE_ROW_MAP.md), [priorities](QUESTIONNAIRE_PRIORITIES.md) and [scope delta](QUESTIONNAIRE_SCOPE_DELTA.md) for scope; [shared contracts](CONTRACTS.md), revision `demo-v2-questionnaire`, remain authoritative for engineering. The [persistent project lead](PROJECT_OVERSIGHT.md) owns evidence classification, acceptance and integration. This proposal changes no application interface or operator procedure.

## Questionnaire mapping and evidence boundary

| Row | Documentary support in this draft | Still required; not demonstrated here |
|---|---|---|
| RFP-083 — Review cadence | Schedule, roles, checklist and review record below | Adoption and completed reviews with retained decisions and follow-up |
| RFP-086 — Improvement method | Issue/feedback backlog and review-to-closure method | Real feedback, assigned actions and evidence of sustained improvement |
| RFP-088 — Domain migration plan | Dependency-led waves, staging, entry/exit gates and rollback | Customer-specific mappings, implemented baseline promotion, authorized execution, reconciliation and sign-off |
| RFP-105 — Product roadmap | Proposed months 1–24, dependencies and decision gates | Product-owner adoption, funded scope and genuine provider commitments |

Candidate classification for all four rows: **design/document supplied for review**. This is not whole-row compliance or demonstrated application capability. Only the lead updates the global evidence ledger. Related training, knowledge-transfer and migration-validation rows receive no automatic completion credit.

## 1. Review cadence and checklist — RFP-083

The following cadence is proposed after adoption; it is not a scheduled automation or a support response commitment. During the short build, use the existing [stage checkpoints](CHAT_STAGES.md); the longer cadence applies only if the project continues.

| When | Accountable role and participants | Required input and retained output |
|---|---|---|
| At each feature/stage handoff; before integration | Persistent lead; owning worker; bounded independent reviewer | Exact SHA/PR, dependencies, diff and evidence/gaps → accepted checkpoint, needs changes or evidence pending, with owner and next action |
| Weekly during an adopted pilot | Lead or appointed delivery coordinator; domain/data owners; core; operator as relevant | Open issues, source freshness/completeness, change and exception history, recipient feedback → prioritized backlog and overdue-action decisions |
| Before every migration wave and at its close | Lead; domain/data owner; operator; designated business approver | Completed wave record, reconciliation and recovery evidence → explicit go/hold/rollback and subsequent exit decision |
| Monthly during continuing delivery | Product owner; lead; affected domain owners | Trends using comparable scope/run/definition, repeated failures and feedback → improvement decisions, assigned dates and retained rationale |
| Every three months, through proposed month 24 | Product owner; lead; relevant engineering/provider representatives | Evidence, dependencies, capacity/funding and remaining gaps → adopt, revise or defer roadmap phases |

For each review, mark every checklist item **met**, **unmet**, **unknown** or **not applicable with reason**. Proposed or unrun work is not met. An unknown required gate holds the affected activity; independent work can continue.

- Identify the scope, purpose, accountable owner, affected domains and exact artifact SHA, source batches and saved run IDs where applicable.
- Separate supplied documents, inspected code, observed runtime outcomes, synthetic inputs and simulated external effects. Link evidence for each claim; list unrun or failed checks plainly.
- Examine scope/time identity, source authority, freshness/completeness and accepted/rejected/duplicate records. Missing evidence stays unknown; no telemetry does not prove no use.
- Compare totals and findings using the same saved run and definitions; record discrepancies, partial writes, stale reviews and failed downstream actions. Acknowledgement does not clear a computed anomaly.
- Review open issues, dependencies, overdue actions, recipient feedback and changes since the last review. Give each action an owner and review date.
- For a wave, examine entry/exit criteria, affected writes, rollback readiness and required authorization. Approval of this document does not authorize execution.
- Record the decision, dissent/conditions, next review and receiving owner's acknowledgement. Keep technical acceptance separate from business/recipient acceptance.

Copy one record per review. Blank fields mean incomplete, not accepted:

```text
Review ID / UTC date / type / prior review:
Chair / participants / decision authority:
Scope and RFP IDs / exact SHA or artifact version / wave ID:
Source batches, run IDs, observation windows and evidence links:
Checklist item -> met | unmet | unknown | N/A(reason), evidence or gap:
Decision -> accepted checkpoint | needs changes | evidence pending;
  wave decision, if applicable -> go | hold | rollback:
Conditions / dissent / issue IDs / action -> owner -> due date:
Next review / receiving owner / acknowledgement date or pending:
Evidence location / access owner / retention rule / disposal review date:
```

Retain the record with the referenced immutable evidence and preserve superseded decisions. Before real data is collected, the data owner sets access and retention rules; this draft prescribes no retention duration. Public repository records must stay generic/synthetic and exclude customer records, private attachments and credentials.

## 2. Issue and improvement backlog — RFP-086

Use one register for defects, evidence gaps, risks and improvement/feedback requests; distinguish their types. The register is a proposed working document or issue-tracker format, not a new application queue. It does not imply external ticketing integration or replace the core-owned exception workflow.

| ID / type / opened | Scope / RFP / source feedback | Observation and evidence | Impact / priority | Owner / dependencies | Outcome / next action / dates | State / closure evidence |
|---|---|---|---|---|---|---|
| `<ID; issue, gap, risk or improvement; date>` | `<domain/scope; row; feedback source/date>` | `<observed or proposed; SHA/run/link; unknowns>` | `<impact; blocking/high/normal>` | `<one accountable owner; prerequisite IDs>` | `<intended outcome/closure criterion; action; due and next-review dates or unassigned>` | `<state; reviewer/date/link or pending>` |

This is a blank template, not a customer finding. Proposed priorities: **blocking** prevents a required gate; **high** materially affects correctness or recipient use; **normal** is bounded improvement work. Priority is not an SLA.

1. **Capture:** retain the reporter's observation and context; separate a reported symptom, a confirmed result and a proposed solution. Do not invent reproduction or acceptance evidence.
2. **Triage at the next applicable review:** link duplicates without discarding provenance; identify impact, affected row, prerequisite and owner. Blocking risks go to the lead before the affected activity continues. Missing owner/date stays visible as unassigned.
3. **Decide:** accept for work, defer with reason and revisit date, or decline with rationale. Define the intended outcome and evidence needed for closure before starting; an estimate is not a delivery promise.
4. **Track:** use `new → triaged → planned → in progress → awaiting evidence → closed`; `blocked`, `deferred` and `declined` require a reason. Review overdue items weekly and record changed dates rather than silently replacing them.
5. **Close or reopen:** an independent reviewer or receiving owner compares the outcome with the agreed criterion. Link actual evidence, remaining limits and acknowledgement. Unrun required checks leave the item awaiting evidence. Reopen on recurrence or new contradictory evidence; review recurring themes monthly.

## 3. Domain migration waves — RFP-088

**Proposed method only.** Here, migration means a possible transfer of intended-inventory authority for a bounded network domain; importing observations is a separate operation. Changed intended-inventory imports remain immutable, **staged and not active** under the current contract. A successful import or comparison cannot promote a baseline or overwrite approved allocations. Baseline promotion and live migration execution are outside the delivered capability claimed here.

Wave names below are illustrative, not an assessment of a customer's estate. Before choosing order, map domain dependencies to real `scope_id`, address family, prefixes/pools, authority and applicable time. Domain labels do not establish routing or tenant isolation. Stage shared prerequisites first; never move a consumer before its prerequisite is ready. Repeat bounded waves rather than migrating every domain together.

| Wave | Entry criteria | Proposed work and exit criteria | Rollback/hold boundary |
|---|---|---|---|
| W0 — Domain map and source agreement | Named domain/data owners; agreed purpose and permitted data access | Catalogue scope/time mappings, authoritative sources, consumers/shared dependencies, counts, exclusions and unresolved records. Exit: owners agree the map, wave order, reconciliation thresholds, recovery scope and required approvals; unresolved identity/authority blocks its domain | Existing authority stays in place; revise the proposal and retain previous mappings |
| W1 — Isolated lab domain rehearsal | W0 complete for the selected fictional domain; compatible artifact and approved evidence set; any execution separately authorized | Stage candidate inventory; rehearse comparisons and recovery when implemented/authorized. Exit: receipts account for every input, explanations cover mismatches and unknowns, saved evidence meets agreed criteria, and recovery outcome is recorded | Keep current intended authority; hold further imports/actions on failure, preserve failed-batch evidence. No automatic deletion or promotion of staged data |
| W2 — One bounded operational domain | Relevant W1 evidence accepted; shared prerequisites ready; real scope/data approved; implemented and reviewed promotion/change controls; authorized window, operator and recovery procedure | Shadow comparison first; cutover only after a recorded go decision. Exit: approved reconciliation, preserved assignments/audit, agreed observation period complete, required downstream outcomes evidenced separately, domain and recipient acknowledgement recorded | Stop affected changes and invoke the approved recovery plan on trigger. Restore previous authority only after reconciling intervening writes and actual downstream effects |
| W3 — Further domains and shared dependencies | Previous applicable wave exits accepted; each domain repeats W0/W2 gates; all affected shared-service owners agree order and recovery impact | Expand in dependency order with separate records and bounded windows. Exit: every included domain meets its criteria; residual work has owners; final authority and support/handoff boundaries are acknowledged | Pause dependent waves; recover only to the agreed consistent boundary. A shared-state rollback may require coordinated recovery of several domains |

W1 has no claimed rehearsal result. W2/W3 execution remains deferred until the missing capability and authorization exist. A calendar date cannot satisfy an entry gate. Actual downstream DNS/DHCP/router actions require their own implemented controls and evidence; the demonstration's simulated outcomes cannot satisfy these exit criteria.

Before any executable wave, complete this record; unassigned approvers, thresholds, recovery points or observation periods hold execution:

```text
Wave ID / domain owner / affected scope IDs, address families and time window:
Source authority before/after / candidate batch IDs / artifact and schema version:
Prerequisite waves/shared consumers / exclusions / data-access approval:
Input = accepted + rejected + duplicate counts; mismatch/unknown disposition:
Entry evidence / reconciliation thresholds / exit criteria / observation period:
Change approver / operator / authorized window / affected write controls:
Recovery point and evidence / all affected domains / allowable loss and intervening-write handling:
Rollback triggers / decision owner / recovery procedure reference / stop condition:
Actual go/hold/rollback decision and time / outcomes or not executed:
Domain and recipient sign-off or pending / residual backlog / next review:
```

**Proposed rollback procedure:**

1. Stop the wave and dependent changes on unexplained scope/authority conflicts, threshold breaches, lost audit/allocations, failed required external actions or an unavailable recovery path. The named change approver records rollback versus continued hold; no silent fallback.
2. Capture the failure, current state, source/run references and all writes since the recovery point. Preserve audit and failed evidence outside any state that recovery could replace, within approved access controls.
3. Assess the whole recovery boundary with core and the operator. One shared SQLite database is not per-domain restore: restoring it can undo other domains' allocations and audit. Account for every affected domain, stop the service and all database writers before restore, obtain exclusive app-data access and reconcile intervening writes. If safe recovery cannot be established, remain on hold and escalate.
4. Use only an implemented, reviewed and authorized recovery procedure for the compatible artifact/schema. Core owns state correctness; Spencer owns the corresponding operator guidance under [Part 6](parts/06-portability.md). This document supplies no executable restore command. Resetting a synthetic scenario is not migration rollback, and restoring local data does not reverse external network changes.
5. Before resuming, reconcile intended authority, allocations/audit and any real external effects; record discrepancies and the recovery outcome. Require renewed owner approval and entry evidence. A failed or unrun recovery remains failed or unverified.

## 4. Handoff responsibilities

Repository responsibilities below follow [project oversight](PROJECT_OVERSIGHT.md). Future domain, product and recipient roles must be assigned for an adopted engagement; they do not establish a staffed delivery/support team.

| Owner | Supplies / receives | Acceptance boundary |
|---|---|---|
| Persistent project lead | Assignments, exact integration baseline, bounded review, questionnaire evidence and next prompt | Owns global status and stage/merge decisions; worker completion is a claim for review |
| Core owners, Parts 1–5 | Application/schema/import/rule/workflow/state correctness, exact commits, supported interfaces and evidence/gaps → lead and Part 6 | Own technical behavior and fixes; do not claim packaging or runtime results from source inspection |
| Spencer, Part 6 | Package, operator instructions, persistent-storage integration and recipient handoff using core interfaces | Owns packaging/operator files; readiness and persistence need actual prerequisite/evidence records. This draft adds no HA, support or production-migration assignment |
| Domain/data owner — to be designated | Source authority, mappings, permitted data, discrepancy decisions and domain exit review | Accepts domain reconciliation within agreed scope; missing evidence cannot be waived by a label |
| Product/business owner — to be designated | Outcome priorities, roadmap adoption, resource decisions and designated change authority | Approves business scope; provider staffing, pricing, licensing, support and compliance claims require genuine provider evidence |
| Receiving operator/user — to be designated | Receives versioned artifact/instructions, limitations and residual backlog; supplies walkthrough feedback and acknowledgement | Knowledge transfer is complete only for the activities actually observed and acknowledged; no recipient acceptance is recorded here |

Every handoff carries exact SHA/PR and dependency state, owned paths, supported behavior, synthetic/simulated/unverified limits, evidence links, unresolved issues with owners, and the next bounded action. The receiver records acknowledgement or missing prerequisites. Point to Spencer's [Part 6 handoff](handoffs/part-6.md) for operator instructions; do not duplicate or invent commands. A later walkthrough should cover evidence interpretation, unknown states and issue reporting; executing the app or recovery exercises requires separate authorization.

## 5. Proposed 24-month roadmap — RFP-105

**Proposal requiring product-owner adoption; no vendor-approved release dates, staffing, budget, SLA or feature commitment.** Month 1 starts only after an agreed adoption date; there is no assumed start date. Each phase may be reduced, deferred or stopped at the quarterly review. Missing prerequisites move downstream work; elapsed time earns no acceptance credit.

Assumptions: a sponsor and domain owners are assigned; permitted representative data becomes available; scope, funding and engineering capacity are agreed; runtime/migration activities receive their own authorization. The current one-app/SQLite synthetic demonstration is the starting design, not evidence of production suitability. No live customer findings inform this proposed sequence.

| Proposed window | Intended outcome | Dependencies / exit decision and evidence sought |
|---|---|---|
| Months 1–3 — Adopt and establish a baseline | Agree use cases, domain/source map, review/backlog ownership, workload and acceptance definitions; assess the actual demo candidate | Product-owner adoption, access and resourcing → approve a bounded pilot plan with explicit gaps and authorized evidence needs |
| Months 4–6 — Complete the bounded demonstration and rehearse | Close selected source-to-finding/workflow gaps; obtain package, persistence and W1 recovery evidence where authorized; collect recipient feedback | Compatible core/Part 6 artifacts, implemented state controls and permitted synthetic data → accept only observed capabilities; otherwise retain evidence pending |
| Months 7–9 — Representative read-only pilot | Stage approved representative data for one domain; compare scope, provenance, freshness and findings; exercise the review/improvement method | W0/W1 gates, source-owner access and approved isolation → decide whether data quality and usefulness justify further engineering; no baseline cutover |
| Months 10–12 — Qualify a production candidate | Assess identity/access, integrations, workload/concurrency, recovery, security and operability requirements; implement the agreed prerequisite changes | Pilot evidence and funded requirements → choose architecture from measured needs, including whether SQLite is suitable; record authorized capacity/recovery evidence and unresolved limits. HA/DR or certification remains unclaimed without evidence |
| Months 13–18 — Consider the first controlled migration | Implement/review missing promotion controls; qualify recovery and external change handling; execute a bounded W2 only if separately authorized | Qualified candidate, explicit change authority, approved W2 entry gates and recipient readiness → record actual cutover/recovery/observation results and sign-off; otherwise stay staged/read-only |
| Months 19–24 — Expand selectively and reassess | Repeat W3 for approved domains; prioritize measured improvements, operating handoff and the next planning horizon | Accepted prior exits, shared dependency readiness, funded capacity and genuine support arrangements → review domain outcomes, residual risk and recipient acknowledgement; propose the next roadmap from evidence |

This sequence proposes future work; it does not add these capabilities to current questionnaire totals.
