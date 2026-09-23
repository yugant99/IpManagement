# Ambiguity and decision register

Historical ambiguity origins and current agent resolutions. Actual agent answers/challenges are in questions.csv.
Discoverable facts are researched from documents/source, not sent back as decision questions.

## Eight previously identified clarification-pending requirements

| ID | Decision to settle | Current discoverable fact | Candidate recommendation |
|---|---|---|---|
| RFP-008 | Internal domain access boundaries or independent customer tenants? | Current scope/domain labels and fixed actors do not establish either trusted tenant isolation or granular enterprise identity. | Internal domain authorization first; independent tenants deferred unless essential. |
| RFP-024 | Deploying the app in containers/VMs or managing virtual/container network inventory? | Bounded Linux package deployment already recorded under 090. | Treat 024 as managed-network inventory; no double credit for packaging. |
| RFP-025 | Carrier-scale qualification scope and success workload? | No carrier-scale evidence in accepted ledger. | Write workload/measurement contract; no three-day carrier claim. |
| RFP-040 | Maturity assessment outcome and scoring authority? | No delivered assessment artifact identified. | Evidence-backed gap/ownership assessment; no invented score or benchmark. |
| RFP-044 | Which element-management interface and which read/write operations? | No adapter or operation proof identified. | One named read-only contract after platform/operation decision; unavailable interfaces remain blocked. |
| RFP-093 | Active-address population, traffic mix and acceptance measure? | Address-space arithmetic is not stored active-record scale. | Preserve requested population; smaller run only establishes its actual tested bound. |
| RFP-094 | Record mix, history depth, performance and growth target? | No million-record operational observations recorded. | Separate inventory/observations/history workload and measurement gates. |
| RFP-096 | Operate DNS/DHCP services or manage existing services through interfaces? | Existing app serves neither provider DNS nor DHCP. | Manage existing services; serving infrastructure is outside this bridge. |

These are eight rows, not the only eight decisions. 026/027/032/038/039/092/095 and
111 also contain clarification language or newly proposed boundaries. The interview must
cover them without treating every comment as a new implementation mandate.

## Source gaps and research facts

- A-SRC-01: Supplied temporary image paths were missing. Recovered retained embedded
  representations were directly inspected read-only; original temporary-file byte identity
  remains unverified. Exact reassignment, reservation/static-mode, prefix proposal/removal
  and LDAP/domain wording remain ambiguous. License alarm-without-shutdown is legible
  meeting intent, still subject to product policy decision. No source inspection blocker remains.
- A-SRC-02: No named EMS product/version/operation contract is supplied. Q063–Q064 resolve this as future read-only contract discovery; no implementation platform is invented.
- A-SRC-03: No live instance, credentials or operational authorization follows from a suggested
  ServiceNow account. Design can specify sandbox gates without connecting now.
- A-SRC-04: Q007/Q089–Q099 set relative days, 20% reserve and Spencer 2 hours/day plus at most 2 contingency hours as planning assumptions, not confirmed capacity.

## Contract conflicts to resolve before lock

| Conflict | Affected requirements | Resolution needed |
|---|---|---|
| Migration promotion versus immutable staged baseline | FR-002, FR-003 | Explicit cutover boundary, approved authority and rollback rule |
| Domain labels versus actual read/write enforcement | FR-005, FR-015 | Authentication boundary and authorization contract |
| Reservations versus non-reserving pending requests | FR-003 | Separate reservation actor, expiry, conflict and release semantics |
| Subscriber reassignment versus one fixed pool | FR-004 | Supported service/address change and source of truth |
| Event orchestration versus fixed local callback | FR-007, FR-011 | Bounded delivery semantics and failure reconciliation |
| HA/active-active versus current architecture | FR-016 | Defer or explicitly funded architecture qualification lane |
| DNS automation request versus explicit exclusion | FR-007, FR-010, FR-012 | Read/validate/export only; any future write must be separately specified |
| 92 label versus 39 accepted observations | FR-001 | Separate target ledger; lead-only evidence promotion |

## Agent resolutions

- 008: internal domain authorization, not customer tenancy (Q003/Q009–Q020).
- 024: managed-network inventory contract; packaging receives no duplicate credit (Q004).
- 025/093/094: future workload cohorts and qualification, no three-day scale claim (Q081–Q088).
- 040: evidence-backed gap/owner report without invented maturity score (Q005/Q079).
- 044: future read-only EMS inventory/status contract; no guessed product endpoint (Q064).
- 096: manage existing service interfaces, no DNS/DHCP server operation (Q006/Q059/Q065).
- Migration: assessment only; no promotion/cutover (Q021–Q032).
- Identity: token-backed principals plus default-deny egress; labels are insufficient (Q009–Q020).
- Lifecycle: explicit reservations distinct from pending requests; allocated release/reuse is Tier B behind history-preserving schema changes (Q033–Q046).
- Subscriber/ticket: synthetic service reference only, one durable ticket simulator, no real provisioning or inbound approvals (Q047–Q058).
- Events: closed local event set, manual attempts, stable correlation and unknown readback gates (Q066–Q070).
- DNS: existing IPAM context export only; no new parser/live read/write (Q065).
- Evidence: all 111 rows keep baseline and meeting labels separate (Q080).

## Gates

G0 source inspection completed, with retained-image byte identity limit.
G1 Spec v0 published before actual review.
G2 Q001–Q100 actual agent answers/challenges recorded.
G3 Q100 initially refused three wording conflicts, then confirmed the corrected candidate before lock.
G4 Agent-locked specification → real Spec Kit plan → tasks → consistency analysis.
G5 Independent document review for this package; later Fable advice and Main Lead adoption/acceptance remain explicit gates.
No gate authorizes application implementation or runtime tests.
