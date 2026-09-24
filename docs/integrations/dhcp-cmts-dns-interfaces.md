# Generic cable/broadband operator interface memo (read-only, synthetic-first)

**Real-data gate (read first):** `backend/ipam_demo/imports.py:378-381`
requires every observation envelope to declare `fixture_contract:
ipam-synthetic-v1` **and** `synthetic: true`, with `demo_clock_at` equal to the
seeded clock. A real operator export therefore **cannot be truthfully imported
through that endpoint as-is** — submitting live customer data with a synthetic
declaration would falsify provenance. The Kea path in this iteration
demonstrates conversion of a **synthetic public-format sample only**; actual
customer ingestion needs a reviewed contract change (new fixture contract /
`synthetic: false` handling, auth, retention) plus authorized access. No live
endpoint, polling loop, or credential is introduced here.

Scope: how a future adapter **could** turn read-only operator exports into the
existing synthetic import envelope once that gate is addressed. Nothing below
claims current CMTS/DNS parsing, a live endpoint, or a universal API.
Product/version behavior varies; verify against the operator's pinned version
before building an adapter.

Existing import envelope (tracked baseline):

- `backend/ipam_demo/imports.py:357-421` — `import_envelope` accepts only
  `source_kind` in `routing`, `dhcp`, `inventory_policy` (mapped to internal
  `route_policy`), plus staged intended inventory when `scenario` is present
  (`imports.py:367-372`). Anything else raises `INVALID_IMPORT`.
- Envelope must declare `schema_version: 1`, `fixture_contract:
  ipam-synthetic-v1`, `synthetic: true` (`imports.py:378-381`), `demo_clock_at`
  equal to the seeded clock (`imports.py:404-406`), a `source` object with
  `authority`/`required_for` per kind (`imports.py:411-415`), per-scope
  `coverage` (`imports.py:112-135`), and `records` bounded by 10 MiB / 10,000
  rows (`imports.py:359-386`).
- DHCP typed rows (`imports.py:143-177,191-201`): `id`, `source_record_id`,
  `scope_id`, `family 4|6`, `address` (no zone id), `client_id`,
  `lease_start_at`, `lease_end_at`, `observed_at`, `original_timestamps`
  (exact echo of the three timestamps). Start/observed must be `<=` demo clock;
  start must be `<` end; family must match address version.
- Routing typed rows (`imports.py:141-166,180-201`): strict `cidr` (no host
  bits), `router_id`, `valid_from_at`, `valid_until_at`, same timestamp rules.
- Coverage semantics (`fixtures/SCHEMA.md:40-61`, `imports.py:127-135`):
  observations use `kind: interval` with start `<` end per scope; policy uses
  `kind: snapshot` with both bounds at the demo clock. `declared_complete` is a
  sender assertion; rejects force `effective_complete: false`. Absence findings
  require complete, fresh, eligible coverage — otherwise `unknown`.
- Identity rules (`imports.py:434-486`, `fixtures/SCHEMA.md:61`): same
  `(source_id, source_run_id)` with identical normalized payload replays the
  original receipt; changed payload conflicts (409). `source_id` cannot change
  kind. Latest ingestion per source/scope wins; no fallback to an older
  complete batch. `source_catalog.py:8-24` reports receipt-derived selection
  only — it never discovers systems.

## 1. Read-only DHCP lease exports/APIs

Generic options (all require a read-only credential or file copy; no
write scope):

