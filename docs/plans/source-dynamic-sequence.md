# Source dynamic sequence: evolving synthetic feed (cycles 3–4)

Scope: source-only map of the existing `ipam-evolving-v1` feed. It is derived from
`fixtures/evolving/README.md`, `fixtures/SCHEMA.md`, `fixtures/v1/pack.json`,
`fixtures/v1/inventory-policy.json`, and the two readable observation feeds
`fixtures/v1/observations/dhcp-north.json` and `fixtures/v1/observations/routing-north.json`.
No cycle has been generated, no import or calculation run, and no runtime result is claimed.
The authored occupancy readings below are expectation text, not measured output.

## 1. Two clocks and a baseline window

- **Simulated clock** (`demo_clock_at`). Per `fixtures/evolving/README.md` "Pure interface",
  time is `2026-09-01T00:00:00.000Z + index × 6h`; cycle 0 is the reference and cycle 1 is
  the first advance at 06:00 UTC. Therefore **cycle 3 = `2026-09-01T18:00:00.000Z`** and
  **cycle 4 = `2026-09-02T00:00:00.000Z`**. Indices 0–1460 cover 365 simulated days; the
  next index raises `ValueError`. The feed emits nine envelopes (policy, four DHCP, four
  routing) with `cycle_id` `evolving-v1-{index:06d}`, so cycles 3 and 4 are
  `evolving-v1-000003` and `evolving-v1-000004`.
- **Ingestion wall time** (`ingested_at`). Per `fixtures/SCHEMA.md` "Common conventions", the
  application supplies real wall-clock ingestion; the generator must not fabricate it. Per
  the README "Runtime boundary", a configurable six-hour cadence (manual next-cycle, at most
  one catch-up) triggers a step but does not set simulated timestamps. Wall time can change
  *when* a cycle lands; it never changes `demo_clock_at`.
- **Baseline window.** Every committed `fixtures/v1/` envelope is fixed at
  `demo_clock_at = 2026-09-01T00:00:00.000Z` over `[2026-08-02T00:00:00.000Z, 2026-09-01T00:00:00.000Z)`
  (`fixtures/v1/pack.json` lines 5–7). Evolving cycles roll that 30-day history forward with
  new interval identities; they never rewind to cycle 0 (README "Pure interface").

## 2. What cycle 3 changes (2026-09-01T18:00:00Z)

- **Coastal access 1 departure.** README "Scenes", "Coastal access 1 arrivals and departure":
  six added addresses `.100`–`.105` are active at `[6+48k, 18+48k)`. With `k = 0` the interval
  is half-open `[6, 18)`, so at hour 18 those six addresses **leave** while the ten-address
  `.100`–`.109` episode (`[30+48k, 42+48k)`) has not yet started. The same row states the
  first eight authored occupancy reads are `96, 96, 90, 90, 100, 100, 90, 90`, i.e. cycles 1
  and 2 read 96, and cycles 3 and 4 read 90. Treat that as the source's expectation, not a
  computed count.
- **New run identities.** README "Pure interface" requires a new `source_run_id` for every
  envelope each cycle, including unchanged evidence, so cycle 3 differs from cycle 2 in
  coverage/run identity even where the evidence is otherwise the same.
- No other scene transition lands on hour 18. Lab's original conflict ends at hour 2
  (README "Scenes" intro), so by cycle 3 it survives only as historical evidence inside the
  rolling 30-day window.

## 3. What cycle 4 changes (2026-09-02T00:00:00Z)

- **North expected-route withdrawal.** README "Scenes", "North expected-route withdrawal and
  recovery": `10.40.1.0/24` expires at hour 24. In the tracked evidence this is record
  `route-north-10.40.1.0/24-10` (`id bf956b6f-91ce-53da-8462-7f7d6803eaa6`,
  `fixtures/v1/observations/routing-north.json`): `router_id north-router-01`, scope
  `7d2075a0-6fd4-4d58-a26c-1e7d8cb0a001`, `valid_from_at 2026-08-29T00:00:00.000Z`,
  `valid_until_at 2026-09-02T00:00:00.000Z`. Because intervals are half-open (SCHEMA.md
  "Common conventions") and the cycle-4 clock equals that endpoint, the route is **no longer
  present** at cycle 4. The next North route interval begins at hour 36 (`[36+48k, 72+48k)`).
- **Policy still expects it.** `fixtures/v1/inventory-policy.json` record
  `policy-prefix-north-dhcp` (`prefix_id 41aca2b0-ec1d-4f64-8d21-c5af0ab0b002`) sets
  `expects_announcement: true` and `route_match_policy: exact`. With a complete routing view at
  cycle 4, that policy makes the withdrawn route an **expected-announcement absence**, not a
  stale-source unknown.
- **Persistent baseline claims renew.** README "Scenes" intro: persistent baseline claims
  "renew daily from their actual final expiry at hour 24". The pattern is visible in
  `fixtures/v1/observations/dhcp-north.json`, e.g. `lease-north-1-client-001-renewal-5`
  (`id 2f67aee2-1bec-5190-9bdb-a4636de01d03`) ending `2026-09-02T00:00:00.000Z`. So cycle 4
  holds presence by renewal rather than dropping those addresses.
