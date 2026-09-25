# Kea sample converter (R4, sample-only)

Bounded converter from a tracked synthetic Kea DHCPv4 memfile CSV to one
valid `source_kind: dhcp` envelope at the seeded synthetic demo clock
(`2026-09-01T00:00:00.000Z`). Source review only; no command or test run
was requested or performed.

## Official behavior used

- Memfile files are plain CSV journals; changes append at the end and LFC
  periodically rewrites a cleaned file. Before cleanup the most recent row
  for each lease wins. DHCPv4 entry order is `address, hwaddr, client_id,
  valid_lifetime, expire, subnet_id, fqdn_fwd, fqdn_rev, hostname, state,
  user_context, pool_id`, where `expire` is epoch seconds
  (`cltt + valid_lifetime`) and `state` is `0 = assigned, 1 = declined,
  2 = expired-reclaimed, 3 = released`. Source: Kea Developer Guide,
  DHCP Database Back-Ends, Memfile Lease Back-End
  (`https://reports.kea.isc.org/dev_guide/d6/dbd/dhcpDatabaseBackends.html`).
- `readCltt` derives CLTT as `expire - valid_lifetime`, and a non-declined
  lease with neither hwaddr nor client ID is a `BadValue`. Column schema
  versions add `state` at 2.0, `user_context` at 2.1 and `pool_id` at 3.0,
  with the minimum valid file reaching `hostname`. Source:
  `csv_lease_file4.cc` source reference
  (`https://reports.kea.isc.org/dev_guide/dc/db8/csv__lease__file4_8cc_source.html`).

## What the converter does

`backend/ipam_demo/convert_kea.py`, wired as
`python -m ipam_demo convert-kea --input ... --scope-map ... --output ... --synthetic-sample`:

- Requires `--synthetic-sample` and a scope-map with
  `synthetic_sample: true`. Only the tracked sample is accepted: the
  scope-map must repeat the pinned `expected_input_filename` and
  `expected_input_sha256`
  (`70d7f38d6686666cd01c97b4245ea26273c75ffa3df8e4da1e3b233c73325707`),
  and input bytes must hash to the same pin. Anything else fails with
  `KEA_SAMPLE_FLAG_REQUIRED` or `KEA_SAMPLE_NOT_RECOGNIZED`, with guidance
  that a real operator export needs a reviewed non-synthetic contract,
  authority, privacy and access gate. Changing the sample needs a reviewed
  pin update. This is a sample-only proof of format mapping, not a generic
  operator importer.
- Validates the exact 12-column header (Kea 3.0 shape); older short
  headers fail instead of guessing missing states. Validates IPv4 address,
  integer epoch/lifetime, `0/1` FQDN flags, `0-3` state, explicit
  `subnet_id` mapping, non-empty hwaddr-or-client-ID, 10 MiB / 10,000-row
  bounds. Infinite lifetime (`0xffffffff`) fails because it cannot be a
  bounded lease interval.
- Collapses append-log duplicates by last row per
  `(subnet_id, address)`, emits only `state 0` with `expire` after the
  demo clock, and reports `input_rows`, `unique_scoped_addresses`,
  `duplicate_rows_collapsed`, `skipped_state`, `skipped_expired` and
  `emitted_records` in stdout JSON. These are converter diagnostics, not
  importer receipts, and no receipt is fabricated.
- Derives `lease_start_at = expire - valid_lifetime`
  (CLTT/most recent transaction, not initial assignment),
  `lease_end_at = expire`, single `observed_at` from the scope-map export
  timestamp at/before the demo clock; `original_timestamps` echoes those
  three normalized UTC ISO strings exactly.
- Emits `fixture_contract: ipam-synthetic-v1`, `synthetic: true`,
  `source_kind: dhcp`, source name `Kea lease export sample (local file)`,
  authority `observed`, `required_for: [dhcp_history]`, coverage copied
  from the scope-map sender assertion after validating every row is an
  interval on a mapped scope with
  `start < end <= export_observed_at <= demo_clock_at` and explicit
  `declared_complete: false`, deterministic UUIDv5 row IDs and
  the scope-map `source_run_id` for idempotent repeats. Writes the output
  atomically (temp file plus rename) so no partial envelope remains. CSV
  parse errors and malformed map types fail as `AppError`, not traceback.

## Sample fixture

17 fictional rows (`fixtures/samples/kea/kea-leases4-sample.csv`) across
Coastal `10.60.1.10-17` and `10.60.2.10-16`, with a renewal supersede on
`10.60.1.10`, a released supersede on `10.60.1.16`, expired/declined/
expired-reclaimed examples, locally administered MACs, opaque client IDs
and blank hostnames. `scope-map.json` maps Kea subnets 11 and 12 to
Coastal scope `6d3bb4b0-ce20-5d83-b609-c09e3468d891`, pins the demo clock,
export time, a bounded 30-minute incomplete snapshot window (not history)
and provenance.

## Truth boundary and store warning

Sample-only: no live Kea API, connection, full lease history, p95 or
forecast. Coverage is a bounded snapshot window asserted by the scope-map
sender, never history and never inferred from present leases. The sample source ID
(`synthetic-dhcp-kea-coastal-sample`) is foreign to the main scheduler
store; importing it there can halt the next synthetic cycle, so use an
isolated store.