- **Kea (generic):** a lease file/CSV dump, or read-only use of the Kea Control
  Agent RESTful control interface and version-specific lease-query commands
  behind an operator-approved read-only access boundary. Kea's basic-auth/TLS
  documentation alone does not establish command-level read-only roles. In this
  iteration the adapter demonstrates conversion of
  a **synthetic public-format sample only**. Verified: the Control Agent
  exposes a RESTful control interface, forwards commands by `service`, and
  supports basic-auth/TLS
  (https://kea.readthedocs.io/en/kea-2.7.6/arm/agent.html). *Unverified:
  exact lease-query command names and output shape for the deployed Kea
  version — confirm against its pinned Management API docs.*
- **ISC dhcpd (generic):** periodic read-only copy of `dhcpd.leases`.
  Verified: log-structured ASCII lease declarations where the last instance of
  a lease wins, with `starts`/`ends`, `hardware`, `uid`, `client-hostname`,
  and `binding state` statements
  (https://kb.isc.org/v1/docs/isc-dhcp-41-manual-pages-dhcpdleases).
  *Unverified: `db-time-format` variant and failover extensions on the
  deployed build.*
- **Infoblox (generic):** read-only Grid API user querying lease objects for a
  bounded network/view/interval. Lead-supplied pointer (not fetched here):
  https://docs.infoblox.com/download/attachments/15433773/Infoblox%20NIOS%20WAPI%209.x%20Reference%20Guide.pdf
  *Unverified: object names, paging, and permission model for the deployed
  NIOS/WAPI version.*
- **Cisco Prime:** no operation claimed. Official documentation supporting a
  read-only lease-export operation could not be verified in this session, so no
  Cisco Prime mapping is stated.

Record shape (normalized before the envelope):

| Field | Meaning |
|---|---|
| `address` | Leased IP string, no zone id |
| `client_id` | Opaque client/hardware identifier (never a subscriber identity in the demo) |
| `lease_start_at` / `lease_end_at` | Half-open validity interval |
| `observed_at` | Export/query time; must be `<=` demo clock at import |
| `scope_id` / `family` | Explicit namespace/VRF + 4/6 chosen by the adapter, never inferred from text |
| `source_record_id` | Stable per-source row key for dedup/receipts |

Timestamp/scope meaning: the lease interval asserts "this address was bound to
this opaque client during `[start, end)`"; `coverage.window_*` asserts "this
scope's DHCP view is complete over this interval". Renewals extend one
interval; they must not be exported as duplicate concurrent leases.

Minimal read-only access: filesystem read on the lease file copy, or an
operator-verified API policy that permits lease reads for named networks/views
without DHCP write, failover-control, or config scope. Do not assume that the
Kea Control Agent's authentication by itself provides that role boundary.

Mapping to the existing envelope: one source-run envelope containing lease
interval records plus declared per-scope interval coverage
(`source.authority: observed`, `required_for: [dhcp_history]`) fits today —
**no new source kind** — provided it sets `fixture_contract:
ipam-synthetic-v1`, `synthetic: true` for demo data, real `demo_clock_at`,
explicit interval coverage, and exact `original_timestamps` echoes. Rejects
(unmapped scope, bad address/family, naive or future-start timestamps) follow
existing rules. A synthetic Kea-format sample converted into this shape is the
bounded demonstration; anything real waits on the contract change above.

What needs a new source kind or rule: lease-history analytics beyond
validity intervals (e.g. churn counters, option-82 circuit text as identity),
pool-label passthrough (pool association must derive from scoped
range membership per `fixtures/SCHEMA.md:55`), or any "expired means free"
reclamation rule — that contradicts the investigation-candidate rule and needs
a new rule version, not an adapter tweak.

## 2. CMTS/CCAP binding snapshot interfaces

Generic options (read-only snapshot of cable-modem/CPE bindings behind a
CMTS/CCAP):

- **SNMPv3 read-only poll of standard DOCSIS MIB binding state** (generic
  modem-status / IP-binding tables), scoped to named devices and a poll
  instant. Lead-supplied pointer (fetched here but returned only a product
  page, so no table operation verified): Cisco cBR SNMP background-sync URL in
  §"What was verified". *Unverified: exact MIB objects and indexing for the
  deployed CMTS/CCAP version.*
- **Vendor-documented read-only telemetry/streaming snapshot** (generic
  modem-session export) where the vendor publishes a read-only binding feed.
  *Assumption — availability, fields, and cadence are vendor/version
  specific; no universal API is claimed.*

Record shape (proposed — **not currently parsed**): device id, modem MAC (or
opaque id), CPE IP, CPE MAC (or opaque id), binding start/end or poll instant
as validity interval, scope id, family.

Timestamp/scope meaning: a snapshot asserts "this binding was observed at this
instant for this CMTS scope"; interval-ization (poll instant ± cadence) is an
adapter assertion and must be declared in coverage, not silently treated as
DHCP-lease-grade history.

Minimal read-only access: SNMPv3 `authPriv` read-only user restricted to the
binding MIB subtree(s), or a read-only telemetry subscription; no write
community, no config/reset scope.

Mapping to the existing envelope: **no fit today**. The importer accepts only
`dhcp` / `routing` / `inventory_policy` observations. A CMTS snapshot is
neither a DHCP lease interval nor a route-state interval, so it **requires a
new source kind** (e.g. `cmts_binding`), new typed-row validation, new
coverage/freshness semantics, and a new detection rule before any finding may
cite it. Do not shoehorn bindings into `dhcp` rows — that would falsify
authority (`observed` DHCP history) and occupancy math.

## 3. DNS resolver activity aggregation (proposed adapter — not current code)

Generic option: aggregated resolver frames (generic `dnstap`-style or
equivalent feed) reduced to per-client activity buckets. Verified shape
background: dnstap `Message` types include `CLIENT_QUERY` / `CLIENT_RESPONSE`
and `RESOLVER_QUERY` / `RESOLVER_RESPONSE`, with `query_address`,
`query_name`, and query/response timestamps
(https://dnstap.info/slides/dnstap.html); BIND 9 documents a `dnstap { … }`
option with per-view `client` / `auth` / `resolver` / `forwarder` / `update`
types and `query`/`response` selection plus a `dnstap-read` utility
(https://bind9.readthedocs.io/en/v9.16.25/reference.html).
*Unverified: transport, framing library, and exact field set on the deployed
resolver/logging stack.*

Record shape (proposed — **not currently parsed**): the activity key is the
**client IP + observation time for a selected resolver message type** (e.g.
client-query count in a bucket), aggregated by scoped prefix. It is **not**
the queried IP and **not** the DNS answer. Drop query names at collection, or
hash them before storage; raw query names must never enter the demo.

Timestamp/scope meaning: a bucket asserts "this client address showed resolver
activity of the selected message type in `[start, end)` within this scope".
It is **traffic-adjacent evidence**, not proof of assignment, routing, or
lease validity. **Do not count an absence as inactivity** — missing buckets
are unknown (no data / no coverage), never zero-use.

Minimal read-only access: read-only access to the aggregated log/frame stream
for named resolvers over a bounded window; no resolver control, zone-write, or
raw-client-identity scope.

Mapping to the existing envelope: **no fit today**. There is no DNS/activity
source kind, no typed row, and no rule consuming "carrying traffic" (see
`docs/ARCHITECTURE.md:59`: allocated, leased, routed, and carrying traffic are
different facts; the demo does not measure traffic). Requires a **new source
kind** plus a new rule that keeps activity separate from occupancy/absence
logic. Until then, DNS-derived rows must be rejected, not mapped.

## What was verified, what was not

- Verified by direct fetch in this session: Kea Control Agent RESTful
  interface / forwarding / auth
  (https://kea.readthedocs.io/en/kea-2.7.6/arm/agent.html); ISC
  `dhcpd.leases` format
  (https://kb.isc.org/v1/docs/isc-dhcp-41-manual-pages-dhcpdleases); dnstap
  message types and fields (https://dnstap.info/slides/dnstap.html); BIND 9
  `dnstap` configuration reference
  (https://bind9.readthedocs.io/en/v9.16.25/reference.html). Exact
  lease-query commands, deployed-version grammars, transports, and field sets
  remain explicitly unverified.
- Lead-supplied pointers, not fetched here (cite as such): Infoblox NIOS
  WAPI reference PDF (see URL in §1); Cisco cBR SNMP background-sync page
  (https://www.cisco.com/c/en/us/td/docs/cable/cbr/configuration/guide/b_cbr_networkmgmt_trblshting_xe16_9/m_snmp_background_synchronization_cbr_16_9.html).
  The Cisco fetch returned only a product page, so no MIB-table operation is
  claimed; CMTS specifics stay version-specific assumptions.
- Cisco Prime: omitted deliberately — no verified official read-only
  lease operation to cite.
- R3 polling implementation is explicitly out of scope and was not started.
