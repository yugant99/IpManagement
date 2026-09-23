# T002 — Source/field authority and missing vendor/business register

Task: **T002**. Owner: Grok 4.6 under Grok 4.7. Stage: Stage 1 (post-meeting bridge).
Leased path: this file only. Branch: `codex/bridge-t002-sources`.
Exact inspection base: `6b66f943b7c7783285bfd1f70859ede42380bf60` (T001 source-adopted contracts and resource-loaded gates). Specification candidate retained as `9df8393171af632b126a9801fe4cca73b1c575d1`; original application main `04eba98cb8673406d1e5d38c5318fb963cc77ff7`. Schema remains v5 at this base; schema 6 is planned (T003), not present.

**Mode:** documentary source review. No tests, builds, runtime, network, vendor research, credentials, or questionnaire-class changes. Historical runtime pointers below are **retained locators** from `docs/QUESTIONNAIRE_ROW_MAP.md` and lead handoffs; this task did not replay them. Future contracts (C-M/C-T/C-O interfaces, C-A route enforcement, schema 6) are **planned**. Fable design advisory is design-only and does not block this inventory.

**Contracts in scope:** C-M, C-T, C-O. **FR in scope:** FR-009, FR-010, FR-012, FR-014, FR-018, FR-020.

**Non-claims:** this register is not T019, T020, T021, runtime acceptance, human rehearsal, live integration, commercial commitment, or questionnaire re-adjudication. Meeting “Demonstrated” labels in S1 do not convert gaps into accepted evidence.

---

## 1. Distinctions that must not be collapsed

These four occupancy-like nouns and the intended/observed pair are independent authorities. Joins use `scope_id` + address family + address/prefix + applicable time interval (`docs/CONTRACTS.md` data boundary; `docs/IMPLEMENTATION_DECISIONS.md` Parts 1–2). A human domain/region label is not routing isolation.

| Noun | What it is in this repository | What it is not |
|---|---|---|
| **Allocated** | Intended local ledger row in `allocations` (`backend/ipam_demo/schema.sql` 55–69). Workflow authority is locked to `workflow.STATIC_POOL_ID` (`workflow.py` 19); `_pool` rejects every other ID (110–112), then requires that selected pool to remain IPv4, static and locally authoritative (119–120). There is no configurable designated-pool list. Pending `allocation_requests` do not reserve or allocate. | Not a DHCP lease, not a route, not traffic, not a CMTS/subscriber assignment, not a ticket. |
| **Leased** | Observed DHCP interval: `address`, `client_id`, `lease_start_at`, `lease_end_at`, `observed_at` under `source.authority=observed` and `required_for=["dhcp_history"]` (`imports.py` 143–145, 411–415). Current claim: `lease_start_at <= clock < lease_end_at`. Positive claims can block allocation; silence never proves availability (`evidence.py` `active_dhcp_claims`). | Not intended inventory. Not occupancy-as-traffic. DHCP-managed pool occupancy uses distinct assignable addresses; renewals do not inflate counts (`calculations.py` 73–74). |
| **Routed** | Observed routing interval: `cidr`, `router_id`, `valid_from_at`, `valid_until_at`, `observed_at` under `source.authority=observed` and `required_for=["routing_view"]` (`imports.py` 140–142). Compared with **intended** `route_policy` (`source.authority=intended_policy`, `required_for=["route_policy"]`). Match policy `exact` or `covering`. | Not traffic. Not BMP add/withdraw. Not CMTS RF/MAC state. Missing expected route requires a complete declared view (`IMPLEMENTATION_DECISIONS.md` zombie/routing rules). |
| **Traffic** | **No field, source, or metric exists.** Occupancy and route findings explicitly refuse traffic inference (`calculations.py` 73; `reconciliation.py` 56–57; FR-008/FR-013 non-claims). | Do not treat lease counts, route presence, Docker packaging, or utilization percentages as traffic. |
| **Intended** | Active seeded/edited inventory (`scopes`, `prefixes`, `pools`, `allocations`) plus intended route policy. Staged candidate inventory (`source_kind=inventory_staged`) is **not** active and does not declare coverage (`imports.py` `_stage_inventory`; `evidence.py` “staged data never active”; `source_catalog.py` staged `authority=not_applicable`). | Staging or C-M assessment is not promotion/cutover (C-M: no activate endpoint). |
| **Observed** | Imported `dhcp` and `routing` batches. Catalog `authority_status` is `declared` only (`source_catalog.py` 54; `app.py` `/api/source-catalog` limitations). Competing `source_id` families are refused by the synthetic feed adapter (`feed_adapter.py` 305–306). | Declared observed authority is not unique live-system authority and not discovery (`app.py` 498–499). |

