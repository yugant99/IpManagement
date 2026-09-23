# Next-phase integration requirements packet

**Prepared:** 2026-09-23. **Owner:** advisory requirements lane; Main Lead 6.0 task `01a0cf70-c4e0-7ed2-b50b-834609e6d909` retains project acceptance and merge authority. **Base:** `339d688c054b586404ac41f605d1852d4d61379c` on `origin/main`. This packet proposes acceptance boundaries; it authorizes no IPAM product edit, deployment, external ticket write, customer-data use, or evidence promotion.

## Evidence basis and interpretation

- The accepted 111-row ledger remains **39 Demonstrated / 18 Partial / 10 Documentary / 44 Missing** in [the row map](QUESTIONNAIRE_ROW_MAP.md). The private post-meeting workbook's `Technical Requirements` column E has **92 Demonstrated / 12 Documentary / 7 Missing**. Those labels express intended/future capability, not observed evidence. Workbook SHA-256: `9ad454822b342f29bd63533ba353cc676a74f073b290de1bf85554f83a06e02e`; private workbook contents stay outside Git and model requests. For these technical items, Excel row = RFP number + 2.
- [T028 adjudication](../specs/001-postmeeting-bridge/delivery/lead-adjudication.md) accepted the pinned Tier A local synthetic technical candidate, with [T025 evidence](../specs/001-postmeeting-bridge/delivery/independent-evidence.md). The ongoing personal trial has setup observations, not a completed human walkthrough. Its local record is outside Git under `Downloads/Ip_inventory/outputs/postmerge-trial-20260923/trial-session.md`; the trial checkout and credentials remain separate.
- [The current ticket contract](../specs/001-postmeeting-bridge/contracts/ticketing.md) and `backend/ipam_demo/access.py` permit `simulated` or `disabled` connector modes. No live ServiceNow adapter is present. A simulated ticket ID, acknowledgement, or local allocation decision is not external ticket creation or network provisioning.
- The private local screening covered all 92 workbook-labeled Demonstrated rows. The tables below retain its direct integration and conditional dependencies without converting each row into a separate connector.

## Direct integration requirements among the 92 labels

All rows in this table are workbook-labeled **Demonstrated** but need the external or trust-boundary proof stated below. The accepted evidence class is shown separately.

| RFP / Excel row | Accepted class | Integration and smallest missing proof | Inherent impact* |
|---|---|---|---:|
| 011 / 13 | Missing | Named DNS/DHCP product and authorized management read/write with provider readback | 3 read; 5 write |
| 036 / 38 | Partial | Discover one authorized source with source identity, scope, time and completeness | 3 |
| 042 / 44 | Missing | ServiceNow sandbox ticket create, fixed route, external ID and state readback | 3 |
| 044 / 46 | Missing | Named EMS/vendor/version, selected operation, object mapping and observed response | 3 read; 5 configuration write |
| 046 / 48 | Missing | Named OSS/BSS service identity contract and readback; opaque local references do not suffice | 3 read; 5 write |
| 048 / 50 | Missing | Entra/AD identity integration with claims-to-scope mapping and denial/revocation | 5 |
| 049 / 51 | Missing | Chosen SAML/OAuth SSO round trip with claims and session boundary | 5 |
| 050 / 52 | Missing | LDAP clause demonstrated against a directory if it remains required | 5 |
| 051 / 53 | Missing | Client-certificate identity validation, mapping and invalid/expired/wrong-scope refusal | 4 |
| 056 / 58 | Missing | Authorized DHCP change and provider before/after readback; synthetic lease observation is separate | 5 |
| 058 / 60 | Missing | One selected IaC resource lifecycle with plan/apply/readback and safe repeat | 5 |
| 061 / 63 | Missing | Continuous scoped observation from a real chosen source, with freshness/failure evidence | 3 |
| 067 / 69 | Missing | Three-source DNS, DHCP and CMTS validation, keyed by scope/time with ambiguous joins visible | 3 read; 5 auto-remediation |
| 098 / 100 | Missing | Authoritative subscriber/service identity and actual allocation/provisioning outcome | 5 |
| 096 / 98 | Missing | Cross-category provider DNS/DHCP: decide operating services versus managing existing providers; then prove selected service/operation | 3 read; 5 write/serve |

*Impact is the ordinal rubric below, not a vulnerability finding. RFP-096 is a separate cross-category dependency, bringing the selected set to 15 requirement rows, not 15 connectors.

