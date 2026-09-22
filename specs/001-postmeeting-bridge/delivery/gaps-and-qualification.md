# T019 — Maturity, authority gaps and future qualification register

Task: **T019**. Owner: Sol fallback replacing the quota-blocked Grok 4.6 documentation scout under Main Lead 4.0. Stage: Stage 1 (post-meeting bridge).
Leased path: this file only. Branch: `codex/bridge-t019-qualification`. Exact source base: `ab005d8bf3b6c57e0a071707796d18514c278674`.

**Mode:** documentary source review. Requirements: FR-010, FR-012, FR-014, FR-016, FR-017, FR-018 and FR-020. The fixed-workflow/IaC row records the adjacent FR-022 exclusion required by T019; it does not expand implementation scope. Governing inputs are the accepted T002 register, `spec.md`, `qualification.md`, C-O, and the canonical 111-row map.

**Non-claims:** no tests, builds, runtime, benchmark, failover, recovery exercise, live connection, vendor research, customer assessment, private evidence review, commercial commitment, named human assignment or questionnaire re-adjudication occurred. This register is a template and gap boundary, not acceptance.

---

## 1. Evidence vocabulary and owner roles

Evidence labels in this document do not create new questionnaire classes:

| Label | Meaning |
|---|---|
| **Retained class** | `Demonstrated`, `Partial`, `Documentary` or `Missing` copied from `docs/QUESTIONNAIRE_ROW_MAP.md`; only the Lead may change it. |
| **Documentary boundary** | Source-backed description of present behavior, an exclusion or a proposed protocol; not runtime proof. |
| **Qualification assumption** | Q081–Q088 planning input for a future protocol; not a customer SLA, source requirement, result or row-credit threshold. |
| **Missing / unverified** | Required authority, product, mapping, artifact or observation is absent from the inspected public sources. |
| **Future evidence gate** | Minimum evidence needed before the Lead may assess a claim; passing is not asserted here. |

Owner labels are roles, not invented people:

- **Lead**: assigns actual human owners, controls canonical row adjudication and accepts evidence.
- **Terra**: architecture/application owner for later implementation decisions; this task assigns no implementation.
- **Spencer**: operator/package artifact owner only; not HA, scale, vendor or commercial owner.
- **Human-int**: authorized integration/vendor-contract owner, currently unassigned.
- **Human-biz**: authorized business/commercial owner, currently unassigned.
- **Performance owner**: future authorized workload/environment operator, currently unassigned.
- **Luna**: independent verifier after explicit validation authority; cannot self-accept results.

---

## 2. Evidence-classed gap and disposition register

