# Synthetic data pack v1

## Evolving feed addition (source only)

The later scheduled-fetch requirement adds the pure Python package
[`ipam_synthetic_feed`](../fixtures/evolving/ipam_synthetic_feed/__init__.py), with
its [interface and timeline](../fixtures/evolving/README.md) and a separate
[authored comparison manifest](../fixtures/evolving/expected-outcomes.json).
The original generator and every `fixtures/v1/` artifact remain unchanged.

`build_cycle(index, baseline_envelopes)` accepts the original policy plus eight
rich observation envelopes, without reading files or application state. It returns
nine importer-shaped envelopes and explicit cycle/time metadata. Index zero is a
reference; the scheduler starts with index one at `2026-09-01T06:00:00.000Z`.
Each successful cycle advances six **simulated** hours, independently of the
configurable real fetch interval (default six hours). Manual **Run now** consumes
the next cycle. The provider does not schedule anything itself.

The recipe adds real changes to fictional observations: sequential renewals,
arrivals and expiry, North route withdrawal/partial export/recovery, Lab route
recovery, additional Central unregistered observations, stale-source recovery and
new overlapping Lab claims. Existing rich logical source IDs continue with new
`evolving-v1-NNNNNN` run identities. UUIDs for new intervals derive from stable
event identities. Original intervals are retained unchanged until they leave the
rolling 30-day window; timestamps are never shifted to manufacture fresh history.
The eight-step story repeats on increasing time, with a visible upper bound of
365 simulated days rather than a silent cursor rewind. Thirty-day p95 and historical
conflict findings need not disappear when current occupancy changes.

The application lane owns normal package inclusion, the baseline-file adapter
using `IPAM_SYNTHETIC_FEED_DIR`, schedule storage/UI and one atomic
clock/import/calculation/exception/cursor transaction. It must validate the pinned
original assets and the rich inventory, refuse mixed first-path/foreign authority,
use the existing shared run lock, and retry a failed cycle at the same index.
Expected outcome labels must never enter the provider or that transaction.
The complete integration contract is in the fixture-local README; this source
does not change backend schemas, startup, the import API or intended allocations.

**Evidence boundary:** this addition was authored and source-reviewed only.
No evolving batches have been generated or imported; no recipe, tests, builds,
scheduler or application runtime has been executed. The existing generated counts
below describe the frozen v1 pack, not executed evolving-feed outputs.

Actual generated inputs are in [`fixtures/v1/`](../fixtures/v1/), with the [standard-library generator](../fixtures/generate.py), [field contract](../fixtures/SCHEMA.md), [file/count/hash index](../fixtures/v1/pack.json) and independent [expected outcomes](../fixtures/v1/expected-outcomes.json). These artifacts are implemented; app import, calculations and rule execution have **not** been demonstrated.

The fixed clock is **2026-09-01T00:00:00.000Z**. History spans `[2026-08-02T00:00:00.000Z, 2026-09-01T00:00:00.000Z)`, exactly 30 days. Final validity intervals extend past the clock to support current presence. Ingestion timestamps belong to the eventual application, not the fixture generator.

## Generated files and counts

| Scope | Prefixes | Pools | DHCP intervals | Routing observations |
|---|---:|---:|---:|---:|
| North | 15 | 2 | 750 | 50 |
| Coastal | 15 | 2 | 679 | 50 |
| Central | 15 | 2 | 51 | 70 |
| Lab | 15 | 2 | 520 | 30 |
| **Rich default total** | **60** | **8** | **2,000** | **200** |

Four scopes; 51 IPv4 and nine IPv6 prefixes; seven DHCP pools and one local static pool. The original intended allocation `10.40.2.2` remains the single intended address allocation. The generator reports the rich totals and file record counts while writing; no application receipt is implied.

There are **28 generated JSON files**: inventory, 60-row policy sidecar, eight observation batches, ten opt-in variants, seven separate first-path files and the pack index. The unchanged foundation snapshot and independently authored expected manifest bring the committed JSON total to **30**. Opt-in and first-path records are not added to the rich totals; they are alternative scenarios. The index records each generated data file's bytes/SHA256 and observation/policy row count, excluding its own digest.

The 2,000 leases comprise 1,968 sequential intervals for 410 persistent clients, 29 additional Coastal growth clients, two conflicting Lab claims and one Central ghost claim. Of the 410 persistent clients, 328 have five intervals and 82 have four. Twenty route subjects each have ten consecutive intervals. This supplies a full hourly history without confusing event volume with active addresses.

