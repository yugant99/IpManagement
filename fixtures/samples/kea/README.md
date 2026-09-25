# Kea DHCPv4 sample (synthetic, local file only)

Small fictional Kea memfile CSV plus an explicit scope-map for the
sample-only converter. All addresses, MACs and client IDs are invented.
Do not substitute a real operator export here.

## Format reference

Kea memfile lease files are append-only journals before LFC cleanup; the
most recent row for each lease wins. DHCPv4 CSV columns are
`address,hwaddr,client_id,valid_lifetime,expire,subnet_id,fqdn_fwd,fqdn_rev,hostname,state,user_context,pool_id`,
with `expire` as epoch seconds (`cltt + valid_lifetime`), `state`
`0 = assigned, 1 = declined, 2 = expired-reclaimed, 3 = released`.
See Kea Developer Guide, DHCP Database Back-Ends, Memfile Lease Back-End
(`https://reports.kea.isc.org/dev_guide/d6/dbd/dhcpDatabaseBackends.html`)
and `csv_lease_file4.cc` source reference
(`https://reports.kea.isc.org/dev_guide/dc/db8/csv__lease__file4_8cc_source.html`).

Supported header caveat: this sample converter accepts only the full
12-column header above (Kea schema 3.0 shape with `state`, `user_context`
and `pool_id` present). Older files that stop at `hostname` are rejected
visibly so missing states are never guessed.

## Files

- `kea-leases4-sample.csv`: 17 fictional rows in Coastal
  `10.60.1.10-17` (Kea subnet 11) and `10.60.2.10-16` (Kea subnet 12).
  Includes one renewal supersede (`10.60.1.10`), one released supersede
  (`10.60.1.16`), one expired lease, one declined and one
  expired-reclaimed row. MACs are locally administered (`02:...`);
  client IDs are opaque `kea-sample-client-*`; hostnames are blank.
- `scope-map.json`: explicit Kea `subnet_id` to Coastal scope UUID
  (`6d3bb4b0-ce20-5d83-b609-c09e3468d891`) mapping, synthetic export
  time `2026-08-31T23:55:00.000Z`, demo clock `2026-09-01T00:00:00.000Z`,
  a bounded 30-minute incomplete snapshot window
  (`2026-08-31T23:25:00.000Z` to `2026-08-31T23:55:00.000Z`, not history),
  pinned input filename plus SHA-256, and sample provenance.

## CLI example

```sh
python -m ipam_demo convert-kea \
  --input fixtures/samples/kea/kea-leases4-sample.csv \
  --scope-map fixtures/samples/kea/scope-map.json \
  --output /tmp/kea-sample-dhcp.json \
  --synthetic-sample
```

## Skipped-row rules

- Append-log duplicates collapse by last row per `(subnet_id, address)`.
- Only `state 0` rows unexpired at the demo clock (`expire > clock`)
  are emitted. Counts for `duplicate_rows_collapsed`, `skipped_state`
  and `skipped_expired` print in the CLI summary; they are converter
  diagnostics, not importer receipts.
- Malformed header, address, epoch/lifetime, unmapped `subnet_id`,
  empty hwaddr plus client_id, infinite lifetime (`0xffffffff`) and
  size/row-count overruns fail visibly instead of silent discard.
- `lease_start_at = expire - valid_lifetime` (CLTT/most recent
  transaction, not initial assignment), `lease_end_at = expire`,
  `observed_at` from the scope-map export time.

## Sample-only truth boundary

Sample-only proof of format mapping, not a generic operator importer.
Only the tracked `kea-leases4-sample.csv` with pinned SHA-256
`70d7f38d…3207` is accepted: the converter requires `--synthetic-sample`,
a scope-map declaring `synthetic_sample: true` and repeating the same
pinned filename and hash, and input bytes matching the pin. A renamed
real export fails the hash gate. Changing the sample needs a reviewed pin
update. A real operator export needs a reviewed non-synthetic contract,
authority, privacy and access gate before ingestion. Output claims no live
Kea API, connection, full lease history, p95 or forecast. Coverage is a
bounded 30-minute incomplete snapshot window from the scope-map sender
assertion, not history and not inferred from present leases.

## Separate-store warning

The emitted envelope uses a foreign sample source ID
(`synthetic-dhcp-kea-coastal-sample`). Adding a foreign source ID to the
main scheduler store can halt its next synthetic cycle; import the sample
into an isolated store only.