| Area / requirement | Retained class and current boundary | Missing authority or capability | Owner role | Future evidence gate |
|---|---|---|---|---|
| **EMS / access network** — FR-010; RFP-044/045/067 | **Missing.** T002 records only named future targets and desired read-only interface/subnet status fields. No product/version/interface or complete DNS/DHCP/CMTS join is established. | Selected product/version, legally available operation contract, authoritative identifiers, scope/time mapping and coverage. Unknown or ambiguous joins remain unmapped. | Human-int selects and owns the contract; Terra implements only after contract freeze; Luna later verifies. | Official documentation for the selected interface plus an authorized sanitized sample and positive, negative and ambiguous mapping observations. Writes require a separate authorized operation. |
| **DNS** — FR-012; RFP-055 | **Missing.** Existing reports can export IPAM context; there is no DNS `source_kind`, zone/record/nameserver schema, parser, live query, machine validation or write. | Named DNS authority/product, scoped read contract and source-to-export comparison. Tier A keeps writes unavailable. | Human-int for any future DNS source; Terra preserves the no-write boundary; Lead adjudicates. | Authorized interface inspection and source/export comparison. Missing or stale DNS stays unknown; absence of a write path must be observed before making a negative claim. |
| **Metadata, governance and maturity** — FR-014; RFP-027–032/038/040/054/084/085 | Retained classes are mixed: bounded schema/policy rows include **Demonstrated**, governance/workflow rows include **Documentary**, and RFP-040 is **Missing**. T002 records fixed string metadata, hierarchy and local policy; none establishes adopted customer governance or a customer maturity score. | Customer vocabulary, accountable owners, current-state workflow evidence, assessment method, reviewer and approved benchmark if one is required. | Human-biz/data steward/current-state assessor, all unassigned until Lead assigns actual people. Terra owns only existing technical guards. | Complete the template in §4 with supplied evidence. Reviewer must mark unsupported dimensions `not assessed`; no numeric maturity score is inferred from the demo. |
| **Stopped recovery / recovery point** — FR-016; RFP-018/019/020/023 | RFP-018 **Demonstrated** for bounded stopped backup/restore; RFP-019 **Missing** because no implemented/measured backup policy establishes the required loss window; RFP-020 and RFP-023 **Partial** at their exact accepted candidates. Prepared-host timing and one Mac-to-Linux transfer do not establish full outage recovery, geo-DR or sustained hybrid operation. The 24-hour snapshot-age value in §3 is a qualification assumption, not RFP-019 evidence. | An approved backup policy and actual measured loss window, plus the full incident boundary: diagnosis, artifact retrieval/transfer, replacement provisioning, restore/migration/startup, logical business checks, loss accounting and key/dependency access. | Platform operator owns any approved backup policy; Terra owns architecture/state gaps; Spencer owns an approved operator procedure; Luna independently verifies; Lead adjudicates. | Pin the required loss window and backup schedule/retention/custody in an approved policy, then later observe an authorized exact-candidate incident using identified snapshots and compare the last acknowledged state with restored state. Record actual loss, start/end, excluded preparation and preserved assignment/audit checks. Source SLA controls if stricter. |
| **HA / failover / geography** — FR-016; RFP-014–017 | **Missing.** Current topology is one process and one SQLite store. Two running processes, packaging or a larger host are not HA evidence. | Failure model, replication/topology, writer election/fencing, partition/rejoin behavior, automated failure detection/promotion and separated recovery site. | Terra for future architecture; platform operator for an authorized environment; Luna independently verifies; Lead adjudicates. | Observe process loss, host loss, partition and rejoin on a pinned design, with zero conflicting successful allocations, preserved history and explicit degraded/refusal behavior. |
| **Encryption** — FR-016; RFP-021 | **Missing.** Loopback packaging, file permissions, read-only filesystems and a future TLS note do not establish transport or at-rest encryption. | Separate controls for remote transport, database, snapshots, exports, sensitive logs, keys, rotation/revocation and recovery. | Platform/security owner, currently unassigned; Terra integrates only after a frozen contract; Luna verifies. | Authorized configuration inspection and positive/negative certificate checks for transport; encrypted-artifact and key-loss/recovery observations for each at-rest artifact class. No control inherits evidence from another class. |
| **Scale and concurrency** — FR-017; RFP-025/093/094/097 | **Missing.** Bounded synthetic pools and lock checks are not carrier scale, millions of logical records or independent-user concurrency. No workload in §3 was run. | Authorized environment, exact dataset manifest, independent principals, operation mix, duration, resource limits, raw results and architecture changes needed beyond single-writer SQLite. | Performance owner operates later test; Terra owns architecture gaps; Luna interprets independently; Lead controls credit. | Execute an approved protocol against exact source/package SHA and retain counts, throughput, percentiles, refusals/errors, corruption/disclosure/duplicate-allocation checks and raw results. Smaller runs prove only their exact bounds. |
| **Virtual/container network inventory** — FR-018; RFP-024 | **Missing.** Docker/Compose packages the application; no overlay/VPC/CNI object, tenant/network ID, controller mapping or managed-network `source_kind` exists. | Decision that managed-network inventory is required, selected source/controller, object identity, scope/time mapping and read/write authority. | Human-int selects source and contract; Terra owns any later data model; Spencer must not recast packaging as inventory. | Authorized sanitized object mapping with positive/negative/ambiguous joins. Mutations require a separately selected controller operation and observed outcome. |
| **Fixed workflow and IaC** — T019 adjacent FR-022 boundary; RFP-058/091/111 | RFP-058 and RFP-111 are **Missing**; RFP-091 is **Partial** for deployment of the same fixed workflow. Existing fixed transitions, Compose and a generic API are not a workflow designer, orchestration platform or IaC integration. | Actual administrator-defined lifecycle contract, compatibility/history rules, or one selected IaC tool/resource/operation contract. | Product/lifecycle owner and Human-int, currently unassigned; Terra implements only after Lead contract amendment. | Configurable workflow claim requires versioned admin-defined transitions with enforced allowed/refused behavior and preserved history. IaC claim requires a chosen tool contract plus an authorized observed operation/readback. |
| **Business, delivery and licensing** — FR-020; RFP-099–103/105/107–110 | RFP-102 and RFP-105 are **Documentary**; the remaining listed rows are **Missing**. Engineering ownership, dependency manifests, audit events and synthetic results do not establish provider references, staffing, commercial terms, support/SLA or certification. | Authentic references, provider staffing/capacity, support operation, approved license offer and dependency terms, SLA, compliance scope/evidence, roadmap adoption and approval identities. | Human-biz roles are unassigned; Lead assigns actual people. Agents and technical workers make no commercial commitment. | Approved artifact for the exact claim/population/unit under authorized custody, sanitized conclusion and approval identity. Private evidence stays outside Git. |
| **License continuity** — FR-020 / C-O Q093 | **Documentary boundary only.** Future intent is to preserve running service/data and raise an owner-visible expiry alarm. No licensing engine or commercial policy exists. | Actual renewal owner, notice source/timing, escalation path, applicable terms and any new-operation restriction or grace period. | Human-biz licensing owner, unassigned until Lead assignment. | Authorized commercial terms and owner approval before design or implementation. Do not infer a grace period, shutdown rule or restriction. |

