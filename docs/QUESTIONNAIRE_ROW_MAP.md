# Questionnaire row map

Planning only. No questionnaire requirement has yet been demonstrated or substantiated by this project. The application is unbuilt; existing provider capabilities are unknown without evidence. Each row has one primary category; a link or proposed document is not full satisfaction. Original workbook text and vendor answers are unchanged and excluded from this public repository.

Source locator: private questionnaire, Technical Requirements sheet, one-based row = RFP numeric ID + 2; requirement column B. Generic labels below paraphrase the engineering topic. Categories and priorities are analyst decisions.

**Priority:** B = original 53-row plan; P1 = 12 prioritized additions (65 total); P2 = two conditional additions (67 total); P3 = optional scheduling (68 total); Later = outside selected weekend evidence. P1/P2 figures include partial and documentary evidence. Existing full/partial capability claims must be judged against the remaining gap, not the priority.

**Categories:** Application = product/data/workflow; Deployment = architecture/deployment/resilience; Integration = external systems/identity; Scale = capacity/performance evidence; Delivery = process/business/provider evidence.

| ID | Topic | Primary category | Priority | Planned evidence / next needed work | Remaining gap |
|---|---|---|---|---|---|
| RFP-001 | Lifecycle | Application | B | Fixed request/approval/allocation and audit | Reclaim and broader lifecycle transitions absent |
| RFP-002 | Dual-stack records | Application | B | Scoped IPv4/IPv6 inventory and prefix arithmetic | No IPv6 subscriber allocator |
| RFP-003 | Subnet editing | Application | P1 | Validated child creation and safe empty-prefix edits | No destructive subtree resizing |
| RFP-004 | Permissions | Application | B | Server-enforced fixed demo roles and approval checks | No granular enterprise permissions or trusted login |
| RFP-005 | Activity audit | Application | B | Decision/import/edit events and export | Not every access/configuration event |
| RFP-006 | Search and reports | Application | B | Scoped search and one saved report preset | No arbitrary report designer |
| RFP-007 | Browser interface | Application | B | Working dashboard and evidence detail | Usability evidence still needs observation |
| RFP-008 | Tenant isolation | Deployment | Later | Future access-isolation design | Network scope is not tenant security |
| RFP-009 | Request portal | Application | B | One-pool IP request and review | Subnet request approval absent |
| RFP-010 | Central service | Deployment | B | One API owning shared intended/evidence state | No HA or distributed service claim |
| RFP-011 | DNS/DHCP management | Integration | Later | Future real adapters and management operations | DHCP replay is not integrated DNS/DHCP management |
| RFP-012 | API access | Application | B | Documented working HTTP resource endpoints | Implementation not started |
| RFP-013 | API-driven product | Application | B | Browser uses the same API and calculations | Implementation not started |
| RFP-014 | No single failure point | Deployment | Later | Future redundant application and database topology | Current single instance has failure points |
| RFP-015 | Active deployment modes | Deployment | Later | Future coordinated active/passive or active/active setup | No redundancy configuration or exercise |
| RFP-016 | Failover | Deployment | Later | Future automated detection and controlled promotion | No failover implementation |
| RFP-017 | Geographical recovery | Deployment | Later | Future off-site replica/backup and recovery design | No second site or recovery exercise |
| RFP-018 | Backup and restore | Deployment | B | Core SQLite backup API and validated restore; packaged instructions | No measured recovery objective |
| RFP-019 | Recovery point | Deployment | Later | Future measured backup/replication policy | No evidence of less-than-15-minute loss window |
| RFP-020 | Recovery time | Deployment | Later | Future timed recovery procedure | No evidence of less-than-60-minute restoration |
| RFP-021 | Encryption | Deployment | Later | Future TLS and encrypted-storage configuration evidence | Both transit and at-rest controls absent |
| RFP-022 | Health and alerts | Deployment | B | Readiness diagnostics plus in-app source/health failures | No production alert routing or monitoring service |
| RFP-023 | Hybrid environments | Deployment | Later | Portable app is a future-host design starting point | No hybrid-cloud integration or host evidence; outside target |
| RFP-024 | Virtual network support | Deployment | Later | Optional future scoped virtual-network/workload scenario | Docker packaging alone is not managed-network support |
| RFP-025 | Carrier scale | Scale | Later | Future workload-specific production design and measurements | No carrier-scale evidence |
| RFP-026 | Network domains | Application | P1 | Separate scoped inventories/sources with domain filters | No directory domains, tenancy or complete multi-domain orchestration |
| RFP-027 | Extra metadata | Application | P1 | Persist extra string key/value fields through the inventory form | No configurable typed schema designer |
| RFP-028 | Classification | Application | B | Persisted owner/purpose/tags with filters | Metadata accuracy is synthetic |
| RFP-029 | Private-space overlap | Application | B | Same private address in separately identified scopes | No tenant security inference |
| RFP-030 | Prefix hierarchy | Application | B | Validated parent/child inventory | No arbitrary hierarchy mutation |
| RFP-031 | Common metadata | Application | B | Explicit versioned inventory/source fields | No organization-wide standards rollout |
| RFP-032 | Governance | Delivery | B | Document authority/owners and local approval/audit controls | Illustrative framework; no adopted customer governance |
| RFP-033 | Normalization | Application | B | Strict CIDR/scope/time parsing with visible rejections | Limited formats and rules |
| RFP-034 | Duplicate inputs | Application | B | Separate duplicate/rejected/accepted receipts | Semantic assignment conflicts handled separately |
| RFP-035 | IPv6 planning | Application | P1 | Child-prefix capacity/preview and persisted child selection | No host enumeration or full IPv6 service planning |
| RFP-036 | Source discovery | Integration | B | Source catalog of known synthetic feeds | No automatic discovery of real systems |
| RFP-037 | Data quality | Application | B | Actual validation/duplication counts and export | No real customer-data assessment |
| RFP-038 | Workflow documentation | Delivery | B | Document the demonstrated process and fictional example | Existing customer workflows not observed |
| RFP-039 | Integration inventory | Delivery | B | Known-source dependency catalog and declared interfaces | Real organizational dependencies not discovered |
| RFP-040 | Maturity assessment | Delivery | B | Explicit assessment template with not-assessed/example sections | No completed customer maturity assessment |
| RFP-041 | CMDB | Integration | Later | Future mapped adapter and real read/write validation | No live CMDB connection |
| RFP-042 | Ticketing | Integration | Later | Future ticket API mapping and outcome evidence | In-app queue is not ServiceNow integration |
| RFP-043 | Event trigger | Application | P2 | Accepted observation import invokes actual reconciler with recorded result | Fixed local trigger; no general event platform |
| RFP-044 | Element systems | Integration | Later | Future equipment-management adapter | No element-system integration |
| RFP-045 | Access-network system | Integration | Later | Future CMTS adapter and matching semantics | No CMTS evidence |
| RFP-046 | OSS/BSS | Integration | Later | Future service/inventory adapter with authority rules | No live OSS/BSS integration |
| RFP-047 | Provisioning | Integration | Later | Future real provisioner calls and execution receipts | Local allocation and simulated outcome only |
| RFP-048 | Enterprise directory | Integration | Later | Future Entra/AD connector and configured identities | Demo actor switching is not directory integration |
| RFP-049 | Single sign-on | Integration | Later | Future configured identity-provider flow | No SAML/OAuth login |
| RFP-050 | LDAP | Integration | Later | Future directory authentication path | No LDAP integration |
| RFP-051 | Certificate API auth | Integration | Later | Future client certificate validation and identity mapping | No certificate-based API authentication |
| RFP-052 | Service credentials | Integration | Later | Future secret storage/rotation/access controls | No service credential management |
| RFP-053 | Allocation/reservation | Application | B | Real reviewed local allocation with retries | Distinct reservation lifecycle absent |
| RFP-054 | Assignment policy | Application | B | Enforce fixed pool ranges/exclusions/scope and current conflicts | No configurable policy language |
| RFP-055 | DNS changes | Integration | Later | Future live DNS write and outcome proof | No DNS update capability |
| RFP-056 | DHCP changes | Integration | Later | Future live DHCP write and outcome proof | No DHCP update capability |
| RFP-057 | Reclaim execution | Application | Later | Future approved local release then real-system integration | Candidates do not release addresses |
| RFP-058 | Infrastructure integration | Integration | Later | Future supported IaC module and state lifecycle | Compose packaging alone does not claim general IaC integration |
| RFP-059 | Lifecycle framework | Application | B | One fixed local approval flow | No configurable orchestration framework |
| RFP-060 | Approval flow | Application | B | Real server-controlled decisions and persisted audit | Fixed local demo actors only |
| RFP-061 | Continuous discovery | Integration | B | Manual synthetic replay and fresh/stale states | Neither timer nor replay discovers a network |
| RFP-062 | Validation | Application | B | Actual scoped prefix/address/time eligibility rules | Bounded data model |
| RFP-063 | Reconciliation | Application | B | Actual intended-vs-observed calculation over imported evidence | Source adapters remain synthetic |
| RFP-064 | Conflicting assignments | Application | B | Detect concurrent incompatible scoped assignments | No live mitigation |
| RFP-065 | Stale allocation | Application | B | Eligible 30-day candidate plus unknown/healthy controls | Investigation candidate; no proven safe reclaim |
| RFP-066 | Unassigned usage | Application | B | Observed-without-intended and policy discrepancies | Not a definitive unauthorized-use verdict |
| RFP-067 | Cross-system validation | Integration | Later | Future combined DNS/DHCP/CMTS adapters and authority joins | Current three sources do not include DNS/CMTS |
| RFP-068 | Run schedule | Application | P3 | Optional persisted timer calling existing runner with visible outcomes | No continuous discovery or worker fleet |
| RFP-069 | Reconciliation reports | Application | B | Saved actual findings and selected-run export | No scheduled report delivery unless implemented |
| RFP-070 | Remediation | Application | Later | Future approved correction/release and actual rerun | No automated external remediation |
| RFP-071 | Run history | Application | P1 | Compare immutable runs by scoped rule/subject | Unknown evidence cannot mark a finding resolved |
| RFP-072 | Discrepancy notice | Application | P1 | In-app notification of actual new findings | No external notification transport |
| RFP-073 | Utilization view | Application | B | Computed scoped lease occupancy/history | Lease occupancy is not traffic |
| RFP-074 | Forecasting | Application | B | Explained fit from complete synthetic daily history | Illustrative model and hourly sampling |
| RFP-075 | Candidate space | Application | B | Union addresses in candidate pools with explicit caveats | Not proven reclaimable/recovered space |
| RFP-076 | Operational metrics | Application | B | Metrics from the same saved run as details | Limited metric set |
| RFP-077 | Overview dashboard | Application | B | Readable computed overview with filters/drilldown | No separate executive reporting suite |
| RFP-078 | Audit reporting | Application | B | Actual decision/edit/import audit export | No compliance certification |
| RFP-079 | Ownership | Delivery | B | Owner fields and documented data/process responsibility map | Customer ownership not agreed |
| RFP-080 | Lifecycle process | Delivery | B | Document and execute the fixed local request/review path | No organization-wide adopted lifecycle |
| RFP-081 | Team handoff | Delivery | P2 | Conditional actual owner transfer/acknowledgement across two named demo teams | Fixed illustrative process; no external team integration |
| RFP-082 | Exception escalation | Application | P1 | Persisted exception owner/status/reason/history | No external paging or escalation service |
| RFP-083 | Review cadence | Delivery | P1 | Concrete review checklist, schedule, roles and retained evidence template | No executed operating history |
| RFP-084 | Change controls | Application | B | Role/version/approval/audit guards on supported mutations | No full enterprise change-management system |
| RFP-085 | Validation policy | Application | B | Enforced scope/range/conflict and mutation checks | No generic policy editor |
| RFP-086 | Improvement method | Delivery | P1 | Action backlog with owner, evidence, due date and review steps | Proposed method; no established improvement history |
| RFP-087 | Legacy migration | Application | B | Canonical import with rejection/provenance; optional one-format adapter | Arbitrary legacy migration not supported |
| RFP-088 | Domain migration plan | Delivery | P1 | Wave dependencies, entry/exit criteria, staging and rollback procedure | Baseline promotion/live migration not implemented |
| RFP-089 | Migration validation | Application | B | Actual schema/identity/duplicate checks and receipts | No real migration reconciliation/sign-off |
| RFP-090 | App deployment | Deployment | B | Portable one-service build/run and persistent state | Declared host must actually be exercised |
| RFP-091 | Orchestration deployment | Deployment | B | Package the fixed local workflow with the app | No separate production orchestration platform |
| RFP-092 | Training material | Delivery | B | Operator/admin walkthrough using the actual app | Material only; no delivered training program |
| RFP-093 | Very large active inventory | Scale | Later | Future 50M-active-address workload, storage and scale evidence | Address-space arithmetic is not active records |
| RFP-094 | Millions of records | Scale | Later | Future volume ingestion/query measurements | Small fixtures give no scale proof |
| RFP-095 | Regional hierarchy | Application | P1 | Persist an intended child prefix under a region parent | No provider geographic allocation policy or live rollout |
| RFP-096 | Provider DNS/DHCP | Scale | Later | Future service architecture, integrations and load evidence | IP inventory does not run provider DNS/DHCP |
| RFP-097 | Large-team concurrency | Scale | Later | Future concurrent workload and authorization evaluation | Single-worker demo is not large-team evidence |
| RFP-098 | Subscriber allocation | Integration | Later | Future subscriber/service integration with actual assignment outcomes | Fixed local request is not subscriber provisioning |
| RFP-099 | Reference portfolio | Delivery | Later | Provider must supply authentic qualifying references | Cannot be generated as product evidence |
| RFP-100 | Telecom references | Delivery | Later | Provider must supply authentic industry references | No references established by this demo |
| RFP-101 | Very large reference | Delivery | Later | Provider must substantiate a qualifying deployed reference | Synthetic data cannot establish a reference |
| RFP-102 | Implementation method | Delivery | B | Concrete build/integration/handoff stages and evidence gates | No completed customer rollout claim |
| RFP-103 | Delivery staffing | Delivery | Later | Provider must confirm dedicated people/capacity/ownership | Weekend contributors do not establish an ongoing team |
| RFP-104 | Knowledge transfer | Delivery | B | Runnable handoff, walkthrough and pickup exercises | No completed transfer program or recipient acceptance |
| RFP-105 | Product roadmap | Delivery | P1 | Proposed 24-month phases, dependencies and assumptions | Draft only; no vendor-approved delivery commitment |
| RFP-106 | Dependency disclosure | Delivery | B | Actual package/license inventory after dependencies are pinned | No speculative completeness before implementation |
| RFP-107 | Local support | Delivery | Later | Provider must confirm support location/coverage/escalation owners | A generic runbook does not establish staffed local support |
| RFP-108 | Licensing offer | Delivery | Later | Provider must specify product and dependency terms | No authority to invent commercial terms |
| RFP-109 | Service commitments | Delivery | Later | Provider must approve measurable support levels and SLAs | No availability/support promise from a demo |
| RFP-110 | Compliance evidence | Delivery | Later | Provider must supply applicable controls/audits/certifications | Audit CSV is not GDPR/SOC2/ISO certification |
| RFP-111 | Configurable lifecycle | Application | Later | Future administrator-defined states/transitions and enforcement | Fixed state machine does not satisfy configurability |

Counts from this mapping: B = 53; P1 = 12; P2 = 2; P3 = 1; Later = 43.

For priority, effort and source-to-claim rules, read [QUESTIONNAIRE_PRIORITIES.md](QUESTIONNAIRE_PRIORITIES.md). Evidence pointers should be added only after actual implementation or document delivery; no row is marked complete by this plan.