Failure cases already encoded in source (not re-run here): unmapped `scope_id`; `SOURCE_KIND_CONFLICT`; `IMPORT_IDENTITY_CONFLICT` on same `(source_id, source_run_id)` with changed canonical JSON; multiple DHCP/policy sources per scope → unresolved authority; stale/incomplete coverage; whole-envelope intended refusal with no receipt or audit; and partial observation receipts through the existing importer, whose current route has no coordinator gate. Coordinator-only observation submission is planned in C-M/C-A.

---

## 2. Existing implementation field authority (source-grounded)

Inspected at base `6b66f94`. These are **existing** fields. Planned C-M/C-T/C-O records are listed later and must not be treated as implemented.

### 2.1 Intended inventory (active ledger)

| Field / object | Locator | Authority | Notes / failure |
|---|---|---|---|
| `scopes.id,name,namespace,domain,region,managed_cidrs` | `schema.sql` 13–20; `imports.py` 261, 285–296 | Intended isolation. `managed_cidrs` is independently declared perimeter; detection must not derive it from checked inventory (`IMPLEMENTATION_DECISIONS.md` 16). | Unmapped scope rejected. Namespace unique. Domain/region labels are not tenant isolation (RFP-008 remaining gap). |
| `prefixes.*` including `owner,purpose,tags,custom_fields,version,origin` | `schema.sql` 21–38; `imports.py` 262 | Intended prefix identity and string metadata. | String key/value only; no typed schema designer (RFP-027 remaining). |
| `pools.management_mode` `dhcp\|static` | `schema.sql` 46; `imports.py` 306–307 | Intended management class. Occupancy/forecast apply only to DHCP-managed IPv4 (`calculations.py` 76–80). | No current `management_mode` edit path was found. Planned T037 requires no static-pool relabeling; T034 separately freezes a provider fixture distinct from local-static authority. |
| `pools.allocation_authority` `local\|external` | `schema.sql` 47; `workflow.py` 19, 110–120 | `STATIC_POOL_ID` plus `_pool` 110–112 is the one-pool lock; 119–120 rechecks that selected pool's IPv4/static/local attributes. | No configurable designated-pool list exists. `seed.py` 94–95 validates local-authority attributes; it does not select the designated pool. External authority is declared, not a live DHCP/DNS/CMTS writer. |
| `allocations` unique `(scope_id,family,address)` | `schema.sql` 55–69 | Intended allocated address. | Cross-scope private reuse is legitimate (RFP-029). Same-scope overlap is conflict. |
| Seed/edit `origin` | `schema.sql` prefixes/pools/allocations `origin` | Provenance of the active row, not an observation batch. | |
| `app_meta.singleton=1` `baseline_version,demo_clock_at` | `schema.sql` 2–11; importer/catalog/workflow/reconciliation reads | Sole global baseline and evaluation-clock authority. | No per-scope baseline or clock list exists. Expected baseline is a planned C-M assessment field, not an implemented object. |

### 2.2 Source batches, coverage, records

