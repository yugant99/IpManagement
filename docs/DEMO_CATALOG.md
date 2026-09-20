# Evidence for the 15 demonstration scenarios

This catalog tracks the generic demonstration outcomes agreed in the private decision memo. It does not reproduce customer clauses. Its **15 scenarios**, the **16 historical Stage 5 acceptance cases**, and the **111 questionnaire rows** are different sets.

The historical catalog baseline was 12 observed scenarios, one bounded IPv6 scenario and two missing outcomes. The final connected rehearsal is recorded in the [sanitized handoff](handoffs/luna-final-rehearsal.md); the two provisional scenarios below are now observed within bounded local scope. The [lead review](handoffs/audit-response-lead-review.md) controls final integration. Historical observations resolve through [Stage 5 results](evidence/stage-05/observed-results.md); final owner checks resolve through the linked handoff.

| # | Scenario | Evidence and bounded outcome | Current disposition |
|---|---|---|---|
| 1 | Healthy pool | S5-05/06: North DHCP capacity 245, current/p95 150; healthy rule results with saved source evidence | Observed |
| 2 | Pool exhaustion | S5-05/06: independent Coastal pressure/forecast arithmetic; fixed p95/forecast rule branches and basis | Observed; thresholds are fixed |
| 3 | Oversized pool | S5-05/06: low occupancy across a complete window produces an investigation finding; missing samples are not zero-filled | Observed; no automatic shrink |
| 4 | Zombie candidate | S5-06: complete zero-lease window plus current intended announcement produces investigation-only evidence | Observed; no safe-reclaim or released-space claim |
| 5 | Ghost scope | S5-05/06 saved Central scope finding with concrete out-of-inventory DHCP observations; new F1 correction preserves the evidence | Observed; authorization is a separate question |
| 6 | Unregistered announcement | S5-05/06 saved Central managed-route discrepancy; routes outside the declared perimeter are not treated as its missing inventory | Observed; no automatic route withdrawal |
| 7 | Stranded block | S5-05/07: intended announcement absent under complete eligible routing; North cycle 4 anomaly, 5 unknown, 6 healthy | Observed; unknown cannot resolve absence |
| 8 | Duplicate assignment | S5-05/06: two concurrent incompatible DHCP claims in one namespace, both records retained; sequential renewals excluded | Observed for DHCP client conflicts |
| 9 | Valid private overlap | S5-05: identical private CIDR in North/Lab isolated scopes does not create a conflict solely from reuse | Observed; scopes are not tenant access security |
| 10 | Hierarchy control | S5-11: valid child create/resize, non-ancestral overlap refusal; F3 separately preserves structural history guards | Observed; safe supported hierarchy operations |
| 11 | Missing metadata | F2 [focused evidence](handoffs/audit-metadata.md) plus final rehearsal handoff: Lab metadata correction advanced the prefix version and saved reconciliation while prior runs remained retained | Observed in bounded local metadata/history flow; no customer metadata-quality assessment |
| 12 | Stale or failed source | S5-05/07: freshness/completeness gates and visible unavailable/unknown states, including North cycle 5 and Central cycle 7 | Observed; complete acquisition does not mean fresh evidence |
| 13 | IPv6 example | S5-11: IPv6 child-prefix preview, arithmetic and persisted selection without enumerating hosts | **Bounded**: DHCPv6 delegated-prefix record/occupancy outcome is not implemented or observed |
| 14 | Approval and rerun | F1 [focused evidence](handoffs/audit-corrections.md) plus final rehearsal handoff: independent `.240` and `.243` registrations, approvals, reconciliations and retained history; latest evidence remains separate from older results | Observed in bounded local correction/rerun flow; no external remediation or missing-route resolution claim |
| 15 | Allocation lifecycle | S5-12: exact candidate, independent decision, real local allocation and audit, explicit simulated downstream outcome; guards and safe retry | Observed for the fixed allocation flow; reservation/release/reclaim absent |

F3 metadata changes do not erase old saved runs, necessarily remove current occupancy, or necessarily make positive-lease zombie evidence unknown. Relevant structural changes conservatively invalidate unsupported history; metadata changes do not revive previously invalid history.

The additional S5-09/S5-15 observations are in [the audit-response evidence](evidence/audit-response/README.md). The original report remains **14 observed passes / two partial cases** at its original candidate. New addenda close the four requested missing observations without rewriting that historical result or asserting exhaustive shutdown/refusal coverage.

The [presenter guide](DEMO_STORY.md), [final procedural handoff](handoffs/luna-final-rehearsal.md), [questionnaire row map](QUESTIONNAIRE_ROW_MAP.md) and [customer phase gaps](PHASE_COVERAGE.md) must retain these boundaries. No 15/15, whole-questionnaire percentage, customer-phase completion or portable acceptance claim follows from a passing local story.
