# Fixture-local contract: ipam-synthetic-v1

This documents concrete JSON artifacts, not a shared application schema change. `schema_version: 1` has a file-specific meaning; inspect `pack.json`'s explicit file roles. Stage 1 intended inventory retains its existing shape. Observation envelopes and the routing-policy sidecar are **proposed Stage 2 inputs**, accepted by the project lead as a fixture proposal; application mapping remains unresolved. No importer is supplied here.

## Common conventions

- Every value is fictional. IPv4 uses private space, except the outside-perimeter documentation route `198.51.100.0/24`; IPv6 uses `2001:db8::/32`. Client/router IDs are invented opaque strings, not subscriber identifiers.
- IDs are UUID strings. Existing Stage 1 IDs remain unchanged. Added IDs use UUIDv5, namespace `fed69f72-8aa8-48e5-896e-cc50e06bc004`, name prefix `ipam-synthetic-v1/` and the explicit stable key in the generator.
- `scope_id` identifies isolation. `domain`, region, names and matching address text do not replace it. Family is integer `4` or `6`; prefix CIDRs are strict network addresses.
- Times are UTC ISO 8601 with milliseconds. Default clock is `2026-09-01T00:00:00.000Z`. Historical window is `[2026-08-02T00:00:00.000Z, 2026-09-01T00:00:00.000Z)`. Validity intervals are half-open; address ranges/exclusions are inclusive at both ends.
- Records can remain valid beyond coverage end and demo clock. A final lease/route ending September 2 is valid at the September 1 clock. Coverage end says how recently the source asserts its view; it is not a forced expiry. Current presence still requires `start <= clock < end`.
- `source_id + source_run_id + source_record_id` locates immutable source evidence. Retain the entire raw record and original timestamps before normalization. The **application** supplies real wall-clock `ingested_at`, receipt and validation result; the generator must not fabricate these. Its file hashes are byte hashes, **not** canonical normalized-envelope replay hashes.

## Intended inventory: inventory.json

Exactly the foundation envelope keys: `schema_version`, `scenario`, `demo_clock_at`, `source_id`, `source_run_id`, `scopes`, `prefixes`, `pools`, `allocations`. `schema_version` is integer 1; `scenario` remains `baseline` because that is the foundation's supported seed shape. The distinct rich identity is `synthetic-inventory-rich / rich-v1-inventory`; it must never masquerade as `synthetic-baseline / baseline-v1`.

| Array | Fields in every row |
|---|---|
| `scopes` | `id`, `name`, `namespace`, `domain`, `region`, `managed_cidrs: string[]`, `source_record_id` |
| `prefixes` | `id`, `scope_id`, `family`, `cidr`, `parent_id: UUID|null`, `owner`, `purpose`, `tags: string[]`, `custom_fields: object<string,string>`, `version: positive integer`, `source_record_id` |
| `pools` | `id`, `scope_id`, `prefix_id`, `name`, `management_mode: dhcp|static`, `allocation_authority: local|external`, `ranges`, `exclusions`, `pool_version: positive integer`, `source_record_id` |
| `allocations` | `id`, `scope_id`, `prefix_id`, `pool_id: UUID|null`, `family`, `address`, `owner`, `purpose`, `source_record_id` |

Ranges/exclusions are arrays of `{start: IP string, end: IP string}`. Ranges are disjoint, inside their prefix, and exclusions are inside ranges. Capacity is distinct configured range addresses minus exclusions, not CIDR cardinality. Pool family derives from prefix. Blank `owner`/`purpose`, empty tags and custom fields on Lab `10.40.15.0/24` are intentional missing metadata, not invented values.

Do not add API-derived `scope_name`, `address_count`, pool `family`/`capacity`, `origin` or scope `synthetic` to seed rows. Derived IPv6-sized counts must later be decimal strings. All original baseline rows, including parent pointers, pool ranges, source-record keys and the intended assignment `10.40.2.2`, are copied unchanged. Top-level source/run identity changes, so richer-envelope provenance is distinct; use the pinned snapshot when identifying original row lineage.

Managed perimeters are independently declared: North `10.40.0.0/16` and `2001:db8:40::/48`; Lab `10.40.0.0/16`; Coastal `10.60.0.0/16` and `2001:db8:60::/48`; Central `10.80.0.0/16` and `2001:db8:80::/48`. Central/Coastal IPv4 intended parents cover only `/20`, deliberately leaving managed space outside inventory.

## Intended route policy: inventory-policy.json

Envelope: `schema_version: 1`, `fixture_contract: ipam-synthetic-v1`, `synthetic: true`, `demo_clock_at`, `source_id: synthetic-inventory-policy`, `source_run_id: rich-v1-policy`, `source_kind: inventory_policy`, `effective_from_at`, `source`, `coverage`, `records`. `source` has `name`, `owner`, `authority: intended_policy`, `required_for: [route_policy]`. Stage 2's owner accepted mapping `inventory_policy` to its internal route-policy type; this is coordination, not executed compatibility evidence.

Policy coverage is a declared scope snapshot: `{scope_id, kind: snapshot, window_start_at: demo_clock_at, window_end_at: demo_clock_at, declared_complete: boolean}`. Equal endpoints are intentional for snapshots, unlike validity/interval coverage. `effective_from_at <= clock` supplies policy effectivity. Select latest policy ingestion per source/scope snapshot. Omitted or rejected policy in a newly selected snapshot is unknown; do not fall back per prefix to an older policy or invent `false`. An explicit accepted `expects_announcement: false` is different from omission. Scopes outside a batch's declared coverage are unaffected by that batch.