| Field / object | Locator | Authority | Notes / failure |
|---|---|---|---|
| `source_batches.source_kind` | `schema_v3.sql` 8: `routing`, `route_policy`, `dhcp`, `inventory_staged` | Kind is immutable per `source_id`. | v2 CHECK omitted `dhcp`/`inventory_staged`; v3 extended it. Kind change → 409. |
| `(source_id, source_run_id)` + SHA256 canonical JSON | `imports.py` 242–250, 387–397; C-M planned reuse | Replay identity. | Same identity/hash returns original receipt; changed content 409. Raw-byte checksums are provenance only (C-M). |
| Envelope `source.{name,owner,authority,required_for}` | `imports.py` 407–415; `fixtures/SCHEMA.md` 47 | Declared sender metadata. | Must match kind table below or import is invalid. |
| `source_coverage` window + `declared_complete` / `effective_complete` | `schema_v2.sql` 15–22; `imports.py` `_coverage` | Sender completeness vs post-reject effective completeness. | Rejected required observations force effective completeness false. |
| `source_records.status` `accepted\|rejected\|duplicate` | `schema_v2.sql` 24–33 | Exclusive receipt classes; counts sum to input. | Existing observation imports may persist partial receipts (`imports.py` 444–520); `/api/imports` is not coordinator gated at this base. Coordinator-only submission is planned in C-M/C-A. Intended staging is all-or-nothing: invalid/duplicate input leaves no receipt or audit, while a new successful staging receipt writes `source.import` (`app.py` 460–477). |
| `ingested_at` vs `demo_clock_at` vs `observed_at` | batches + typed records | Wall-clock ingest vs evaluation clock vs observation time. | Future `observed_at`/start rejected; future lease/route end allowed. |
| Catalog `authority_status=declared` | `source_catalog.py` 44–64; `app.py` 491–499 | Receipt projection. | Explicitly not discovery or live uniqueness. Staged rows: `authority=not_applicable`. |

Required `source.authority` / `required_for` (existing importer, not vendor):

| `source_kind` (envelope / stored) | `source.authority` | `required_for` | Class |
|---|---|---|---|
| `routing` / `routing` | `observed` | `["routing_view"]` | Observed routed |
| `dhcp` / `dhcp` | `observed` | `["dhcp_history"]` | Observed leased |
| `inventory_policy` / `route_policy` | `intended_policy` | `["route_policy"]` | Intended policy |
| intended envelope with `scenario` / `inventory_staged` | not on envelope; catalog `not_applicable` | none | Intended candidate, not active |

Freshness used by eligibility (illustrative demo limits, not SLA): DHCP 1800s, routing 300s from coverage end vs demo clock (`evidence.py` 48–52).

### 2.3 Observed record fields

| Kind | Required fields | Locator | Join / limitation |
|---|---|---|---|
| DHCP | `id, source_record_id, scope_id, family, address, client_id, lease_start_at, lease_end_at, observed_at, original_timestamps` | `imports.py` 143–145, 167–178 | Conflict identity: scope+family+address with intersecting validity and incompatible `client_id`. Pool membership derived from ranges; no fixture pool label chooses the result (`fixtures/SCHEMA.md` 55). `client_id` is opaque, not subscriber identity. |
| Routing | `id, source_record_id, scope_id, family, cidr, router_id, valid_from_at, valid_until_at, observed_at, original_timestamps` | `imports.py` 140–142, 179–190 | Strict network CIDR (no host bits). Bounded intervals, not a parser. `router_id` opaque. |
| Route policy | `source_record_id, scope_id, prefix_id, expects_announcement, route_match_policy` | `imports.py` 146–163 | Intended. `expects_announcement: false` means no absence finding requested, not “route forbidden”. Snapshot coverage bounds equal demo clock. |

Synthetic feed pins eight observation files plus policy (`feed_adapter.py` 23–30). Scheduling refuses competing foreign `source_id` authority. This is local synthetic acquisition, not live discovery (`source-seams.md`; RFP-061 remaining).

### 2.4 Existing local API documentation surfaces (FR-009 existing, not new)

| Surface | Locator | Mode |
|---|---|---|
| FastAPI `/api/docs`, `/api/openapi.json` | `app.py` 72, 598; S10 in `source-reconciliation.md` | Existing source. C-A **plans** these to be authenticated; current base still uses fixed demo actors (`workflow.py` `DEMO_ACTORS`). Source inspection ≠ runtime observation. |
| Foundation/Stage 3/4 interface docs | `docs/FOUNDATION_API.md`, `docs/STAGE3_API.md`, `docs/STAGE4_API.md` | Existing documentary. |
| Import/catalog/run APIs | `app.py` `/api/imports*`, `/api/source-catalog` | Existing. Mixed-scope raw envelopes remain an access-treatment seam (`source-seams.md`). |
| C-M assessment routes | `contracts/migration.md` “Proposed interfaces” | **Planned** (T008/T009). Reuse `POST /api/imports` and receipts; no cutover. |
| C-T handoff routes | `contracts/ticketing.md` | **Planned** (T013/T014). `internal-ticket-simulator/v1` only. |
| Offline API pack | T021 `delivery/offline-api.md` | **Planned**. |