## Regeneration and provenance

```sh
python3 fixtures/generate.py
```

Python 3.10+ standard library only; no installation, network, database or application runtime required. The script resolves paths relative to itself, writes its named files and prints counts. It does not delete other files or read expected outcomes. Writes are not transactional: an error stops visibly and may leave a partial artifact set; complete generation before publishing. No reproducibility comparison command or application validation was run.

The frozen [`foundation-baseline.json`](../fixtures/v1/foundation-baseline.json) was copied with `git show` from `backend/ipam_demo/data/baseline.json` at published foundation commit **ea51aa64b1780fa5c171e95ae59a619bf0109d52**, branch `codex/part-1-foundation`. Its Git blob is `1fda9dbba4fb50ce93261f7417b18ff89720f43d`; the same commit supplies `docs/FOUNDATION_API.md`. The generator reads this local frozen input and preserves every original scope/prefix/pool/allocation row and UUID. It never rewrites Stage 1's packaged seed. `scenario: baseline` and seed schema version 1 remain intact; rich source/run changes to `synthetic-inventory-rich / rich-v1-inventory`.

Added UUIDs use fixed UUIDv5 names; generation contains no random draw or wall clock. Per-scope DHCP/routing source identities, typed records, raw timestamps, complete/partial coverage and intended-policy authority are explicit. These are wholly fictional public-repository inputs: no customer topology, credentials, source attachments, subscriber identity or live telemetry. Later content changes require a new version/run identity; do not publish changed envelopes as identical-batch replays. The deliberately changed replay file is the one explicit negative control.

## Scenario/file map

All paths below are relative to `fixtures/v1/` and rely on `inventory.json`; route expectations additionally use `inventory-policy.json`. The numbers are independently authored recipe expectations, **not executed rule outputs**.

| Scenario | Evidence file / subject | Intended comparison |
|---|---|---|
| Pressure, p95 branch | `observations/dhcp-coastal.json`, access 1 | 90/100 p95, above the agreed 80% threshold |
| Pressure, forecast branch | Same file, access 2 | Daily counts 40…69; monthly p95 68; OLS +1/day; 31 days to full, below 60 |
| Oversized | `observations/dhcp-central.json`, access 2 | 10/100 p95, below 50%; positive leases prevent zombie classification |
| Zombie candidate | Central access 1; Central DHCP + routing files | Complete zero-lease history and current route; also oversized, never safe-to-reclaim |
| Ghost DHCP scope | Central DHCP, `lease-central-unlisted` | `10.80.240.10` is managed by `/16` but outside every intended prefix; intended IPv4 parent is only `/20` |
| Unregistered managed route | Central routing, `10.80.241.0/24` | Same independent perimeter distinction; `198.51.100.0/24` is an outside-managed-space control |
| Missing expected route | Lab routing + policy, `10.40.2.0/24`; Coastal routing + policy, `10.60.4.0/24` | Complete views lack exact expected routes |
| Covering policy control | Coastal `10.60.3.0/24` and aggregate `10.60.0.0/20` | Aggregate satisfies explicit covering mode; does not satisfy exact mode on Coastal `.4` |
| Healthy occupancy | North DHCP; Lab access 2 | 150/245 and 60/100; complete history and no positive growth |
| Assignment conflict | Lab DHCP, `lease-lab-conflict-alpha/beta` | Same scoped `10.40.1.100`, incompatible principals, concurrent `[Aug 31 22:00, Sep 1 02:00)`; one occupied address |
| Legitimate reuse and renewals | North/Lab DHCP, `10.40.1.10`; North client 001 renewal 1/2 | Separate scopes do not conflict; exact meeting boundary Aug 8 is sequential |
| Metadata and hierarchy | Inventory, Lab `10.40.15.0/24`; North declared parent/children | Empty metadata stays visible; declared parent/child containment is legitimate |
| Static control | Original North static pool | Capacity 13 and one intended assignment; no DHCP inactivity inference |

Hourly p95 uses 720 eligible samples, nearest-rank item 684. Daily p95 uses all 24 hourly samples; forecasts use 30 consecutive complete days here. Lab access 1 has monthly p95 60 but current occupancy 61: the conflict adds one distinct address during the last two hours. Its final daily p95 is 61, slope is 1/155 and mathematical exhaustion is 6,045 days, outside the 365-day illustrative horizon; do not show a clamped calendar date or label it no-growth. Central's candidate union is 200 distinct assignable addresses; overlapping zombie/oversized labels on access 1 cannot double-count it.

