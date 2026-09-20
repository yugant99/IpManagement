# Evidence for the 15 demonstration scenarios

This catalog tracks the generic demonstration outcomes agreed in the private decision memo. It does not reproduce customer clauses. Its **15 scenarios**, the **16 historical Stage 5 acceptance cases**, and the **111 questionnaire rows** are different sets.

The historical catalog baseline was 12 observed scenarios, one bounded IPv6 scenario and two missing outcomes. New metadata and correction implementation is reviewed; **final connected rehearsal is pending**, so the two catalog upgrades below remain provisional. The [lead review](handoffs/audit-response-lead-review.md) controls acceptance. Historical observations resolve through [Stage 5 results](evidence/stage-05/observed-results.md); new owner checks resolve through the linked handoffs.

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
| 11 | Missing metadata | F2 [focused evidence](handoffs/audit-metadata.md): one explained Lab gap and healthy controls; audited metadata edit, new healthy result, immutable old run | Focused evidence accepted; final catalog closure pending rehearsal |
| 12 | Stale or failed source | S5-05/07: freshness/completeness gates and visible unavailable/unknown states, including North cycle 5 and Central cycle 7 | Observed; complete acquisition does not mean fresh evidence |
| 13 | IPv6 example | S5-11: IPv6 child-prefix preview, arithmetic and persisted selection without enumerating hosts | **Bounded**: DHCPv6 delegated-prefix record/occupancy outcome is not implemented or observed |
| 14 | Approval and rerun | F1 [focused evidence](handoffs/audit-corrections.md): independent concrete registration, persisted before/after/decision, actual reconciliation; latest unknown never falls back to old healthy evidence | Focused evidence accepted; final two-episode catalog closure pending rehearsal |
| 15 | Allocation lifecycle | S5-12: exact candidate, independent decision, real local allocation and audit, explicit simulated downstream outcome; guards and safe retry | Observed for the fixed allocation flow; reservation/release/reclaim absent |

F3 metadata changes do not erase old saved runs, necessarily remove current occupancy, or necessarily make positive-lease zombie evidence unknown. Relevant structural changes conservatively invalidate unsupported history; metadata changes do not revive previously invalid history.

The additional S5-09/S5-15 observations are in [the audit-response evidence](evidence/audit-response/README.md). The original report remains **14 observed passes / two partial cases** at its original candidate. New addenda close the four requested missing observations without rewriting that historical result or asserting exhaustive shutdown/refusal coverage.

The [presenter guide](DEMO_STORY.md), [native runbook](DEMO_RUNBOOK.md), [questionnaire row map](QUESTIONNAIRE_ROW_MAP.md) and [customer phase gaps](PHASE_COVERAGE.md) must retain these boundaries. No 15/15, whole-questionnaire percentage, customer-phase completion or portable acceptance claim follows from a passing local story.