Five workbook-labeled **Missing** integration rows remain on the roadmap: **041 / 43** CMDB read or synchronization; **045 / 47** CMTS access; **047 / 49** provisioning system execution; **052 / 54** service-account credential custody/rotation/revocation; **055 / 57** DNS update execution. ServiceNow Incident does not prove CMDB, and a DHCP change does not prove DNS update or subscriber provisioning.

## Conditional integration dependencies

These rows can consume one or more selected external sources or destinations. They do not each imply a new connector. Excel locators follow the verified `RFP + 2` technical-sheet mapping.

| Requirement rows / Excel rows | Condition and proof boundary |
|---|---|
| 001/3, 053/55, 054/56, 057/59, 059/61, 070/72, 080/82, 091/93 | Local lifecycle, policy and approval can be shown in IPAM; real network allocation, reclaim, remediation or orchestration needs an authoritative provider and readback. No telemetry does not mean safe to reclaim. |
| 024/26 | If "containerized/virtualized networks" means managing their address objects, select a platform/controller and operation. Running IPAM in a container or VM alone is deployment proof. |
| 062/64, 063/65, 064/66, 065/67, 066/68, 069/71, 073/75, 074/76, 075/77, 076/78, 077/79, 078/80, 083/85, 085/87, 095/97 | Saved calculations, reconciliation and reports can use authorized imported inputs. Live-network claims need scoped, timestamped, sufficiently complete source evidence; missing or stale data remains unknown. |
| 022/24, 043/45, 072/74, 081/83, 082/84, 084/86 | In-app health, events, notices and handoff are local. External paging, team receipt or change-system behavior requires the selected destination and observed delivery. |
| 033/35, 034/36, 037/39, 087/89, 088/90, 089/91 | Source-specific normalization and migration require representative authorized inputs, mapping, rejected-row accounting and before/after reconciliation. A file may suffice; Tier A assessment is not cutover. |
| 004/6, 008/10, 021/23, 079/81 | Permissions, tenancy, encryption and ownership require explicit architecture and human authority. Adding SSO, HTTPS or a ticket cannot establish all of them. |

RFP-014–020/23, 025/27, 090/92, 093/95, 094/96 and 097/99 also need resilience, deployment or measured scale evidence, not another SaaS account. RFP-040/42, 086/88, 100/102, 101/103 and 103/105 need an assessment method or real business/reference/staffing evidence.

## Six open decisions for Pooyan, spanning eight rows

The options below are proposals. No option is recorded as selected or accepted.

| Rows / Excel rows | Decision and concrete options | Acceptance definition to obtain |
|---|---|---|
| 008 / 10 | Internal domains/teams, independent customer tenants, or both? | Boundary, administrator powers, shared objects, record/export/job/audit isolation; allowed and denied cross-boundary scenarios. Current local domain access only addresses the first option. |
| 024 / 26 | Deploy IPAM in containers/VMs, manage their networks, or both? | Named platform/version, object types, read/write actions, authentication, freshness and readback. |
| 025 / 27; 093 / 95; 094 / 96 | Which population and workload must pass, on what target? Is **more than 50,000,000 active IPv4 addresses** mandatory at initial acceptance? | Individually stored active assignments versus address-space capacity; IPv4/IPv6 classes, history/audit size, users/concurrency, read/write/import mix, sustained duration, p95/p99 latency, error budget, target hardware and approver. A one-million-record plan does not prove 093. |
| 040 / 42 | Gap assessment/roadmap, scored maturity, or benchmark against a defined peer set? | Inputs, dimensions, scoring anchors if used, target state, reviewer and accepted artifact. Unknown evidence stays not assessed. |
| 044 / 46 | Which EMS/vendor/version and equipment; read-only status/inventory or configuration write? | Object IDs, field authority, API/sample, auth, poll/events, error/retry, sandbox and observed selected operation. |
| 096 / 98 | Operate DNS/DHCP as a provider service or manage an existing product via API? | Vendor/version, zone/scope, operation, approval, timeout/duplicate behavior, readback, rollback, scale and operations owner. |

## Candidate first slice: ServiceNow personal sandbox

The user requested a path of **synthetic customer/service context → IPAM → real ServiceNow ticket → fixed network team/test engineer → status change in ServiceNow → IPAM readback**. The smallest candidate is one synthetic **Incident**, subject to the requirement owner's choice of Incident versus request/change/task workflow. ServiceNow documents free [Personal Developer Instances](https://www.servicenow.com/docs/r/application-development/personal_developer_instance_guide.html) for individual learning and experimentation, not business or production use, and an [Incident REST create flow](https://www.servicenow.com/docs/r/api-reference/rest-api-explorer/t_GetStartedCreateInt.html). A PDI can prove an experimental sandbox round trip, not customer/enterprise readiness.