---

## 3. FR registers — existing vs gap (requirement, owner role, evidence gate)

Every gap row includes requirement ID, owner **role** (no invented person), and a future evidence gate. Existing bounded rows keep their S3 class; this document does not reclassify them.

Owner-role abbreviations: **Lead** = Main Lead 4.0; **Grok-int** = Grok 4.7 requirements/integration sublead; **Terra** = schema/API owner; **Spencer** = operator/package; **Human-biz** = human business owner, unassigned until Lead names an actual person (C-O Q092); **Human-int** = human integration/vendor-contract owner, likewise unassigned; **Luna** = independent verifier after explicit validation permission.

### FR-009 — API documentation and integration inventory

Disposition: A local API/offline pack and selected simulated contract; other entries documentary. Questionnaire: RFP-010, 012, 013, 039, 041, 046.

| ID | S3 class (retained) | Existing source locator | Gap | Owner role | Future evidence gate |
|---|---|---|---|---|---|
| RFP-010 | Demonstrated | S5 readiness/UI HTTP records; one process `python -m ipam_demo serve` (`CONTRACTS.md` runtime) | Single local service only; no HA/distributed claim | Terra (existing service); T019 for HA exclusion | Retain exact candidate serving `/healthz` and compiled UI. New HA claim needs FR-016 protocol + authorized failure observation. |
| RFP-012 | Demonstrated | `docs/STAGE3_API.md`; S5 HTTP resource reads/mutations | Local documented resource API; no external consumer or production security | Grok-int T021 offline pack; Terra T005/T009/T012/T014 for new routes | Versioned offline pack tied to delivery SHA (C-O Q094): auth, scope, errors, replay, simulation, non-claims. Examples labeled illustrative until Luna T025. |
| RFP-013 | Demonstrated | UI vs saved backend results (S5-04/06/12) | Observed supported product paths only | Terra + DeepSeek UI under T006/T010/T015 | Same-candidate UI/API agreement after C-A; no ecosystem claim. |
| RFP-039 | Documentary | `docs/SYNTHETIC_DATA.md` scenario map; `CONTRACTS.md`; this register; planned T020 matrix | No discovered organizational system inventory | Spencer T020 status-level matrix; Lead accepts | Matrix row per integration RFP: requirement, direction, product/version **or unverified**, authority, principal, payload/error/retry/readback, mode, owner, evidence, gap. No guessed endpoint (C-O Day 1). |
| RFP-041 | Missing | None | No CMDB adapter, table, or join key | Human-int (unassigned); Spencer records gap in T020; Grok-int does not invent mapping | Official product/version/interface + authorized sanitized sample + positive/negative/ambiguous join. Until then mode=`unverified` / unavailable. |
| RFP-046 | Missing (S3); meeting label is not evidence | None | No OSS/BSS adapter | Human-int (unassigned); Spencer T020 gap | Same as RFP-041. C-T: related CMDB/OSS/BSS remain matrix gaps. |

**FR-009 planned contract fields (not implemented):** C-M create/list/detail/signoff/export (`contracts/migration.md`); C-T handoff list/detail/attempt/readback/acknowledge (`contracts/ticketing.md`); C-O authenticated `/api/readiness` wrapper vs `/healthz` liveness. Selected simulated product: `internal-ticket-simulator/v1` only. ServiceNow object/table/API: **unverified, mapping pending** (C-T UI label). Timeout/retry already specified for the simulator (three attempts, 5s observation) and must not be copied onto an invented vendor SLA.

### FR-010 — CMTS/vCMTS and element-system boundaries

Disposition: C future read-only access-network/EMS contracts; no vendor adapter. Questionnaire: RFP-044, 045, 067. Q063: Cisco CMTS documentation is **first future research priority**; no product/version selected. Harmonic and Comcast are distinct named **targets**, not verified interfaces (`spec.md` FR-010; `questions.csv` Q063; C-O). **No endpoint, ACL, table, webhook, or vendor idempotency is recorded here.**

