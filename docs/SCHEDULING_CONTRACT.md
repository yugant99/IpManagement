# Evolving synthetic feed and scheduling

Lead decision, 2026-09-19. **Required source work; not implemented or demonstrated at this checkpoint.** The user selected an evolving synthetic feed we control, every six hours configurable, with a manual **Run now** button. This supersedes RFP-068's earlier optional/deferred status. It does not authorize execution, infrastructure or a real network connector.

## Owners and delivery boundary

- Existing data owner `01a0b8b9-82fb-7a11-bc50-ec3a5b234729`: new `fixtures/evolving/ipam_synthetic_feed/__init__.py`, supporting files under `fixtures/evolving/`, `docs/SYNTHETIC_DATA.md` and its data handoff. Keep its existing clean worktree; new branch `codex/part-2-evolving-feed` from Stage 3 `c2629fbf6516a744e65c52a424700563c0f4a0a2`. Preserve every `fixtures/v1/` byte and the original generator. No backend edits.
- Stage 4 scheduler/integration owner: new backend scheduler and feed adapter, schedule UI/client, minimal `app.py` lifecycle/routes/shared lock, store/schema migration, and the existing `pyproject.toml` wheel package list. Include `fixtures/evolving/ipam_synthetic_feed` as a normal packaged Python module alongside `backend/ipam_demo`; no dynamic generator execution, runtime path injection, duplicate producer or dependency addition.
- Core keeps `state_ops.py`, `__main__.py` and state documentation. Coordinate shared migratable-version changes with that owner; do not rewrite state commands.
- Spencer keeps container/Compose/ops/operator files. The new read-only asset contract is `IPAM_SYNTHETIC_FEED_DIR`, pointing to the immutable rich v1 directory containing policy and eight observation envelopes. The scheduler adapter reads only those named files. Missing/wrong assets fail visibly; no fallback to mutable database views or developer paths. Spencer packages assets once the candidate is pinned. This document is not permission to run or deploy it.
- Lead keeps global status, contracts, row accounting, reviews and main acceptance. Scheduling is a separate feature branch from the source-accepted Stage 3 checkpoint. No new user-owned task is created automatically.

## Feed interface

`build_cycle(index: int, baseline_envelopes: list[dict]) -> dict` is pure: no filesystem writes, database/network access, wall clock, random values or expected-outcome input. It must not mutate the caller's baseline inputs. Reject booleans, negative indices and invalid baseline shape visibly. The scheduler reads the immutable baseline files and passes their parsed envelopes; the function does not read latest imported evidence.

Return `feed_version="ipam-evolving-v1"`, `cycle_index`, deterministic `cycle_id`, `demo_clock_at`, and `envelopes`: one complete unchanged-policy reassertion plus four DHCP and four routing views. All use the existing strict envelope format and the same scenario instant. Index 0 is the reference baseline; the scheduler's first advancement consumes index 1. Scenario time is `2026-09-01T00:00:00.000Z + index * 6 hours`, irrespective of wall interval.

Reuse the existing rich logical source IDs (`synthetic-dhcp-*`, `synthetic-routing-*`, `synthetic-inventory-policy`). New content has immutable per-cycle source-run identity. Repeating an index yields identical data, identities and serialization input. Preserve entity IDs and unchanged interval facts; new interval identities derive from entity and absolute boundaries. Retain a truthful full rolling 30-day history. Never shift old observations merely to make graphs move.

Immediate scenario changes may show route withdrawal, intentional incomplete evidence, complete restoration and current occupancy growth/relief. Historical p95, completed-day forecast and 30-day conflicts need not change immediately. An intentional partial step is explicitly documented in feed metadata outside importer envelopes and yields visible partial/unknown results. Unexpected rejected records or malformed bundles fail the cycle. Expected answers remain outside runtime inputs.

## Two clocks and one atomic cycle

Wall time drives scheduling: default interval six hours, configurable in hours, saved enabled/disabled state and next due. Scenario time drives all eligibility/calculations and appears separately in UI. Enabling requires valid rich seed/assets and compatible source authority. Refuse mixed first-path/foreign competing sources before mutation; do not silently retire evidence or create a second authority. Initial schedule is off until explicitly enabled; Run now remains an explicit independent action on eligible data.

Use one timer in the existing single API process, under the existing exclusive app-data lifecycle. No OS cron, second service, queue, new dependency or missed-run backlog. Start only after readiness; cancel/join cleanly before releasing data access. Restart makes at most one overdue attempt, then schedules forward. Failure/busy uses a visible future retry time rather than a tight loop.

1. Build the complete deterministic bundle outside the write transaction. Capture the requested cycle and durable operation identity.
2. Acquire the same run lock used by explicit reconciliation. Inside `BEGIN IMMEDIATE`, recheck cursor, operation replay, current rich identity/source authority and configuration. A stale prepared bundle must not run as the next cycle.
3. Advance `app_meta.demo_clock_at`, invoke the existing importer directly for all nine envelopes, create the existing saved reconciliation run, sync exceptions, and persist cursor/run/audit/success status in the same transaction. The ordinary import clock equality check remains intact. New policy snapshot bounds equal the scenario clock; unchanged intended state and original seed envelope remain untouched.
4. Commit once. On fetch/import/calculation failure, roll back clock, imports, run and cursor together; record failure separately and report loss of that failure record visibly if necessary. A documented valid partial scenario commits with partial status. Previous results retain their original clock and provenance.

Manual Run now accepts a stable idempotency key, retains it across ambiguous UI responses, and returns the committed result on retry. A replay neither advances cursor nor creates another run/audit. Timer/manual/ordinary-run races share the same in-flight guard; a busy response is not success. This is one atomic scheduled acquisition operation. Ordinary manual import remains a separately committed receipt; the broader optional RFP-043 callback stays deferred.

Persist/expose enabled state, interval, next wall due, last attempt, last success, last error/partial outcome, feed/cycle identity, scenario clock and saved run ID. Configuration and explicit actions use existing fixed actor permission/audit conventions. New inputs do not increment intended allocation tokens, but approval still rechecks current DHCP evidence at the current scenario clock.

## Remaining evidence

No producer, scheduler, migration, timer, restart, replay, browser or packaging behavior has been executed or accepted. Required later evidence is one advancing successful cycle, unchanged retry, deliberate partial/unknown step, failed-cycle rollback, overlapping manual/timer attempt, restart without catch-up burst, matching saved run/detail/export clocks, and portable fixture availability. Preserve denominator 111; scheduled synthetic acquisition does not establish live discovery or satisfy every clause of RFP-061/068/043.
