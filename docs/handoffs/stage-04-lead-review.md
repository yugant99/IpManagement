# Stage 4 independent source review

Persistent lead: `01a0b845-6c8d-7021-a5c9-15e673db07c9`. Date: 2026-09-19.

## Candidate and disposition

Candidate: [PR #25](https://github.com/yugant99/IpManagement/pull/25), `codex/stage-4-scheduler-integration`, publication **`42cba9089f30aca47771849dd6f6541c50a60d65`**. Source/API checkpoint `217a1bc03c87ea832785ec75e0f908755871652a`; scheduler code checkpoint `c3c7aed154babeea54690cd91802c094f9252106`. Isolated worker: `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-4`, task `01a0bacd-a541-73e1-8a06-f674dd4a1bcd`.

**Accepted Stage 4 source checkpoint: `54f8f8168108733d40d842263218f16b33df5868`.** Three independent bounded lead reviews covered scheduler transactions/lifecycle, feed compatibility/provenance, and UI/API retry wiring. The lead read the source and routed two concrete findings to the existing Stage 4 owner. The owner corrected both; independent lead reviewers closed each by reading the exact correction delta. The lead read the complete two-file source delta and confirmed the pushed PR head. This is source acceptance only; runtime evidence remains pending.

| Finding at `42cba908` | Concrete consequence | Owner / disposition |
|---|---|---|
| P2, confidence 9/10: `scheduler.py:275–276,291–292` applies a process-local retry deadline without its configuration identity | A due timer using six hours can lose the lock to a new one-hour configuration. After that configuration clears retry state, the old timer failure installs a six-hour guard, delaying the new schedule | Fixed at `ed00d1b8b9d83a864dbbf2487b1a45a9efb5a2f2`: guard is an atomic tuple of config version, due identity and deadline; only a matching guard applies. Independent source closeout also checked failure-record-loss backoff |
| P2, confidence 8/10: `feed_adapter.py:162–180` checks seed IDs/scopes against pinned policy, but compares original bounds/perimeter only with the saved seed | Rich setup permits changes to appended records. A changed original rich subnet can retain IDs and pass eligibility while the fixed feed targets different bounds | Fixed at `f0f4b82feae49c3083c4fdeb0c18b315b89c8761`, merged at `54f8f816`: independent pins for four scopes and sixty original prefix structures check both seed and current inventory. Reviewer compared every tuple with original fixture source; metadata and later additions remain allowed |

UI/API source review found no actionable issue in retained manual key/payload, response validation, navigation/reload retention, sequential polling, actor/configuration handling or clock/status wiring. No other actionable finding arose in the bounded scheduler and adapter reviews. These statements do not establish runtime behavior.

The adapter correction changes no fixture and adds no tenth runtime asset. The exact nine input files and Spencer's existing packaging interface remain unchanged. The accepted source delta changes only `scheduler.py` and `feed_adapter.py`. Final publication **`117d05295473cf25d362adb320e6fef26ecdd74c`** changes only `STAGE4_API.md` and the worker report; the lead read that delta and confirmed the remote PR head. Use this publication as the Stage 5 pickup point while preserving the separate accepted code identity.

## Actual dependencies

PR #25 remains OPEN/draft against Stage 3. It inherits source-accepted Stage 3 publication `63287e0ff281b678abbd8809ca9160739de8c537`, accepted producer `3218daade8de3fe61bd6df36da431411add4a3ad`, and lead docs through main `de535d1f8aca6b39b87a5debf01951e54dde88f0`.

- Schedule UI #23 at `d8f1c1a79475f2f6bdb5905a233a43bd139b212e` and core wording #22 at `16c316d0afa5c22bccb5268eba5db113ada1680a` are GitHub **MERGED into Stage 4**, not main. Adapter branch `cace14765a6c8f017ab214d03370129c0211bf0a` is integrated without a separate PR.
- Stage 3 components #12/#13/#14/#16/#17 are merged into Stage 3. Foundation #5, frozen data #7, Stage 2 #8, original state #10, Stage 3 #18 and producer #19 remain open despite source inheritance in the candidate. Main contains documentation only.
- Delivery-method #9 at `c3e45fa43a1e9f59e6c9af298b14e2c0857ebaa2` remains separate, review pending and **NO MERGE**.
- Spencer has no registered package checkpoint. Local application acceptance can precede packaging; portable/recipient acceptance cannot be inferred from it. `PART6_READY=no`.

## Next gates and permissions

Both owner corrections are closed in source. [Stage 5's approved handoff](stage-05-kickoff.md) permits isolated source/evidence preparation on this exact candidate. Actual local E2E remains separately gated on the user's affirmative scope. No broad repeat audit or new feature lane is required.

The data-owner task is gathering an explicit user decision on isolated local E2E: locked dependencies if needed, UI build, localhost service and browser/API interaction on disposable data, scheduled/manual acquisition, receipts/replay/rollback, findings/exports/allocation, and stopped-service backup/restore/restart. **That question is pending, not authorization.** Docker, cloud, deployment and existing user databases are outside that proposed local gate. No duplicate acceptance worker is assigned.

The lead owns application main integration after accepted evidence and dependency review. Stage 5 keeps existing owners for concrete application, core-state, data and packaging fixes. Local E2E and Spencer's recipient package are separate acceptance gates; neither requires inventing new features.

No tests, smoke/type/parser/compile/import checks, builds, generator runs, installs, application/API/browser/state/migration/container/VM or infrastructure commands were run in this lead review. No application PR was merged into main. All runtime behavior remains unverified, including inherited Stage 3/state behavior. Denominator **111**; source review adds no demonstrated rows.
