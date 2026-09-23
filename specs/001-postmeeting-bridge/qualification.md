# Future qualification protocol — not measured

Q081–Q088 are architecture-agent planning assumptions, not customer-approved SLAs or a
substitute for exact RFP clauses. No workload, benchmark, failover or recovery was run here.

| Dimension | Future assumed protocol | Evidence boundary |
|---|---|---|
| HA | Process loss, host loss, partition, rejoin; writer fencing; zero conflicting successful allocations | No HA implementation in Tier A; one process/local store retained |
| Recovery | Incident-unavailable to UI/API ready plus business-state read; 15-minute planning goal, backup age <=24h, zero loss versus chosen snapshot | Include diagnosis/retrieval/restore/migration/startup/validation; enumerate acknowledged post-snapshot loss; source SLA if stricter controls |
| Host loss | Same protocol including replacement provisioning and artifact transfer | Separate from prepared-host restore |
| Encryption | Transport certificate validation; at-rest DB/snapshots/exports/sensitive logs and key recovery | No added TLS or app-at-rest encryption; bridge loopback only |
| Load | 80% reads, 15% import/status, 5% changes; 100 accepted observations/sec sustained | Approved mutation submix separate; bounded <=10k-record batches |
| Active IPv4 | First cohort 1M individually stored current intended assignments keyed scope/family/address | No CIDR capacity, reservations, candidates, history or duplicates; original higher population still required for row credit |
| Record mix | 1M current assignments +3M lease observations/30days +500k historical changes +500k audit =5M logical records,100scopes | Raw storage copies/indexes/findings reported separately; current importer/history model not qualified |
| Concurrency | 100 distinct principals, one outstanding interactive request each,2s think,10min warm-up+60min measured | Actor switching is not independent principals |
| Latency | Reads p95<=1s/p99<=3s; decisions p95<=2s/p99<=5s; import acceptance/status p95<=5s | Include expected conflicts/denials separately; not hidden in aggregate |
| Correctness | Unexpected failures/timeouts <=0.1%; zero silent partial writes, leakage or duplicate/conflicting successful allocations | Report every refusal, unknown and interrupted measurement |

Dataset manifest fields: exact source/package SHA, schema/config versions, generator version,
seed and declared synthetic status, scope/family distribution, individually stored active
counts, observation intervals/completeness, record classes, history depth, storage duplication,
hardware/limits, operation mix, principal count, offered/completed throughput, durations,
percentile method, error categories and retained raw results. No populated manifest is claimed.

Luna independently interprets future results; Terra owns architecture gaps; Main Lead owns
canonical row credit. Corporate/customer reference requirements need actual approved private
evidence from their business owner. Smaller observed runs prove only their exact bound.
