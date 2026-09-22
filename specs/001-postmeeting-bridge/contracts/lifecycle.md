# C-L: Narrow local reservation lifecycle

Q033–Q046/071–Q077; FR-003/006/008. Designated local static IPv4 pool only.

Authority reuses `workflow.STATIC_POOL_ID` = `8821c420-18ea-4caa-9d97-83a331c0c002`
and existing `workflow._pool`: the stored pool must retain family=4,
management_mode=static and allocation_authority=local, valid ranges and exclusions.
Its scope must additionally map to the selected permitted domain under C-A. No new
per-domain pool list or arbitrary local-static pool support is introduced. Missing,
changed-policy, foreign, IPv6 and non-designated pools fail visibly. T025 observes
non-designated-pool refusal as well as the supported path.

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

## T011 conversion identity clarification — 2026-09-22

The existing allocation request has owner and descriptive purpose. Purpose is not
an opaque service identifier and must not be silently substituted for one. When an
allocation request supplies reservation_id, also require service_reference and a
strict positive reservation_version. Persist these in the existing payload_json
and reservation_id column; no schema addition is needed. Reject the two companion
fields without a reservation_id. Requests without any reservation fields retain
their existing normalized payload and hash, including historical exact-key replay;
do not inject nullable defaults into that preexisting payload.

At both request creation and independent approval, authorize the selected domain
before disclosing pool or hold details. Require the exact reservation scope, pool,
IPv4 address, owner_reference=owner, service_reference and reservation_version;
the saved allocation request is the authority for approval, not replacement fields
in its decision body. The hold must still be state=reserved. An intervening extension
makes the old request stale and requires a renewed review. Expiry alone does not
free the hold. Existing purpose remains a descriptive field, retained unchanged.

All availability/eligible-claim checks, allocation insertion, conditional hold
conversion, converted_allocation_id linkage, history, audit and one pool/baseline
bump occur in the same immediate transaction. The partial unique reservation
index does not enforce cross-table allocation exclusion. Ordinary unreserved
allocation must refuse a reserved address; a matching reserved allocation may
consume only its explicitly identified current hold. T012/T015 expose these exact
fields. This decision follows the lead's source inspection and independent Sol
challenge; no application execution or T011 completion is implied.