| ID | S3 class | Existing source locator | Gap | Owner role | Future evidence gate |
|---|---|---|---|---|---|
| RFP-044 EMS | Missing | Named intent only: S8/S7 sanitized notes; Q064 desired future read = interface/subnet inventory, status, observation time | No adapter, no official interface pack, no join keys | Human-int selects product/version; Grok-int documents after official source; Terra implements only after contract freeze | Official docs for **chosen** interface; sanitized mapping of vendor ID → `scope_id`/prefix/time; positive/negative/ambiguous match; read-only default. Unknown vendor/schema blocks correlation. |
| RFP-045 access-network | Missing | Same named targets (Cisco / Harmonic / Comcast) without version | No CMTS/vCMTS connection or matching evidence | Human-int; Cisco docs first **when research is authorized**; this T002 does not research | Named product **and** version, legally available contract/sample, stable keys. Configuration writes excluded (Q062). No operator/vendor equivalence. |
| RFP-067 cross-system | Missing | S5-03 available synthetic sources only; `PHASE_COVERAGE.md` §§4.5/7.3 | No DNS+DHCP+CMTS authority join | Human-int + Grok-int; T019 records exclusion | Independent authorities remain separate records until each join key is evidenced. One sample cannot complete DNS/DHCP/CMTS validation (FR-010 non-claim). |

Desired future EMS fields (planned documentary, not implemented): interface/subnet identity, operational status, observation time, coverage, for comparison with intended prefixes. Ambiguous join → unmapped, not guessed.

### FR-012 — DNS validation and export boundary

Disposition: A existing IPAM context export; C DNS parser/live/write. Questionnaire: RFP-055. S7/S8: DNS automation explicitly not recommended.

| ID | S3 class | Existing source locator | Gap | Owner role | Future evidence gate |
|---|---|---|---|---|---|
| RFP-055 | Missing | Inventory/report export of IPAM context (`reports.py`, Stage 3/4 API docs). No DNS record type, zone, or nameserver field in schema/importer. | No DNS parser, live query, write, or machine-validation | Terra preserves no-write; Spencer/Grok-int document export limitations in T020/T021; Human-int owns any later DNS product | Authorized negative evidence that write paths are absent; export shows source, time, limitations, recipient responsibility. Missing/stale DNS → unknown. RFP-055 remains a gap under this boundary (FR-012 non-claim). |

No DNS observation `source_kind` exists. Do not treat `custom_fields`, prefix `purpose`, or report CSV as DNS zones.

### FR-014 — Metadata, policy and maturity assessment

Disposition: A fixed registry/policy dictionary and documentary gap assessment; no customer maturity claim. Questionnaire: RFP-027, 028, 029, 030, 031, 032, 038, 040, 054, 084, 085.

