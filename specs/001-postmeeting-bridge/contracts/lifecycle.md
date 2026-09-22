# C-L: Narrow local reservation lifecycle

Q033–Q046/071–Q077; FR-003/006/008. Designated local static IPv4 pool only.

## Proposed interfaces
- GET/POST /api/reservations: scoped list/create exact pool/address/owner/service/reason,
  positive duration <=168 hours (24 default), reviewed pool/baseline versions and idempotency.
- POST /api/reservations/{id}/extend: exact current reservation version, duration/reason/key.
- POST /api/reservations/{id}/release-requests and /{id}/release-requests/{request_id}/decision:
  exact versions, reason, stable key; independent approver decides a local-only release.
- Existing allocation-requests optionally name reservation_id; approval converts only the
  matching address/owner/service hold and links its allocation, atomically.
- POST /api/reservations/evaluate: authorized bounded selected-domain UTC evaluation.
- POST /api/reservations/{id}/notice: exact notice version, permitted acknowledgement/reason.
All reads/actions use C-A; all versions and eligibility are rechecked inside the write boundary.

| State/event | Capacity | Success and refusal |
|---|---|---|
| Proposed allocation | No reservation | Existing request stays non-reserving |
| Create reservation | Consumes one current hold | Operator exact address, one active reservation, no active allocation/eligible claim |
| Extend | Still holds | Versioned audited expiry; cannot silently renew forever |
| Expired | Still holds | Alert at due, alarm due+24h; one notice episode, unknown evidence cannot free it |
| Approve allocation | Converted; allocation holds instead | One atomic transaction, same logical subject; no gap/double count |
| Propose release | Still holds | Pending proposal is not release |
| Approve unused local release | No longer holds | Different approver; no allocation/unresolved external effect; no irrelevant network evidence |
| Refuse release | Still holds | Nonempty reason, immutable decision; materially changed proposal supersedes |
| Allocated reclaim/reuse | Deferred Tier B | History-preserving schema/readers and full applicable authority/evidence required |

Database success state and audit commit together. Rollback preserves prior state; failed audit
persistence is visible using existing audited_write conventions. Same principal/key/payload
replays prior outcome; changed payload conflicts. Principal authorization still checked on replay.
Hold changes bump pool/baseline versions; evidence imports and unchanged retry do not. Do not
invalidate denominator history merely because occupancy changes.
Cross-table reservation/allocation eligibility must run inside the same immediate transaction;
a unique reservation index alone is insufficient. Concurrent second holder loses visibly.
No external DNS/DHCP writes or automatic local compensation.

Aging uses server UTC, not saved-run demo time. Historical synthetic dates may demonstrate
aging, clearly labeled. Acknowledgement does not clear condition. Extension, conversion or
approved local release ends that reservation episode while retaining history. Finding-backed
exceptions separately require comparable healthy evidence before closure.
Three distinct refused reclaim proposals within seven days raise one owner escalation in
the optional reclaim path; same-request retries never count multiple times.
Retention review is due 30 days after handoff, no automatic purge.

## Reporting compatibility
Current static occupancy = active allocations + state=reserved holds over assignable capacity,
with separate components and as-of time. Converted/released reservations excluded. Saved
DHCP evidence/runs remain immutable. Preserve current p95/forecast/720-sample semantics and
supported IPv6 prefix units; no invented delegation/host-occupancy metric.