- Coastal remains at the authored 90 reading (README "Scenes").
- **Do not conflate cycle 4 with cycle 5.** README, same scene: at hour 30 (cycle 5) the
  selected North routing batch is "explicitly incomplete and empty", which yields unknown and
  "cannot resolve the preceding absence"; cycle 6 restores complete evidence. Absence at
  cycle 4 (complete view, expected route gone) is a different state from cycle 5 (incomplete
  view, no conclusion).

## 4. What a domain viewer should see through permitted reads

Keep the following layers separate; each has a different truth value.

- **Simulated clock.** The envelope `demo_clock_at`, shown as the evaluation time. It is not
  the ingestion time and not the freshness measure by itself.
- **Run summary/receipt.** `source_id` (for example `synthetic-dhcp-north`,
  `synthetic-routing-north`), the per-cycle `source_run_id`/`cycle_id`, declared coverage, and
  accepted/rejected/duplicate counts. At baseline these run as `rich-v1-complete`
  (`fixtures/v1/pack.json`, counts: 2000 DHCP lease intervals, 200 routing observations). A
  replay of the same identity with an identical payload returns the original receipt; a
  changed payload is a conflict (SCHEMA.md "Observations").
- **Freshness and completeness.** DHCP freshness is ≤30 minutes and routing ≤5 minutes against
  the selected clock; `declared_complete` is only a sender assertion and the importer derives
  effective completeness after rejects (SCHEMA.md "Observations"). Coverage describes the
  whole declared perimeter, "including no-observation regions", and must not be inferred from
  present rows.
- **Actual findings.** Produced by the calculator from accepted evidence for the current saved
  run. The viewer must not read `fixtures/evolving/expected-outcomes.json` or any
  expected-answer label to choose output (SCHEMA.md "Pack index and comparison oracle";
  README "Runtime boundary").
- **Not permitted read.** A domain viewer never consumes the comparison oracle; expected
  outcomes may only be compared against independently calculated results, by an authorized
  harness, after the fact.

Concretely: through cycle 3 the viewer should see the Coastal occupancy easing as the six
addresses depart, and through cycle 4 the viewer should see the North `10.40.1.0/24`
expected-route absence carrying its policy reference and expired interval id, while Coastal
stays flat and the baseline leases remain present through renewal. Exact anomaly counts at
these cycles cannot be established from source alone; they must come from an executed
calculation run.

## 5. What would require the coordinator's off-camera acquisition

- **Real telemetry.** Only a synthetic baseline, synthetic DHCP imports and synthetic routing
  observations exist. Live DHCP/lease, BMP, CMTS, RADIUS/Diameter, CGNAT, ARP/ND, external
  BGP+RPKI, active probing, IPDR, flow export and DNS resolver sources are unbuilt and
  unconnected (see `docs/plans/evidence-sources-manifest-draft.json`).
- **Private source material.** Customer documents and the local `assessment/` area are
  excluded from this public repository; the coordinator would supply any non-public evidence
  through an approved channel, not this repo (AGENTS.md line 25).
- **Actual results.** Any measured occupancy, p95, absence or conflict count needs the app
  run on the feed. Comparing to `fixtures/evolving/expected-outcomes.json` additionally needs
  an authorized comparison harness after independent computation.
- **Infrastructure and deployment.** A hosted environment, provider, cost or data lifetime is
  a separate authorization, not implied by this sequence (ARCHITECTURE.md section 8; the
  current permission record is `docs/STATUS.md`).
- **Sensitive identity data.** CMTS bindings, AAA accounting, CGNAT logs and DNS query logs
  carry subscriber-identifying detail; they stay synthetic-only here.

## 6. Suggested before/after UI sequence for a later R3 worker

Concise sequence; treat the floor readings as authored expectations until the app computes
them.

**Before (cycle 3, `evolving-v1-000003`, 2026-09-01T18:00:00Z)**

1. Header: simulated clock, current `cycle_id`/`source_run_id`, and a separate wall-clock
   ingestion stamp.
2. Source-status strip: per source, coverage window and effective completeness plus freshness
   age (DHCP ≤30 min, routing ≤5 min).
3. Coastal domain view: base occupancy 90/100 after the `.100`–`.105` departure; note the
   renewal at hour 12.
4. North domain view: expected route `10.40.1.0/24` still present.

**After (cycle 4, `evolving-v1-000004`, 2026-09-02T00:00:00Z)**

1. Header: clock advanced to 2026-09-02T00:00:00Z; new run identities; ingestion time shown
   independently.
2. North domain view: `10.40.1.0/24` absent; the finding links the withdrawn interval
   (`route-north-10.40.1.0/24-10`, `bf956b6f-91ce-53da-8462-7f7d6803eaa6`) and the policy
   record `policy-prefix-north-dhcp` (`expects_announcement: true`, `exact`).
3. Coastal and baseline-lease views: unchanged through renewal; no false drop.
4. A "what changed" delta panel limited to source-backed facts: Coastal departures, the North
   absence, baseline renewals. No invented counts.
5. Guardrail banner distinguishing this cycle from cycle 5, where the North routing batch is
   incomplete/empty and the result is unknown, not absent.

**Order rationale.** Show clock first, then source status, then domain findings, so the viewer
can tell when something changed (clock), how trustworthy the view is (freshness/completeness),
and only then what was found (findings).
