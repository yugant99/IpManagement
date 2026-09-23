# Main Lead 4.0 Tier A capacity preflight

Prepared 2026-09-22 from the specification tasks, routing, roadmap, quickstart and operator contract. This is a read-only planning assessment; no application execution, test, provider call or implementation dispatch occurred.

## Current decision

**Execution update, 2026-09-22:** Route discovery is no longer on the immediate
critical path. OpenCode is paused; all further Claude/Fable/Opus use is stopped by
the user after the one completed advisory. Codex GPT-6 Luna implements and GPT-6
Sol independently reviews/escalates, with Astra lead. Access through T007 and
migration core T008 are source accepted; T009 API/T010 UI run on disjoint leases.
T011 is still dependency-held. The original model-hour estimates below are
planning history, not measured throughput or a revised completion promise.
Human T020/T022/T024/T026 remain unacknowledged, and their hours cannot be supplied
by model work. T025 runtime has not begun; Tier B remains held and reserve protected.

**Retain three days as a timebox, not a completion commitment.** The latest user clarification supplies approximately **8 total human hours for Spencer**, with review Wednesday night September 23 or Thursday September 24. Exact daily availability and review duration are not specified. A general VM target comes later and must not block immediate preparation; no VM provisioning is authorized.

Route recheck is in progress: the user identifies Terra through OpenCode, Fable through Claude Code CLI, and Sol through Codex. Earlier discovery found Go-listed Luna/Grok 4.7/Grok 4.6/DeepSeek but no Terra there. That earlier listing is not proof that Terra is absent from all configured routes. Inclusion/overage remains to be established by the lead; availability of a listed model does not establish additional-spend authorization. For any lane whose required route/authority remains unconfirmed, **0 dispatchable hours are counted until that lane is resolved**. This does not prevent lead adoption, documentation preparation or exact dispatch manifests under existing authorization.

## Units and confidence

- **M** means forecast active model wall-hours: time occupying that owner's execution lane, including its bounded source work and retained handoff. It is not a human labor estimate, billed token estimate or measured provider throughput.
- **H** means human working hours for Spencer. A simulated model turn cannot supply these hours or replace acknowledgement.
- Ranges are provisional planning judgments from the specified task surfaces and acceptance obligations. They are not observed durations. Calibrate them from the first authorized slices; do not infer a fixed AI-to-human productivity multiplier.
- Dependency elapsed time sums active task durations when they must run serially. Queueing, availability gaps, provider throttling, review/merge waits, target access, approval, human scheduling and unresolved defects add elapsed time.
- Task budgets include implementing/preparing the assigned deliverable; independent candidate validation remains T025. The 20% reserve is additional capacity for cross-lane review, integration and bounded fixes. It is not a new-feature allowance or a second copy of planned T025 effort.
- The fixed 2h budgets for T020/T022 are Spencer's requested bounded finishes, not proof that every unknown can be resolved within two hours. Unknown vendor/human facts must remain explicit.

## Per-task owner budgets

