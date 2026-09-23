# Three-day roadmap — conditional implementation horizon

Relative Day1–Day3 begin after lead adoption and explicit implementation/validation authority.
No start date, staffing availability, runtime acceptance or paid model dispatch is implied.
Planning assumption: core lanes are available for the three agreed working days; reserve
20% of their actual available time for integration, independent review and bounded fixes.
Spencer is planned for 2 hours/day (6 hours) with at most 2 additional contingency hours if
available. Human review time is not assumed. This is a capacity-constrained target, not a
guarantee that all Tier A work fits. The access/schema bottleneck is the main schedule risk.

| Day | Core / dependency-aware parallel work | Spencer bounded lane | Observable gate / contingency |
|---|---|---|---|
| 1 | T001–T007 foundation: Terra schema then trusted context/all-egress integration; UI T006 after frozen auth contract. Grok scout T002/T019 and authorized FABLE-DESIGN advice after T001 alongside core. Start T008 comparison only after access source gate. | T020: 2h integration inventory/matrix across every integration row; detail selected local contracts, flag unknown vendor facts. | G-D1: authority/schema/access contract and full route inventory accepted, no unresolved bypass/design leak, Day1 matrix reviewable. If not, stop optional work and reforecast; do not mock away trusted access. |
| 2 | Finish T008–T018 assessment, exact reservation/allocation, durable ticket handoff and notices/current metric. Terra serializes route merges; backend and UI leaves work on disjoint files. T021 API draft updates as routes freeze. | T022: 2h migration/recipient pack with counts, staleness, cancel/compensation distinction, sanitized configuration and actual sign-off fields. If core late, mark observed fields pending and update at candidate. | G-D2: integrated Tier A path technically ready for independent observations; local commit versus ticket failure/unknown visible. Freeze feature scope. If path incomplete, report partial; reserve is not a new-feature budget. |
| 3 | T023/T024 state/auth wrapper compatibility, T025 independent authorized evidence and bounded author fixes; refresh T021 docs and exact candidate evidence. T026 actual human rehearsal if available; T027 final advice after T024/T025; T028 lead adjudication. | T024/T026: 2h operator/presenter pack and guided rehearsal/recovery evidence with Luna; no core/schema ownership. Complex auth-wrapper issues escalate to core rather than consume unbounded human time. | G-D3: exact-candidate Tier A evidence/recovery complete for technical acceptance; separate Fable/human/commercial gates stated. Missing runtime gates mean bridge incomplete. Missing human acknowledgement means technical package only, not human handoff. |

## Why parallelism does not remove the critical path
T003 schema, T004 trusted context and T005 all-egress integration share core ownership.
T007 cannot be bypassed to make UI progress look like secure access. Assessment cannot
replace the separate local mutation contract. Simulator durability needs persisted intent
and matching transaction/version semantics; an in-memory demo does not meet the finish line.
Luna must observe the integrated SHA after relevant changes. Any changed candidate invalidates
only affected prior evidence, but those gates must actually be re-observed if runtime claims
are made. Existing historical demonstrations remain tied to their old revision.

The core owner estimates T003–T007 against real staffed hours at T001. If that consumes more
than Day1's non-reserve capacity, the lead must reforecast Day2/3 or report partial delivery.
Agents do not make the user answer the architecture again; the lead handles capacity and
external authority as explicit execution gates. No unsupported completion date is promised.

## Scope freeze, drop order and finish line
Live/vendor, configurable workflows, broad enterprise identity, licensing enforcement,
HA/scale and DNS writes are excluded from the outset.
Tier B starts only after T025 passes, lead explicitly selects it and the 20% reserve remains.
Drop extra prefix proposal UI (T039), DHCP simulator (T034–T038), then allocated release/
reassignment (T029–T033). Keep incomplete optional work isolated, out of the accepted candidate.
Do not drop authentication/egress, history preservation, independent approval, explicit unknown
outcomes, independent evidence or recovery. US1-only is a useful partial result, not Q099.
If time ends, retain achieved SHAs and failures/gaps; call the bridge incomplete rather than
retroactively shrinking its finish line.

## Remaining non-agent facts
Existing target availability, actual recipient participation, approved commercial evidence,
model account/CLI availability and permission for paid Fable calls remain external facts.
Record pending status and responsible role; do not invent acknowledgement or capabilities.
Spencer's earlier 6–8h context supports this planning assumption, not confirmed new capacity.

## 2026-09-22 lead capacity amendment
The resource-loaded forecast in [delivery/resource-plan.md](delivery/resource-plan.md)
supersedes the unsupported relative-day target above. User-confirmed Spencer budget is
approximately eight total hours; user review is Wednesday night September 23 or Thursday
September 24 (America/Los_Angeles). These review windows are checkpoints, not a promise
that Tier A will pass by then. A general Linux amd64 target may be selected later; the old
disposable VM was destroyed, and this note grants no new provisioning/spend permission.