---

## 3. Future qualification assumptions — not measurements

These values come from `qualification.md` / Q081–Q088. They define a first future protocol only. They do not replace a larger source requirement, become an SLA, or support a current capability claim.

| Dimension | Qualification assumption | Required result boundary |
|---|---|---|
| Recovery | 15-minute planning goal; chosen snapshot no older than 24 hours; zero loss versus that snapshot | Measure full declared incident boundary; list acknowledged operations after the snapshot as recovered or lost. Prepared-host restore alone is narrower. |
| Workload | 80% reads, 15% import/status, 5% changes; 100 accepted observations/second sustained; import batches no larger than 10,000 rows | Record offered/completed throughput and a separately approved mutation submix. No extrapolation from a reduced sample. |
| Active IPv4 cohort | 1,000,000 individually persisted current intended assignments, unique by scope/family/address | Exclude CIDR capacity, reservations, candidates, history and duplicates. Any larger source requirement remains controlling for row credit. |
| Logical corpus | 1,000,000 current assignments; 3,000,000 lease observations over 30 days; 500,000 historical changes; 500,000 audit events; 100 scopes | Report the four classes separately. Raw copies, indexes and saved findings do not increase logical counts. Current importer/history design is not qualified by this plan. |
| Concurrency | 100 distinct principals; one outstanding request each; two-second think time; 10-minute warm-up and 60-minute measurement | Actor switching is not independent-user concurrency. Preserve identity/authorization results and report expected refusals separately. |
| Latency | Reads p95 <=1s / p99 <=3s; decisions p95 <=2s / p99 <=5s; import acceptance/status p95 <=5s | State percentile method and operation counts. Do not hide denials, conflicts or incomplete operations in aggregate latency. |
| Correctness | Unexpected failures/timeouts <=0.1%; zero silent partial writes, disclosure, corruption or duplicate/conflicting successful allocations | Retain every refusal, unknown and interrupted interval. Any integrity or isolation failure blocks that protocol result. |
| HA | Process loss, host loss, partition and rejoin with writer fencing | Zero conflicting successful allocations; record recovery/degraded behavior for each failure separately. No topology is selected by this assumption. |