| Task | Deliverable | Owner | Unit | Low | High |
|---|---|---|---|---:|---:|
| T001 | Authority, adoption, base, ownership and capacity | Main Lead 4.0 / Astra | M | 1.00 | 2.00 |
| T002 | Source/field authority and missing-fact register | Grok 4.6 under Grok 4.7 | M | 0.50 | 1.50 |
| T003 | Tier A schema and recognized upgrade/fresh initialization | Terra | M | 1.50 | 3.00 |
| T004 | Trusted identity and fixed coordinator | Terra | M | 1.00 | 2.00 |
| T005 | All-egress guards and route/projection integration | Terra | M | 3.00 | 6.00 |
| T006 | Auth/domain propagation across all browser clients | DeepSeek UI under Terra | M | 1.50 | 3.00 |
| T007 | Independent source/design access review | Luna | M | 1.00 | 2.00 |
| T008 | Immutable migration comparison and normalized replay | DeepSeek backend under Terra | M | 1.50 | 3.00 |
| T009 | Migration assessment API and independent sign-off | Terra | M | 0.75 | 1.50 |
| T010 | Migration receipt/comparison UI | DeepSeek UI under Terra | M | 1.00 | 2.00 |
| T011 | Exact reservation/conversion/unused-release logic | DeepSeek backend under Terra | M | 2.00 | 4.00 |
| T012 | Reservation/release API and authority/version guards | Terra | M | 0.75 | 1.50 |
| T013 | Durable ticket intent, attempts, effects and readback | DeepSeek backend under Terra | M | 2.00 | 4.00 |
| T014 | Ticket API and independent local/ticket states | Terra | M | 0.75 | 1.50 |
| T015 | Reservation/decision/ticket UI | DeepSeek UI under Terra | M | 1.50 | 3.00 |
| T016 | UTC notice episodes, acknowledgement and occupancy | DeepSeek backend under Terra | M | 1.00 | 2.00 |
| T017 | Notice/evaluation/occupancy routes | Terra | M | 0.50 | 1.00 |
| T018 | Due-state UI and current-versus-saved metrics | DeepSeek UI under Terra | M | 1.00 | 2.00 |
| T019 | Evidence gaps, qualifications and business-owner register | Grok 4.6 under Grok 4.7 | M | 0.75 | 1.50 |
| T020 | Day 1 integration/status matrix | Spencer | H | 2.00 | 2.00 |
| T021 | Exact-candidate offline API documentation | Grok 4.7 | M | 1.00 | 2.00 |
| T022 | Day 2 recipient/migration validation pack | Spencer | H | 2.00 | 2.00 |
| T023 | State operations and recovery compatibility | Terra | M | 1.00 | 2.00 |
| T024 | Auth-aware operator wrappers/package/handoff | Spencer | H | 1.50 | 3.00 |
| T025 | Independent Tier A observations and recovery evidence | Luna | M | 2.00 | 4.00 |
| T026 | Guided human rehearsal and actual acknowledgement | Spencer | H | 0.50 | 1.00 |
| FABLE-DESIGN + T027 | Design advice and optional candidate advice | Fable, direct to lead | M | 0.50 | 1.50 |
| T028 | Lead adjudication and canonical evidence/status | Main Lead 4.0 / Astra | M | 0.50 | 1.00 |

The advisory allowance covers both potential reviews: 0.25–0.75h after specification/dispatch lock and 0.25–0.75h against the exact candidate after T025. The final review must depend on T025 (and thus T024); T028 depends on that final review. The user subsequently requested one completed Fable pass and user-run prompts for substantial further reviews. Record actual advice or the delivered prompt and lead adjudication; never invent a review or make Fable invocation an implementation dependency.

## Owner loads and required capacity

Capacity including reserve = planned task hours / 0.8. Human reserve is displayed separately: the roadmap explicitly protects core reserve. Spencer now has approximately eight total hours per the user, but exact daily slots remain to be scheduled.

| Owner/lane | Task load | Unit | Capacity with 20% reserve | Minimum average/day across 3 days, including reserve |
|---|---:|---|---:|---:|
| Main Lead 4.0 / Astra | 1.50–3.00 | M | 1.88–3.75 | 0.63–1.25 |
| Terra core | 9.25–18.50 | M | 11.56–23.13 | 3.85–7.71 |
| DeepSeek backend | 6.50–13.00 | M | 8.13–16.25 | 2.71–5.42 |
| DeepSeek UI | 5.00–10.00 | M | 6.25–12.50 | 2.08–4.17 |
| Grok 4.7 | 1.00–2.00 | M | 1.25–2.50 | 0.42–0.83 |
| Grok 4.6 | 1.25–3.00 | M | 1.56–3.75 | 0.52–1.25 |
| Luna | 3.00–6.00 | M | 3.75–7.50 | 1.25–2.50 |
| Fable, two advisory calls | 0.50–1.50 | M | 0.63–1.88 | 0.21–0.63 |
| Spencer | 6.00–8.00 | H | 7.50–10.00 if human reserve also protected | 2.50–3.33 |

Model task load totals **28–57 model wall-hours**, or **35–71.25 model wall-hours** including core/model reserve. Spencer adds **6–8 human hours**, not interchangeable with model time. The mixed-unit total is 34–65 task-hours only; do not label it human labor or elapsed schedule duration.

Grok's contract-sensitive code reviews, Terra's integration, Astra's coordination and Luna's author-feedback exchanges must be booked against their reserve. If those duties exceed reserve, reforecast; the apparent small Grok/Astra task totals are not free capacity to absorb another implementation lane.

These averages establish necessary owner capacity only. They do not establish sufficient schedule feasibility because shared files and dependencies serialize work. No more than three active subleads; Sol replaces a blocked leaf. Provider or platform concurrency below the requested topology adds queueing. One writer owns each shared-file lease.

## Critical paths

The user-specified **16-task serial chain** is:

T001 → T003 → T004 → T005 → T007 → T008 → T009 → T011 → T012 → T014 → T017 → T021 → T024 → T025 → T026 → T028

