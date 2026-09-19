# Evolving synthetic feed v1

This separate recipe advances the rich synthetic evidence in six-hour simulated steps. It preserves every committed `fixtures/v1/` artifact. The implementation and the [independent expectations](expected-outcomes.json) are source-only: no evolving outputs have been generated, and no import, calculation, test, build or runtime result is claimed.

## Pure interface

`ipam_synthetic_feed.build_cycle(index: int, baseline_envelopes: list[dict]) -> dict` takes the rich-v1 policy envelope and eight rich-v1 observation envelopes. The caller loads these exact inputs from `fixtures/v1/`:

- `inventory-policy.json`
- `observations/dhcp-{north,coastal,central,lab}.json`
- `observations/routing-{north,coastal,central,lab}.json`

Inventory, the pack index, first-path/opt-in variants and expected outcomes are not feed inputs. The rich intended inventory must already be established by its existing explicit setup path. The function deep-copies inputs and uses no filesystem, database, network or wall clock.

The adapter must pin the actual original baseline assets. The pure function checks
identity/shape, not content hashes; matching header strings alone do not establish
that an input is the immutable baseline. Source arithmetic bounds even the largest
DHCP view below 10,000 rows (conservative Coastal bound: 5,960). This is not an
executed count or serialized-size measurement; the normal import limits still apply.

The returned dictionary contains `feed_version: "ipam-evolving-v1"`, `cycle_id: "evolving-v1-{index:06d}"`, `cycle_index`, `demo_clock_at` and `envelopes`. The nine output envelopes are ordered policy, four DHCP, then four routing, with scopes North, Coastal, Central, Lab in each observation group. Their existing `source_id` values and `ipam-synthetic-v1` envelope contract remain stable; every cycle has new run identities, including for unchanged evidence. Same input and index produce the same result.

Cycle 0 is the reference at `2026-09-01T00:00:00.000Z`; the first scheduler advance is cycle 1 at 06:00 UTC. Time is `reference + index * 6 hours`. Indices 0–1460 cover 365 simulated days; the next index raises `ValueError` for exhaustion. The 48-hour event pattern repeats with later timestamps and interval identities, never by rewinding to cycle 0.

## Scenes

Hours below are relative to the reference; repeated episodes use `k = 0, 1, 2, ...`. All validity intervals are half-open. Complete batches carry the rolling 30-day history, retaining intervals that overlap the window and permitted future expiry times. Persistent baseline claims renew daily from their actual final expiry at hour 24. The original Lab conflict ends at hour 2 and is not renewed.

| Scene | Authored behavior |
|---|---|
| Coastal access 1 arrivals and departure | Six added addresses `.100`–`.105` are active at hours `[6+48k, 18+48k)`, with a sequential renewal at hour `12+48k`. Ten added addresses `.100`–`.109` are active at `[30+48k, 42+48k)`. Base occupancy is 90/100; the first eight advances read 96, 96, 90, 90, 100, 100, 90, 90. |
| North expected-route withdrawal and recovery | `10.40.1.0/24` expires at hour 24. Later route intervals are `[36+48k, 72+48k)`. At hour `30+48k`, the selected North routing batch is explicitly incomplete and empty; the following cycle restores complete evidence. Unknown cannot resolve the preceding absence. |
| Lab route recovery | `10.40.2.0/24` becomes present at hour 36, followed by contiguous 48-hour route intervals. |
| Central new managed-space discrepancy | Address `10.80.243.10` and route `10.80.243.0/24` appear at `[36+48k, 48+48k)`, inside the managed `/16` and outside intended prefixes. |
| Central freshness failure and recovery | At hour `42+48k`, DHCP coverage is one hour old and routing coverage is ten minutes old. Each view contains only evidence available at its cutoff. The next cycle supplies fresh evidence; a stale view cannot prove disappearance. |
| Lab new concurrent claims | Principals gamma and delta claim scoped address `10.40.1.101` at `[48+48k, 54+48k)`. The two claims count as one occupied address. Earlier conflicts remain historical evidence while their intervals overlap the rolling window. |

Current occupancy, hourly p95, daily forecast and historical conflict evidence have different time meanings. Current departures do not instantly erase p95 or a conflict from the 30-day history. Sequential renewals and isolated North/Lab address reuse must not create conflicts. These inputs support G05–G08 and evolving G09–G14/G17 comparisons; they do not establish demonstrated questionnaire rows.

Central's original ghost/unregistered observations and Lab's original conflict
already exist in the baseline. The later episodes add specific addresses/evidence;
they do not necessarily flip the whole managed-perimeter finding state. Expiry of
the new Central episode removes those current observations while the original
Central anomalies remain.

## Runtime boundary

The application packaging must include `ipam_synthetic_feed` in its normal wheel. The separate lead-assigned runtime adapter reads baseline envelopes from `IPAM_SYNTHETIC_FEED_DIR`; the pure package does not read that setting. The runtime owner supplies a configurable wall-clock cadence (six hours by default), manual next-cycle control and at most one catch-up cycle. Wall time triggers a step; it does not set simulated timestamps.

Nine imports, clock advancement, the saved calculation run and the persisted cursor must succeed atomically. A failed attempt retries the same index and identities without consuming a cycle. Those orchestration requirements are outside this recipe and remain unverified here. Only actual independently calculated results may be compared with `expected-outcomes.json`; no generator, importer, calculator, detector, scheduler or UI may consume that manifest as operational input.
