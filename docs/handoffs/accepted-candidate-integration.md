# Accepted candidate integration and readiness

Main Lead 2.0, task `01a0bb80-cf0d-7f60-8e46-1e825f42d276`, 2026-09-19. This record coordinates the existing accepted candidate; it creates no new stage, feature scope or runtime grant.

## Readiness map

| Area | Current evidence | Remaining gate / owner |
|---|---|---|
| Local application | Accepted pickup `117d05295473cf25d362adb320e6fef26ecdd74c`; Stage 5 report `fe50cd6828016a25fee9086f499e2e865b4a16e4`: 14 passes, two partial, zero observed application defects | Retain all bounded local/synthetic limits; existing workers own scoped fixes |
| Main integration | Prepared history-preserving merge `12384916152be635bea1087540a7cb7d59898360` on registered-lead main `b6616a72d72d2b55659da796944e0a6fda46db7f`; [PR #34](https://github.com/yugant99/IpManagement/pull/34) | Lead's bounded review and main merge; no code substitution or new runtime run |
| Questionnaire | 111-row denominator; 51 unique candidate IDs in the worker ledger | Lead's final row adjudication; candidate IDs are not completed requirements |
| Customer phases | [Phase coverage](../PHASE_COVERAGE.md) retained alongside questionnaire | Customer Phase 1 assessment and Phase 2 rollout/adoption outcomes remain incomplete |
| Delivery-method document | PR #9 exact `c3e45fa43a1e9f59e6c9af298b14e2c0857ebaa2` is separate | NO MERGE; proposed documentary support only |
| Core packaging inputs | Runtime module/locks/UI build path, state CLI, feed module/assets and local prerequisite evidence available | Spencer packages this candidate and reports exact artifacts |
| Portable delivery | No registered package checkpoint, target-host or recipient result | `PART6_READY=no`; Spencer owns package/operator handoff, lead owns acceptance |

## Lineage and review boundary

Refreshed GitHub before integration. All eight heads below are ancestors of `fe50cd6`; none were in transfer main `4884481`. One merge incorporates their already-reviewed combined state. Do not merge the historical stack separately or replace newer global docs with old worker copies.

| PR | Exact inherited head |
|---|---|
| #5 | `c6131c38a460c13c3a189ee64a530042b2a2bf0f` |
| #7 | `907f6e7bf32f23f36d270da49c3177b015c8bfae` |
| #8 | `8a1a122737618748c58c5a8fc31b58a3b5f6f37e` |
| #10 | `0e139a85b445f7d07968c855e770c525c5e4d91c` |
| #18 | `63287e0ff281b678abbd8809ca9160739de8c537` |
| #19 | `3218daade8de3fe61bd6df36da431411add4a3ad` |
| #25 | `117d05295473cf25d362adb320e6fef26ecdd74c` |
| #27 | `fe50cd6828016a25fee9086f499e2e865b4a16e4` |

The merge had no conflicts. Git identity comparison against the tested pickup found no change in backend, frontend, fixtures, build metadata or locks. Matching objects:

| Path | Git object |
|---|---|
| `backend` | `49168e853b1e777231c2f91469a0fa48e787c27e` |
| `frontend` | `3ca8fb81cde1a35496f82bd0fbe0f6da8703029a` |
| `fixtures` | `f7ae0533b3efa9fce618def206561a60d8d355ad` |
| `pyproject.toml` | `931397380ed4f4cfa46e1c7737b0bcb5706faad8` |
| `uv.lock` | `56671dad30939e0e1df3fdf0e44105316f15a3d1` |
| `.python-version` | `3b2cfc0e6904f4f3bfefaadc28451ba1f2818332` |
| `.gitignore` | `90bcd360ddab68bac0a762b0d065252d5f3b4dd5` |

The independent bounded review examined ancestry, main/candidate differences and registration. It found no source-integration blocker and identified stale pickup wording for correction. This is identity/source review, not a repeated runtime acceptance run. Historical worker reports retain their original identities and pre-review wording; current lead acceptance supersedes them.

PR #9's head is not an ancestor of the integration and its two unique files are absent. Its no-merge instruction is unchanged. Worker branches and worktrees were not switched or edited. Registration was merged through PR #33; retained owners were notified of the routing change only.

## Preserved evidence limits

- **S5-09 partial:** timer contention used the real ordinary-run guard held by a harness; active ordinary reconciliation was unrun. Stop was direct scheduler/lifespan behavior, not an OS signal during acquisition.
- **S5-15 partial:** asset/authority refusals used fresh initial states; preservation after prior success and first-path-specific refusal remain unrun.
- Representative v3 migration only; v1/v2, reset and enabled-snapshot restore remain unrun. Disabled snapshot round trip and controlled overdue restart are distinct observations.
- Workflow response-loss recovery was in the mounted UI. Schedule recovery separately covered navigation/reload. Exception writes used API followed by UI observation. CSV content proof was unfiltered/default-column API capture; the browser showed the download request.
- Controlled time is not elapsed-hour endurance. No Docker/Compose/Linux/recipient, live-network, carrier-scale, HA, production or customer-migration proof.

These limits do not block integration of the unchanged, locally accepted synthetic demo. They do prevent broader acceptance claims. No failing application behavior was observed that requires an owner fix. Reuse passing evidence unless a relevant change/failure invalidates it.

## Spencer's current candidate and remaining evidence

This lead-owned addendum controls current candidate/routing where the older Part 6 pickup still says no application exists or names the old lead. Spencer retains all Part 6 files; this record does not implement his package or operator instructions.

Use the application pickup `117d05295473cf25d362adb320e6fef26ecdd74c` and the integrated lineage in PR #34. Inspect current main/PR status before branching; coordinate any existing preparation based on old Stage 2 instead of overwriting it. Core supplies `ipam_demo`, the committed locks, compiled-UI build path, schema-v4 state CLI, and the normal packaged `ipam_synthetic_feed` module. Package immutable `fixtures/v1` assets and set `IPAM_SYNTHETIC_FEED_DIR` with `IPAM_STATIC_DIR` and persistent `IPAM_DATA_DIR` under [contracts](../CONTRACTS.md) and [scheduling](../SCHEDULING_CONTRACT.md).

Keep core prerequisites and portable acceptance separate. Earlier `PART6_READY` wording meant core inputs; the transferred controlling flag remains **no** until the lead reviews package/recipient evidence. Native local acceptance does not prove the package.

When available, the published handoff needs exact base/package SHA and PR, owned files, target platform, locked build/static/feed inclusion, volume/data/health/state-command instructions, dependency/license facts, and actual outcomes with limits. Target startup must serve the compiled UI and API; persistence evidence must retain populated allocations and audit, including backup/restore/restart under the declared contract. Record recipient pickup and acknowledgement separately from the author's local result. Reset remains unrun and cannot be reported as passed.

Read-only package review can begin from the published files. No Docker/image pull, VM, deployment, spending or new target execution is authorized by this record. Before any such execution, prepare the concrete target, writable/mounted paths, persistence, cleanup and evidence scope for the user's decision. Do not borrow stopped acceptance stores with enabled schedules or modify existing user stores. All retained Stage 5 artifacts remain preserved at the recorded evidence root.