A future dataset/run manifest must record exact source and package SHA, schema/config/generator versions, seed and synthetic label, scope/family distribution, individually stored active counts, observation intervals/completeness, record classes/history depth, storage duplication, hardware/limits, operation mix, principal count, offered/completed throughput, durations, percentile method, error categories and retained raw-result location. No populated manifest is claimed here.

---

## 4. Evidence-backed maturity assessment template

Use one row per assessed dimension. Blank evidence or an unavailable authorized owner means `not assessed`, not a score of zero and not a maturity finding.

| Field | Required entry |
|---|---|
| Requirement / dimension | Exact FR/RFP ID and narrowly worded claim. |
| Current-state evidence | Public source locator or authorized private evidence pointer; include revision/date, scope and custodian. Never copy private content into Git. |
| Evidence class | Retained class, documentary boundary, qualification assumption, or missing/unverified. |
| Current-state finding | What the evidence supports, with population/environment/time limits. |
| Authority / accountable role | Actual approved owner when supplied; otherwise the role plus `unassigned`. |
| Proposed future state | Explicitly proposed behavior, kept separate from current state. |
| Gap and consequence | Missing artifact/capability and which claim or operation remains unavailable. |
| Future evidence gate | Concrete artifact and/or authorized observation needed to reassess. |
| Reviewer conclusion | `supported`, `insufficient`, `missing`, or `not assessed`, with reason. |
| Approval | Reviewer identity/authority and date only when actually supplied. |

Template rules:

1. Do not compute an overall maturity score without an approved method, weights, benchmark and reviewer.
2. Do not convert demo metadata, workflow documentation or a future-state proposal into customer current-state evidence.
3. Record incompatible sources separately; do not average them into a finding.
4. Keep technical capability, operating adoption and commercial commitment as separate dimensions.
5. A future gate is a condition for reassessment, not a promise that the claim will pass.

---

## 5. Human business-owner register — roles remain unassigned

| Evidence family | Required human role | Required artifact / decision | Current disposition |
|---|---|---|---|
| Provider and telecom references; large-deployment reference | Human-biz reference owner | Approved reference matching exact service, population, unit and outcome | Missing; synthetic demonstration cannot substitute. |
| Delivery staffing and capacity | Human-biz delivery owner | Named people, availability/capacity and ongoing authorized commitment | Missing; engineering agent roles are not provider staffing. |
| Product roadmap | Human-biz product owner | Adoption decision, funded staffing and release commitments | Documentary proposal only; not adopted. |
| Local support and service commitments | Human-biz support/SLA owner | Locations, staffed coverage, escalation, response/availability terms and approval | Missing; §3 numbers are qualification assumptions, not SLA terms. |
| Licensing and continuity | Human-biz licensing owner | Authorized offer/terms, dependency obligations, expiry notice/renewal/escalation policy | Missing; preserve-service alarm is future documentary intent only. |
| Compliance | Human-biz compliance owner | Applicable control scope and authorized assessment/audit/certification evidence | Missing; application audit events are not certification evidence. |

The Lead must assign actual people outside this document. Until then, each role remains `unassigned`; no agent-generated name, approval, capacity or commitment is valid.

---

## 6. Inspection boundary and downstream use

Inspected public sources: T019 in `tasks.md`; FR-010/012/014/016/017/018/020 and adjacent FR-022 in `spec.md`; `qualification.md`; C-O `contracts/operator.md`; accepted T002 `delivery/source-authority.md`; current `docs/QUESTIONNAIRE_ROW_MAP.md`, `QUESTIONNAIRE_PRIORITIES.md`, `STATUS.md`, architecture and relevant part pages.

Not accessed or performed: network/vendor sites, customer/private files, `assessment/`, `audit/`, `outputs/`, attachments, credentials, user configuration, other worktree writes, tests, builds, runtime, SQL, migrations, model calls, Fable, T020 integration work, global status/ledger edits, owner outreach or human acknowledgement.

Downstream users may copy a gap, assumption or evidence gate only with its label intact. Lead review is required before publication or any row/acceptance decision.
