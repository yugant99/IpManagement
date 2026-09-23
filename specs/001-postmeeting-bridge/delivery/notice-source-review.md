# T016 reservation notice source review

Author: GPT-6 Luna high, retained worker /root/t016_reservation_notices.
Independent reviewer: GPT-6 Sol high. Lead: Main Lead5.0 Astra.
Exact source: 1be8bbdf4a0ed11bc82c75da7a89f2deadaeaf74, PR85.
Integrated source: c5121d4d85c6972fe5ae39315a5a413a96a07599.

The full source review and correction review closed the scoped implementation.
Server UTC establishes the due alert and24-hour alarm; timestamps with missing
timezone fail visibly. One notice episode persists, alarm increments notification
version and old acknowledgement cannot acknowledge it. Current designated pool
policy/scope are revalidated before acknowledgement/replay. Foreign actor/reason
are redacted. Extension/conversion/approved release resolve notices atomically
without extra pool/baseline bumps; expiry never frees a hold. Current static
occupancy reports active allocations plus reserved holds, including expired holds,
with units, scope, pool, UTC and local provenance; saved DHCP runs are unchanged.

The response explicitly says operator_acknowledgement and owner_signoff=false.
FR006 owner/recipient permission and delivery lacks trusted mapping in schema6 and
remains OPEN, not waived by this bounded source acceptance. No claim of owner
receipt, portable/human evidence or external state follows.

No tests, imports, builds, lint, database or application runtime checks were run.
T025 remains prerequisite-gated and disposable-synthetic-only. Tier B is locked;
T028 remains the next main merge.