| ID | S3 class | Existing source locator | Gap | Owner role | Future evidence gate |
|---|---|---|---|---|---|
| RFP-027 extra metadata | Demonstrated | Prefix `custom_fields` object\<string,string\> (`schema.sql` 32; S5-11) | No typed schema designer | Terra keep string map; T019 notes exclusion | New typed-metadata claim needs schema owner + denied invalid types. |
| RFP-028 classification | Demonstrated | `owner`, `purpose`, `tags` | Synthetic only | Data steward role unassigned for customer vocabulary | Customer vocabulary/approval identity if ever claimed. |
| RFP-029 overlap | Demonstrated | S5-05 scope reuse vs same-scope conflict | Not tenant security | Terra keep namespace semantics | Isolation claim requires FR-005 evidence, not this field. |
| RFP-030 hierarchy | Demonstrated | `parent_id` FK same scope/family | No arbitrary restructure | Terra | Unsafe resize already refused; new hierarchy language is out of scope. |
| RFP-031 common metadata | Demonstrated | `FOUNDATION_API.md` payloads; version/origin | Not organization-wide standard | Human-biz / data steward (unassigned) | Adopted standard document with owner, not app schema alone. |
| RFP-032 governance | Documentary | `ARCHITECTURE.md` §§3–6; `CONTRACTS.md` | No adopted customer governance or accountable customer owners | Human-biz (unassigned); Lead assigns; T019 documents | Named customer owners + operating history. Agents must not invent owners (C-O). |
| RFP-038 workflow docs | Documentary | `ARCHITECTURE.md` §6; `STAGE3_API.md` | Demo process ≠ current-state customer workflow | Human-biz current-state assessor (unassigned) | Evidence-backed as-is vs to-be with “not assessed” where missing (FR-014). |
| RFP-040 maturity | Missing | `PHASE_COVERAGE.md` §4.7; `docs/parts/02-sources.md` | No delivered assessment/template; “not assessed” is not a score | Human-biz assessor (unassigned); T019 may supply documentary template only | Reviewer-reviewed assessment linking each finding to supplied evidence; no invented benchmark (FR-014 non-claim). |
| RFP-054 assignment policy | Demonstrated | `workflow.py` eligibility; current DHCP claims; stale-review; no partial allocation | Fixed local pool policy; no policy language | Terra T011/T012 planned reservation still local-static | Configurable policy editor remains excluded. |
| RFP-084 change controls | Demonstrated | Actor/revision/approval/audit (S5-08/11/12) | No enterprise change-management integration | Human-int for ITSM; C-T simulator is not that integration | External change system needs official contract like C-T live gate. |
| RFP-085 validation policy | Demonstrated | Scope/range/overlap/conflict guards | No generic policy editor | Terra | Same as RFP-054. |

C-M adds **planned** comparison classes `added|changed|unchanged|conflicting` plus active-only (never deletion proposals). Changed owner conflicting with current approved assignment is conflict. Missing source rows do not establish available addresses. Sign-off does not promote inventory.

### FR-018 — Virtual/container network management boundary

Disposition: C managed-network inventory contract; no controller integration or new parser. Questionnaire: RFP-024.

| ID | S3 class | Existing source locator | Gap | Owner role | Future evidence gate |
|---|---|---|---|---|---|
| RFP-024 | Missing | Part 6 `Dockerfile`/`compose.yaml` package application **runtime**; `QUESTIONNAIRE_PRIORITIES.md` 73–74 packaging ≠ network management; Docker networking docs cited there as external reference only | No managed virtual/container-network objects, tenant/network IDs, or controller mapping. Image/Compose evidence belongs to RFP-090, not this row. | Human-int decides whether managed-network inventory is required and names source; T019 records exclusion; Spencer does not treat packaging as inventory | Selected outcome names managed objects and source/controller; one synthetic mapping labeled synthetic; unknown tenant/network identity blocks joins; mutations need an explicit controller operation. No Kubernetes/VM integration inferred from Docker (FR-018 non-claim). |

No `source_kind` or schema table for overlay/VPC/CNI identities exists at this base.

### FR-020 — Corporate, delivery and commercial evidence

Disposition: C/documentary business register and future expiry continuity policy; no commercial claims. Questionnaire: RFP-099, 100, 101, 102, 103, 105, 107, 108, 109, 110. C-O: no new licensing engine; future preserve-service expiry alarm is documentary intent only (S7a); no invented grace period or new-operation restriction.