Its summed active duration is **19.25–38.50 hours**, before waits and reserve. Four of those steps alone do not make the branch executable: T014 also needs T013, T017 needs T016, T024 needs T022/T023, and T025 needs T018/T019 plus the operator pack.

Weighting the full 28-task dependency graph by the task estimates above produces a longer active path:

T001 → T003 → T004 → T005 → T007 → T008 → T009 → T011 → **T013** → T014 → **T015 → T022** → T024 → T025 → T026 → T028

That path is **22.50–43.00 active elapsed hours**. A simple one-task-at-a-time schedule for each named owner also reaches that range under continuous availability; it is a lower-bound scenario, not a live forecast. The terminal Fable pass after T025 can overlap T026 at the stated budgets. If human rehearsal is unavailable, Fable still gates the candidate review separately.

Adding a 20% scheduling allowance gives approximately **28–54 available elapsed hours**, before external waits. This allowance is a planning scenario and does not allocate a human or model working calendar. Three conventional 8h days contain 24h, with 19.2h available after reserving 20%; even this optimistic dependency schedule does not fit that envelope.

At eight operating hours per working day, **four to seven working days plus external waits** is a provisional reforecast scenario, not a promise. A three-calendar-day outcome could be possible with longer agent operating windows and precisely timed human slots, but neither availability nor throughput is established. Do not imply 24/7 model or human coverage.

## Spencer's day-by-day dependency problem

| Day | Authorized proposed finish | Work budget | What must already be ready |
|---|---|---:|---|
| 1 | T020 integration/status matrix | 2 H | T002 source/authority register; unknown fields may remain explicit |
| 2 | T022 recipient/migration pack | 2 H | T010/T015 usable comparison/change paths and T020; pending observed values cannot be called accepted |
| 3 | T024 operator package, then T026 rehearsal | 2–4 H total | T021/T022/T023 before T024; T025 must finish between T024 and T026 |

The Day 3 work is **two availability windows separated by independent validation**, not one guaranteed contiguous two-hour meeting. With the user's approximately eight-hour total, the lower estimate leaves two hours contingency; the upper estimate consumes all eight and leaves no human reserve. The original 2h/day distribution is still a proposal. Use the September 23 night/September 24 review availability to schedule a reviewable checkpoint; it is not evidence that the final candidate will be ready then. A wrapper/auth problem or unavailable recipient creates a real schedule extension; do not move core schema/auth ownership to Spencer to disguise it.

## Recommended checkpoint plan

1. Close the route/billing and owner-availability gates needed for each implementation lane; record unresolved lanes as unavailable for dispatch. Route existence alone is insufficient. Continue preparation before the VM is identified. Select/pin an authorized target before target-specific execution/evidence; do not provision a VM by inference.
2. On authorized dispatch, launch T003 and disjoint T002/FABLE-DESIGN work; do not fabricate a Terra substitution. Spencer T020 starts after T002. UI T006 starts after T004's frozen contract.
3. Treat completion of T003–T007 as the first calibration gate. Their sequential path consumes 6.5–13 model hours, or 7.5–15 including T001. T006 must also finish for T007. Compare observed active time, provider queueing, defects and staffed windows to the estimate before promising the remaining calendar.
4. Reforecast after the foundation gate using actual throughput and the next human slots. Preserve a candidate-freeze point before T024/T025. Review evidence only at its identified candidate.
5. Keep all Tier B off the schedule. To fit a fixed three-day timebox, deliver the largest fully reviewed Tier A increment and report the remaining bridge incomplete. US1 can be the first useful partial release; it does not satisfy Q099. Do not remove access/egress, exact ownership/version checks, independent approval, durable unknown/readback, history, recovery or independent evidence to rename partial work complete.

No Tier A scope cut preserves the full Tier A finish line. The honest choices are to extend the horizon, secure real additional compatible availability, or explicitly deliver a partial milestone while preserving the original acceptance contracts.

## Sources inspected

- specs/001-postmeeting-bridge/final-handoff.md
- specs/001-postmeeting-bridge/tasks.md and task-graph.csv
- specs/001-postmeeting-bridge/three-day-roadmap.md
- specs/001-postmeeting-bridge/agent-routing.md
- specs/001-postmeeting-bridge/plan.md
- specs/001-postmeeting-bridge/quickstart.md
- specs/001-postmeeting-bridge/contracts/operator.md
- Current user attachment and repository development/ownership rules

Worktree read: /Users/yuganthareshsoni/.codex/worktrees/18f4/Ip_inventory. Prepared independently; incorporated by Main Lead 4.0 into this delivery record.
