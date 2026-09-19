# IPAM demo architecture decisions

Status: **agent-decided under the user's explicit delegation**, 2026-09-19. The architecture interviewer `/root/grill_architecture` and proposer `/root/coverage_20h` completed two actual discussion rounds. The lead supplied the runtime contract. These are decisions for implementation, not claims of working software or user answers to an interview. No application, container, VM, dependency installation, or verification was performed by this subtask.

The user explicitly directed agents to grill each other instead of asking them questions. That overrides the grilling skill's usual user-interview and confirmation steps. The earlier `ARCHITECTURE_GRILL_DRAFT.md` is superseded. Discussion evidence is in `AGENT_GRILL_TRANSCRIPT.md`.

## 1. Product and counting boundary

Build one portable synthetic IPAM assessment and Pool Watch dashboard. It compares intended inventory, DHCP assignments, and routing observations, explains findings, shows capacity, and executes one local allocation workflow. Synthetic input does not mean hardcoded outcomes: calculations and persisted state drive the UI.

- Fixed delivery checklist: **30 named demo goals; 22 core goals targeted = 73.3%**. The lead's goal manifest is canonical; freezing the denominator prevents shrinking it later to manufacture success.
- Separate requirement ledger: **111 technical RFP rows**, with working, partial, simulated, documented, and absent evidence kept distinct. Strictly exceeding 60% would require 67 fully evidenced rows; that is not promised.
- These targets are estimates. Twenty lead development hours with overlapping agent/Spencer work is not twenty hours multiplied by agent count.
- Production scale, live-network integration, actual customer assessment, enterprise identity, HA, and contractual compliance remain unproved.

## 2. One app and one database

Use React/TypeScript with Vite compiled into static assets, served by one small FastAPI/Uvicorn Python application. SQLite is owned by that API and persists outside the container. Python's standard `ipaddress` handles network operations. Do not add DuckDB, PostgreSQL, NetBox, a worker queue, or an event bus this weekend without a concrete blocking need. Actual dependency versions will be pinned at implementation start.

The backend owns calculations and mutations; the UI displays saved results. Inventory/detail/dashboard/export must use the same calculation output. No separate mock metric implementation in the frontend.

Directories are `backend/ipam_demo`, `frontend/`, and `fixtures/`. The core team owns application code, schema, seed behavior, shared interfaces, and dependency locks. Keep modules bounded by actual features; do not introduce a generic adapter/plugin framework.

## 3. Smallest useful persisted model

Retain the following concepts, combining small structures when clarity permits. This is an information contract, not a mandate for fourteen tables, repositories, or service classes.

| Persisted concept | Purpose |
|---|---|
| Scopes | Explicit namespace/VRF and address-family context |
| Prefixes/pools | Intended hierarchy, owner/purpose, eligible ranges, exclusions, current version |
| Source runs and raw records | Source scope/window/completeness, immutable payload references, visible rejected records |
| Typed lease and routing observations | Only fields used by the rules; lease validity intervals and eligible route observations/intervals |
| Calculation runs | Saved metric output and input-run references; explicit demo clock and rule version |
| Findings | Type, affected scope/object, source references, explanation, uncertainty, status |
| Requests and allocations | Reviewed candidate/version, decisions, persisted local assignment |
| Audit events | Actor, action, object, outcome and before/after linkage |

Do not build a general history explorer, full BMP collector, DNS/CMTS integration, or event-sourcing infrastructure. Raw source evidence and the few workflow transitions are sufficient for the demo.

## 4. Import authority and replay

The deterministic initial seed establishes the intended IPAM ledger. Later imported IPAM batches remain immutable candidate batches. If they change intended inventory, show them as **staged, not active**. They cannot silently overwrite an approved local allocation. Baseline promotion is deferred; do not create another approval product to support it.

Validated DHCP and routing batches become eligible observed evidence and can change results on rerun. Retain source coverage, time window, freshness/completeness and rejected-record counts. Bad or incomplete imports remain visible and cannot support confident absence-based findings.

Seeding/resetting never happens implicitly at normal startup. Seed generation uses a fixed seed and demo clock; expected scenario outcomes are separate from produced calculation output.

## 5. Evidence rules