| ID | S3 class | Existing source locator | Gap | Owner role | Future evidence gate |
|---|---|---|---|---|---|
| RFP-099 references | Missing | Priorities “provider-evidence gaps” only | No authentic provider references | Human-biz (unassigned) | Approved sanitized reference with exact scope/metric/population; synthetic demo cannot substitute. |
| RFP-100 telecom refs | Missing | Same | No authenticated industry customer references | Human-biz (unassigned) | Same; meeting Demonstrated label is not evidence. |
| RFP-101 very large ref | Missing | Same | No qualifying large-deployment reference | Human-biz (unassigned) | Exact population/unit match; CIDR size is not a reference. |
| RFP-102 method | Documentary | `PLAN.md`, `CHAT_STAGES.md`, `PROJECT_OVERSIGHT.md`, stage-05 lead review | Engineering method ≠ customer rollout execution | Lead (engineering method); Human-biz for customer rollout | Customer plan/execution acceptance separate. |
| RFP-103 staffing | Missing | `PROJECT_OVERSIGHT.md` contributor roles | Project agents ≠ dedicated provider team/capacity/commitment | Human-biz (unassigned); Lead must not invent named staff | Named people, capacity, ongoing commitment from authorized business owner. |
| RFP-105 roadmap | Documentary | PR #9 `docs/DELIVERY_METHOD.md` §5 `c3e45fa43a1e9f59e6c9af298b14e2c0857ebaa2` OPEN / NO MERGE | Unadopted proposal; no funded releases | Human-biz product owner (unassigned) | Product-owner adoption, staffing, release commitments. |
| RFP-107 local support | Missing | None | No provider support location/coverage/escalation operation | Human-biz (unassigned) | Provider-confirmed location, hours, escalation owners. |
| RFP-108 licensing | Missing | Dependency manifests are RFP-106, not a product license offer | No authorized commercial model or complete terms | Human-biz (unassigned) | Authorized license offer + applicable dependency terms. Expiry alarm remains unimplemented. |
| RFP-109 SLA | Missing | None | No support tiers/response/availability commitments | Human-biz (unassigned) | Provider-approved SLA text; Q081–Q088 numbers are qualification **assumptions**, not source replacements (T019). |
| RFP-110 compliance | Missing | App audit records exist for local mutations | Audit ≠ certification | Human-biz / compliance owner (unassigned) | Applicable control assessment/audit/certification under authorized custody; no customer detail in this repo. |

Private evidence, if later supplied, stays outside Git (`DEVELOPMENT_RULES.md` §6; FR-020). This task did not access `assessment/`, `audit/`, `outputs/`, or attachments.

---

## 4. Missing vendor/business fact register (closed list)

Facts **not** present in public repository source. Each stays unverified. Cisco is documentation priority only.

| Missing fact | Related requirement | Owner role | Evidence gate | Explicitly not to invent |
|---|---|---|---|---|
| ServiceNow product, instance, table, API, auth scopes, idempotency, rate limits | FR-009 / FR-004 / C-T | Human-int | Official instance contract after selection | Endpoints, table names, inbound approval trust |
| CMDB class/CI keys | RFP-041 | Human-int | Official mapping + sample | Join to `allocations` by guessed name |
| OSS/BSS product/version | RFP-046 | Human-int | Official contract | Parallel provisioning simulator as live |
| Cisco CMTS/vCMTS product/version/interface | RFP-044/045/067 | Human-int; **future docs priority** | Official Cisco documentation **after** authorized research | REST/SNMP/CLI paths, community strings, MAC/RF fields |
| Harmonic product/version/interface | RFP-045 | Human-int | Official Harmonic source | Interchangeability with Cisco |
| Comcast-named platform interface | RFP-045 | Human-int | Official source if legally available | Operator-specific endpoints |
| EMS inventory operation contract | Q064 / RFP-044 | Human-int | Read-only official op + observation time | Generic EMS adapter |
| DNS product, zones, TSIG, update API | RFP-055 | Human-int | None in Tier A; write forbidden | Parser or live query |
| Live DHCP vendor API | RFP-056 / FR-007 | Human-int; optional T034 is **synthetic fixture** | Isolated fixture contract distinct from local-static | Vendor reservation URL |
| Kubernetes/VM/CNI controller and network IDs | RFP-024 | Human-int | Named controller + object mapping | Docker image as managed network |
| Customer metadata vocabulary / maturity scores | RFP-028/031/040 | Human-biz | Assessed evidence or “not assessed” | Benchmark scores |
| Named human owners for commercial rows | FR-020 / C-O Q092 | Lead assigns actual people | Written assignment + artifact under custody | Agent-generated names/commitments |
| References, staffing, license terms, SLA, compliance certs, distribution rights | RFP-099–103, 107–110 | Human-biz | Approved authentic artifacts | Fabricated portfolios |
| License expiry commercial restrictions | S7a / C-O | Human-biz | Authorized business terms | Grace periods, new-operation locks |
| Recipient identity / human acknowledgement | FR-020/021; T026 | Human recipient + Spencer recorder | Actual ack fields on pinned candidate | Agent rehearsal as human handoff |
| Customer/source attachments | FR-001 | Lead custody | Stay out of public Git | Hashes already in `source-reconciliation.md` are identity only |