Each of 60 records has `source_record_id`, `scope_id`, `prefix_id`, `expects_announcement: boolean`, `route_match_policy: exact|covering`. Exactly one record per intended prefix. Policy applies from August 2; this pack has no historical policy changes. `exact` is the default; `covering` explicitly allows an active same-scope/same-family containing route. `expects_announcement: false` means no absence finding is requested, not that a route is forbidden. Positive route presence may still support the zombie rule. This is intended operational policy, not expected detection output.

## Observations: observations/*.json and opt-in observation variants

| Envelope field | Type and meaning |
|---|---|
| `schema_version`, `fixture_contract`, `synthetic` | `1`, `ipam-synthetic-v1`, `true` |
| `demo_clock_at` | Fixed evaluation clock, independent of wall-clock import |
| `source_id`, `source_run_id` | Stable strings identifying feed and whole batch |
| `source_kind` | `dhcp` or `routing` |
| `source` | `{name, owner, authority: observed, required_for: string[]}`; declares observation ownership, not intended-allocation authority |
| `coverage` | Array of `{scope_id, kind: interval, window_start_at, window_end_at, declared_complete: boolean}`; one scope per supplied batch |
| `records` | Typed rows below, preserving invalid raw fields in opt-in cases |

`source_id` is `synthetic-{dhcp|routing}-{north|coastal|central|lab}`. Every default run is `rich-v1-complete`. `required_for` is `dhcp_history` or `routing_view`. Interval coverage describes the source's whole declared managed perimeter within that scope, including no-observation regions; it must not be inferred from present rows. `declared_complete` is a sender assertion; the importer must derive effective completeness after rejects. Observation freshness uses covered end: DHCP ≤30 minutes and routing ≤5 minutes against the selected clock. All 720 historical samples require applicable complete coverage. No-data and missing source are not complete zero-use statements.

Common row fields: `id: UUID`, `source_record_id: string`, `scope_id: UUID`, `family: 4|6`, `observed_at: timestamp`, `original_timestamps: object`.

- DHCP adds `address: IP`, `client_id: opaque string`, `lease_start_at`, `lease_end_at`. Conflict identity is scope + family + address with intersecting validity and incompatible principals. Pool association derives from scoped address/range membership; no fixture-supplied pool label chooses the result. Preserve managed observations outside pools for discrepancies.
- Routing adds `cidr: strict CIDR`, `router_id: opaque string`, `valid_from_at`, `valid_until_at`. These are bounded route-state intervals, not a BMP event/withdraw parser. Compare against independent managed perimeters before flagging unregistered announcements.
- `original_timestamps` repeats exactly the input values for `observed_at` and the applicable pair of bounds. It intentionally includes null, naive or invalid-bound values in opt-in cases. It is raw provenance, not a second source of eligibility truth.

Reject unmapped scopes, bad addresses/family, host-bit CIDRs, missing bounds, naive timestamps, empty/reversed intervals and future observation/start times for calculations. Future ends are allowed. Required rejected observations make effective completeness false. Positive accepted observations may remain usable in partial batches; absence conclusions cannot use incomplete coverage.

Latest accepted ingestion sequence per source/scope wins. Opt-in runs must be applied **after** the defaults for that source, one scenario at a time in isolated integration datasets. Never order by run-name text, union old and new batches, or silently fall back to a complete predecessor. Same `(source_id, source_run_id)` with identical normalized payload must return the original receipt; changed payload under that identity must return conflict. Replaying the old complete batch therefore cannot restore selection after a newer partial batch; restoration needs a new complete run identity. Each import is bounded by 10 MiB/10,000 records; each provided envelope is below that intended budget by its generated size/count, without an importer acceptance claim.

## Foundation-only first path: first-path/*.json

This separate recipe needs only the preserved Stage 1 ledger, not richer inventory promotion. `first-path/inventory-policy.json` has all six foundation prefix IDs and two scope snapshots, source `synthetic-first-path-policy`, run `first-path-v1-policy`. Only North DHCP `10.40.1.0/24` and Lab `10.40.1.0/24` require exact routes; the other four explicitly do not.

Routing source IDs are `synthetic-first-path-routing-north` and `synthetic-first-path-routing-lab`, isolated from richer feeds. Default run `first-path-v1-complete` has one North route and zero Lab routes, both complete/fresh views. Lab `partial`, `stale`, and `recovery` filenames use distinct `first-path-v1-*` runs of the same Lab source; recovery has a present Lab route. `inventory-policy-lab-partial.json` uses policy run `first-path-v1-policy-lab-partial`, declares only Lab with incomplete coverage and no records. It must replace Lab policy selection without altering North or falling back to Lab's older expected flag. Do not mix rich and first-path feed families in one comparison without defining multi-source precedence.

## Pack index and comparison oracle

`pack.json` includes version/clock/window, foundation commit/path/snapshot/hash, `default_inputs`, `opt_in_inputs`, separate `first_path` inventory dependency/input lists, actual rich-pack `counts`, per-file `generated_files` entries (`bytes`, `sha256`, and `records` where applicable), and fictional `provenance`. Paths are relative to `fixtures/v1/`. Inventory counts are in `counts`; policy rows are not prefixes or observations. Opt-in and first-path records are excluded from rich default totals. The index does not hash itself.

`expected-outcomes.json` is independently authored: version, clock, evidence status, default recipe, pool expectations, scenario comparisons and opt-in receipts/reasons. It is not generated or read by the generator, appears in neither input list, and must never be loaded by an importer, calculator, detector or dashboard. A later authorized comparison harness may read it **after** the application independently produces results. Its numbers are design expectations, not measured application results.