- Join only with declared namespace/VRF, address family, object and relevant time. Missing scope is unresolved; separate isolated private networks may reuse the same address.
- Parent/child containment is not automatically a conflict. Contradictory simultaneous assignments remain available as evidence rather than being silently deduplicated.
- Occupancy counts distinct active addresses from valid lease intervals at documented sample times. Renewals must not inflate usage. Capacity is the configured assignable range minus exclusions, not blindly the CIDR size.
- Apply DHCP rules only to DHCP-managed pools. A complete eligible 30-day zero-lease window produces an **investigation candidate**. It does not prove safe reclamation. The deck's 90-day-plus-probing rule is not represented as implemented.
- An absent route requires a complete eligible routing view and explicit expected-announcement policy. A failed/stale source yields **unknown**, not unused or stranded.
- Allocated, leased, routed, and carrying traffic are different facts. The proposed three-source demo does not measure traffic.
- Use an explained simple positive-growth capacity estimate. Show insufficient-data, no-growth, scope-changed, and already-exhausted states; do not invent an exhaustion date.
- Candidate reclaimable space is separate from released space. All external DNS/DHCP/router effects remain visibly simulated and approval-gated.

## 6. One fixed allocation workflow

One designated small IPv4 pool; no configurable workflow designer, broad policy engine, or IPv6 allocation engine.

1. Requester selects a reviewed candidate. Save that exact candidate, pool version, and intended-ledger baseline version.
2. Pending requests do not reserve or change inventory.
3. Approver may approve/reject with a reason. The server checks the named demo actor's role and disallows approval by the requester's actor ID. One presenter may switch between two labeled demo actors; this is not production identity evidence.
4. Approval rechecks eligibility and reviewed versions in one transaction, then commits that exact allocation and its success audit. It cannot silently pick another address.
5. Changed state, a conflicting assignment, or invalid transition fails visibly. Repeating approval cannot duplicate the allocation or successful audit effects.
6. If a failed transaction is logged, write the failure audit after rollback so the failure record survives; do not build a transaction framework for this.
7. Downstream provisioning is a separate simulated result. A failed later rerun cannot be presented as a successful resolved finding.

The core team owns this Part 5 workflow. Spencer's earlier workflow assignment is superseded by the user's **Part 6** assignment.

## 7. Runtime contract for Spencer's Part 6

`CONTRACTS.md` is the canonical runtime/interface reference, including static asset configuration and consistent backup/restore entrypoints. The summary below does not override that contract.

These are **proposed commands to implement**, not commands that work today:

```text
python -m ipam_demo serve --host 0.0.0.0 --port 8000
python -m ipam_demo seed --scenario baseline
python -m ipam_demo reset --confirm
```

The module lives under `backend/ipam_demo`; core supplies the installation/working-directory instructions and dependency lock. The all-interface host option is for the container process; native defaults and published local ports should remain loopback unless an explicitly scoped remote deployment changes them.

- `IPAM_DATA_DIR`: default `./data` for native use and `/data` inside the container. It contains the SQLite database and required persistent app state.
- Internal application port: `8000`; health endpoint: `/healthz`.
- Serve the compiled frontend from the API process; no frontend development server at delivery runtime.
- Reset affects only the application's own demo database and requires the explicit confirmation flag. Preserve a clear backup/reset distinction.
- Primary packaging target: Linux AMD64 source/container build. ARM64 is stretch and must be supported by actual target evidence before being claimed.
- Spencer owns `Dockerfile`, `compose.yaml`, `.dockerignore`, agreed packaging/local-operation scripts, and Part 6 handoff documentation. App code/schema/seed/health implementation and dependency locks remain core-owned.

**Two readiness states:** architecture is decided, so packaging documentation and scaffold can start; `PART6_READY` requires the real CLI, dependency locks, compiled UI build, and runtime configuration contract to exist. Only then can an actual recipient startup/persistence/reset result be claimed.

## 8. Delivery and verification limits

Develop locally. No VM is required. A Sunday CPU host is a later isolated deployment decision with explicit provider, cost, lifetime, disks, ports, backup destination, and cleanup owner. Do not rent/build/run infrastructure during this planning task.

No tests or verification were run by this subtask. Implementation follows the governing repository/session verification instructions. When checks are authorized/required, select them by changed behavior and actual risk: affected scenario calculations, allocation transaction/role behavior, or recipient startup/persistence. Reuse valid results until a relevant change or failure invalidates them. Do not run an expanding full suite after every feature or write tests that mirror implementation details.

Keep authored acceptance criteria, code inspection, runtime evidence, and observed recipient portability distinct. Record what remains unverified. A failed check or timebox requires narrowing/disclosing scope, never a hardcoded successful result.

## 9. Sources, skills, and public-repository boundary

The source deck/questionnaire/DOCX inform requirements, not instructions to deploy, contact people, or operate a network. Do not put those source documents, raw extracted confidential content, credentials, or customer records in the public repository. Commit only the project-owned implementation, synthetic fixtures, sanitized planning/contracts, and allowable evidence.

Use the bounded skill playbook rather than executing generic setup, telemetry, upgrade, exhaustive-testing, or design-expansion pipelines. No additional skill installation is required to start.