---

## 5. Planned contract objects (label: planned)

Do not treat as present in schema v5.

| Contract | Planned objects | Authority effect |
|---|---|---|
| C-M | `migration-assessments` with source batch ID, expected baseline, canonical hash, mapping/policy revisions, comparison classes, sign-off digest | Assessment is not intended promotion; abandon review changes no persisted state; restore is not undo. |
| C-T | ticket intent/attempt/simulator effect; correlation; route revision; mode=`simulated` | Local allocation independent of ticket. External ticket approval never authorizes IPAM mutation. Provisioning unsupported/not requested. Optional DHCP simulation uses a **separate** fixture (T034), not this ticket. |
| C-O | operator matrix, recipient pack, authenticated readiness wrapper, separate coordinator vs domain credentials | Wrappers must not log tokens. SQLite snapshot excludes code/UI/feed/config/tokens. Global Docker volume is not isolated by Compose project name. |

---

## 6. Failure cases and limitations (source)

| Case | Locator | Consequence |
|---|---|---|
| Missing/stale DHCP or routing | `evidence.py`, rules/reconciliation unknown paths | Unknown, not zero use / not safe reclaim |
| Multiple sources same kind+scope | `evidence.py` 71–72; `reconciliation.py` 61–62 | Authority unresolved |
| Competing feed `source_id` | `feed_adapter.py` 305–326 | Scheduling 409 `SYNTHETIC_FEED_INCOMPATIBLE` |
| Intended invalid/duplicate rows | `_stage_inventory`; `app.py` 460–477 | Whole envelope refused before persistence; no receipt or failure audit. Only a new successful staging import writes `source.import`. |
| Observation partial receipts | `imports.py` 444–520; `app.py` 460–477 | Existing importer can persist them and its route is not coordinator gated; they are not migration candidates. Coordinator-only submission is planned in C-M/C-A. |
| DHCP claim on static pool | `calculations.py` `static_dhcp_observations` | Policy discrepancy, not occupancy |
| Zombie candidate | `IMPLEMENTATION_DECISIONS.md` 47 | Investigation only; not reclaim |
| Catalog declared authority | `app.py` 498–499 | Not live uniqueness |
| Historical downstream_status | C-T | Compatibility only; old requests “not tracked” |
| Meeting vs accepted ledgers | `source-reconciliation.md` | Preserve S1/S2/S3 separately; S3 remains 39/18/10/44 |

---

## 7. Downstream use (not performed here)

- **T019** (`gaps-and-qualification.md`): may consume this register for HA/scale/encryption/virtual-network/EMS/DNS/IaC/business exclusions. Numeric cohorts stay assumptions.
- **T020** (`integration-matrix.md`): Day-1 matrix must copy unverified vendor cells as unverified; detailed contracts only for local API, C-M, and `internal-ticket-simulator/v1`.
- **T021** offline API: source-accurate examples; no secret/vendor invention.
- **T034** (Tier B, locked): synthetic DHCP fixture only after T025 and Lead selection.

---

## 8. Inspection method and non-claims

Read-only paths used: `AGENTS.md` required docs, `specs/001-postmeeting-bridge/{spec.md,data-model.md,contracts/migration.md,ticketing.md,operator.md,source-seams.md,source-reconciliation.md,coverage.csv,questions.csv}`, `backend/ipam_demo/{schema.sql,schema_v2.sql,schema_v3.sql,imports.py,evidence.py,source_catalog.py,calculations.py,reconciliation.py,workflow.py,feed_adapter.py,app.py,seed.py}`, `fixtures/SCHEMA.md`, `docs/{CONTRACTS.md,IMPLEMENTATION_DECISIONS.md,QUESTIONNAIRE_ROW_MAP.md,SYNTHETIC_DATA.md,parts/02-sources.md}`. Git: branch `codex/bridge-t002-sources` at `6b66f94`.

Not accessed: `assessment/`, `audit/`, `outputs/`, attachments, user configuration, other worktrees, network/vendor sites, credentials.

This document does not implement behavior, run software, assign named humans, select a Cisco product, or close questionnaire rows.
