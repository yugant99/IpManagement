# Ambiguity and decision register

Spec v0. Recommendations are proposals, not answers. User answers belong in questions.csv.
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
- A-SRC-02: No named EMS product/version/operation contract is supplied. The product boundary
  is a user decision; once chosen, research official documentation and actual available schema.
- A-SRC-03: No live instance, credentials or operational authorization follows from a suggested
  ServiceNow account. Design can specify sandbox gates without connecting now.
- A-SRC-04: Three-day elapsed schedule, staffing hours and tradeoffs require user decisions.
  Earlier 20-hour and Spencer 6–8-hour budgets are historical, not confirmed new capacity.

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

Resolve user-answer conflicts explicitly. Clarify within the same numbered decision until
answered consistently; do not invent an additional Q101 or silently average positions.
If further independent decisions are discovered, replace an unasked slot and retain the
change history. If 100 cannot close all branches, report that conflict before claiming lock.

## Gates

G0: Complete source inspection or explicit approved source omission.
G1: Publish Spec v0 before interview.
G2: Exactly 100 real user answers, no unanswered/conflicting decisions.
G3: User confirms shared understanding (Q100), required conflicts resolved.
G4: Locked specification → Spec Kit plan → tasks → consistency analysis.
G5: Fable advisory after lock, independent evidence review, Main Lead 3.0 acceptance.
No gate is an authorization to implement or execute tests.