**Inputs needed before implementation:** instance URL and availability; dedicated API identity and least-privilege table/field ACLs; chosen record type and permitted state transition; fixed assignment-group and test-assignee IDs; synthetic field map and service-reference meaning; stable searchable correlation and external ID; rate/error/timeout/lookup behavior; secret custody and revocation; approved sandbox write scope. The API identity's create/read permissions and the human test engineer's assignment/state permissions are distinct. A personal signup alone supplies none of these mappings.

**Proposed behavior:** one domain-scoped synthetic request produces one immutable business identity; the operator explicitly sends the allowlisted payload to the approved sandbox; IPAM stores the external `sys_id`/number and observes group/assignee; a human changes status in ServiceNow; IPAM manually refreshes and records the observed status/time. Wrong-domain access fails. A lost response remains **unknown** until a correlation lookup resolves it; ordinary retry must not create another logical ticket. The exact uniqueness/lookup and idempotency contract must be checked against the chosen instance before a live retry is implemented. Ticket outcome remains separate from local allocation and from provisioning. A ticket closure does not resolve an IP finding automatically.

**Acceptance gate:** retain redacted request/response evidence showing one external ID, fixed team and person, manual external state change, IPAM readback, same-correlation retry/uncertain-outcome behavior, wrong-domain denial and failure visibility. A sandbox record qualifies only that sandbox. CMDB, OSS/BSS, subscriber systems, DHCP/DNS, discovery, EMS, identity federation and provisioning retain separate contracts and evidence.

## Ordinal inherent security impact

This is a **1–5 analyst estimate of plausible harm from a wrong identity, authority or action boundary before controls**. It is not CVSS, a vulnerability claim, likelihood, residual-risk certification or readiness score. Re-score when product, data and operations are named. A synthetic PDI experiment has a smaller actual blast radius than the eventual customer integration.

1. Isolated synthetic/public information; no external authority.
2. Limited internal read with minimal sensitive context.
3. Topology/customer-context read or bounded ticket/notice write; confidentiality or workflow consequence.
4. Credential/trust configuration or privileged business-record change; access or authoritative-record consequence.
5. Tenant authorization, network/address write or subscriber provisioning; cross-customer access or service disruption is plausible.

## Priority and independent gates

1. **Now: local trial feedback.** Classify reproduced Tier A failures as defects, deferred requirements as gaps, and new behavior as requested changes. The local trial is still awaiting the user's walkthrough; do not claim human completion.
2. **Next chosen implementation: one ServiceNow PDI ticket round trip.** Gate on the instance/identity/table/routing/correlation decisions above. Keep it isolated, synthetic and manual. This is a candidate for 042 and bounded aspects of 081/83, 082/84 and 084/86; it cannot close 046/48, 047/49 or 098/100.
3. **Provider integrations:** select one DNS/DHCP operation and named product separately. DHCP simulation is deferred Tier B; actual DHCP write/readback and DNS/CMTS validation are distinct future gates.
4. **Recipient Linux portability:** an actual selected Linux amd64 recipient target, package transfer, startup/persistence/recovery and owner observation. The completed local T025 is not this gate.
5. **Human rehearsal and business approvals:** T026 human participation/acknowledgement remains PENDING / NOT RUN; T019 licensing, support, staffing, references and business-owner signoff remain open. A person trying the personal trial may supply bounded feedback, not automatically close recipient or business acceptance.
6. **Tier B and scale:** remain locked until separately authorized, specified and measured. No automatic dispatch follows this packet.

## Bounded evaluation and executor workflow

Sol writes the requirement/evidence packet; Jev receives only minimized public/synthetic claims and typed questions about evidence sufficiency, ambiguity, impact and routing; a reviewer challenges concrete discrepancies for **at most one reconciliation round**; Main Lead 6.0 adjudicates technical scope, and Pooyan/user owns business interpretations. Jev is advisory and cannot approve evidence, spend, external writes or merges. Its [actual access outcome and local harness](jev-advisory-evaluation.md) are recorded separately.

For a later authorized implementation, the preferred executor is exact `opencode-go/muse-spark-1.3-contributor#xhigh`, with exact `opencode-go/deepseek-v4.1-flash` as conditional fallback. One synthetic probe reached the Muse xhigh route on this date; it does not verify capacity for a full task. Restrict Contributor input to approved tracked public/synthetic relative paths. Exclude raw workbook, customer material, untracked outputs, existing databases, credentials and private chat history from all model payloads. No Grok 4.6/4.7, heavy Kimi/Qwen, heavy cap-consuming models, Opus or Fable is selected here.