## Opt-in quality and unknown controls

Use isolated future integration datasets, apply defaults before one variant, and retain selected source-run references. Latest accepted ingestion per source/scope wins. Replaying an old complete batch returns its old receipt, so it **cannot** restore the selection after a newer partial batch. In-place restoration needs a new complete run ID. No app import or reset command is supplied here.

| Opt-in file | Records | Intended behavior |
|---|---:|---|
| `opt-in/dhcp-{coastal,central}-partial.json` | 0 each | Explicitly incomplete; pressure/oversized/inactivity conclusions unknown, never zero-filled |
| `opt-in/routing-{coastal,central,lab}-partial.json` | 0 each | Missing route evidence unknown; no fallback or false resolution |
| `opt-in/dhcp-central-stale.json` | 51 | Coverage end 60 minutes old exceeds 30-minute DHCP limit |
| `opt-in/routing-central-stale.json` | 70 | Coverage end 10 minutes old exceeds five-minute routing limit |
| `opt-in/dhcp-central-invalid.json` | 9 | Expected receipt 1 accepted / 7 rejected / 1 duplicate; missing expiry, unmapped scope, bad IP, naive time, future start, reversed interval and family mismatch |
| `opt-in/routing-central-invalid.json` | 7 | Expected 1 accepted / 6 rejected / 0 duplicate; missing end, CIDR host bits, future observation, family mismatch, unmapped scope and reversed interval |
| `opt-in/dhcp-north-changed-replay.json` | 750 | After original North batch, changed payload under identical identity must conflict with no mutation |

Raw bad values remain in files. Valid controls in invalid batches have distinct identities and current positive evidence, so partial acceptance cannot discard everything. Required rejects force effective completeness false despite declared completeness. Identical whole-batch replay is exercised by resubmitting an unchanged default file, not by a second copy with a different run ID. Missing-source behavior can be compared by withholding a required source in an isolated dataset; absence of a file is never a complete zero-use assertion.

## Stage 2 integration handoff

The lead and Stage 2 owner coordinated a smaller `first-path/` recipe against the existing two-scope/six-prefix Stage 1 ledger. It avoids richer inventory activation entirely:

1. Use the existing foundation ledger and `first-path/inventory-policy.json`: North DHCP and Lab `10.40.1.0/24` require exact routes; the other four foundation prefixes explicitly do not.
2. Select `first-path/routing-north.json` (one present route) and `first-path/routing-lab.json` (complete fresh empty view). Expected comparison: North healthy; Lab missing expected route.
3. Select a newer Lab `routing-lab-partial.json` or `routing-lab-stale.json`: Lab becomes unknown, not resolved. The distinct-run `routing-lab-recovery.json` then supplies a fresh complete present route for actual recovery comparison.
4. Separately, `inventory-policy-lab-partial.json` declares only Lab with incomplete coverage and no policy rows. Lab policy becomes unknown without per-prefix fallback; North stays unaffected. Routing recovery alone cannot repair unknown intended policy.

Policy envelopes explicitly declare `source_kind: inventory_policy`, `authority: intended_policy` and per-scope snapshots with equal clock endpoints. The Stage 2 owner accepted that mapping to its internal route-policy type. Omitted/rejected policy remains unknown; explicit false is different from omission. These files contain intended policy only. Rich and first-path feed families use distinct source IDs and must not be mixed without an explicit multi-source precedence decision.

**Remaining integration dependencies:** Stage 2 must map/persist these policy/observation schemas, assign actual ingestion times/sequences, enforce receipt/replay/coverage rules, and run the agreed missing-route calculation when checks are authorized. Rich `inventory.json` is seed-shaped, but the existing Stage 1 CLI accepts only its packaged seed: no custom-path CLI/import compatibility is claimed. Rich intended-state activation requires lead-owned integration; changed inventory imports must remain staged and preserve approved local allocations. Do not replace the packaged baseline silently.

`expected-outcomes.json` is outside all input lists, never read by this generator, and must stay outside import/detection/UI code. Later comparison may consume it only after independent results exist. Source generation was run twice (initial artifacts, then coordinated first-path/policy update). Independent review was static source/contract reading only. No tests, smoke checks, application builds, imports, rule calculations, container/VM/database operations or deployment were run. This supports G05–G08 and later G09–G14/G17 scenarios; it does not mark any questionnaire application behavior complete.
