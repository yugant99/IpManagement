# Current project status

## Authorization and evidence

- Persistent lead remains task `01a0b845-6c8d-7021-a5c9-15e673db07c9`, regardless of its sidebar title.
- Stage 3 PR #18 is accepted as a **source checkpoint at `009e80197ab610e5a365d1e3dd4462588754d646`**, after three independent reviews and owner fixes for three findings. No runtime/browser/import/calculation/state/persistence result is accepted. See [Stage 3 lead review](handoffs/stage-03-lead-review.md).
- User scope change: evolving synthetic feed, **every six hours configurable, with manual Run now**. RFP-068 is now required. Follow [SCHEDULING_CONTRACT.md](SCHEDULING_CONTRACT.md); original fixtures stay unchanged. Producer PR #19 at `3218daade8de3fe61bd6df36da431411add4a3ad` is [source accepted](handoffs/evolving-feed-lead-review.md), unmerged as a GitHub PR and unexecuted. Stage 4 task `01a0bacd-a541-73e1-8a06-f674dd4a1bcd` is retained for assigned fixes; Stage 5 is the current acceptance lane.
- Stage 4 [PR #25](https://github.com/yugant99/IpManagement/pull/25) is **source accepted at `54f8f8168108733d40d842263218f16b33df5868`**, with reviewed API/report-only publication `117d05295473cf25d362adb320e6fef26ecdd74c`. Independent lead review found two issues at the initial `42cba908` candidate; the existing owner corrected both and independent delta reviews closed them. See [Stage 4 lead review](handoffs/stage-04-lead-review.md). Runtime acceptance remains pending.
- On 2026-09-19 the user explicitly authorized the prepared Stage 5 local checks: **“lets go man tun the tests man”**. [Execution scope](handoffs/stage-05-execution-authorization.md) covers locked local setup/build, browser/API checks, controlled disposable harnesses and backup/restore/migration on fresh acceptance data. This supersedes the earlier execution prohibition within that scope. Application main integration still requires actual evidence; cloud/VM/Docker execution remains excluded.
- No cloud spending, public exposure, external submission or provider commitment is granted. Status records decisions; latest user instructions govern. Private attachments and local assessment stay outside Git.

## Integration and task registry

Repository: `yugant99/IpManagement`. Main contains documentation only. All registered tasks use host `local`; titles do not reassign ownership.

| Owner / task | Branch / checkpoint / PR | Actual state |
|---|---|---|
| Persistent lead, Main Lead, `01a0b845-6c8d-7021-a5c9-15e673db07c9` | Lead documentation branches into main | Global status/contracts, acceptance and main integration stay here |
| Foundation 1, `01a0b8ae-bd65-7331-b548-da5dca1e0d5e` | `codex/part-1-foundation`, `c6131c38a460c13c3a189ee64a530042b2a2bf0f`, [#5](https://github.com/yugant99/IpManagement/pull/5) | Source reviewed; open/draft, inherited by Stage 2/3, outside main |
| Implement Stage 2 first path, `01a0b8c2-f283-7cf1-9128-85e9164f5fe9` | `codex/part-2-first-path`, `8a1a122737618748c58c5a8fc31b58a3b5f6f37e`, [#8](https://github.com/yugant99/IpManagement/pull/8) | Source accepted; open/draft, inherited by Stage 3; retained for assigned fixes |
| Overseer / data, `01a0b8b9-82fb-7a11-bc50-ec3a5b234729` | Frozen data `907f6e7bf32f23f36d270da49c3177b015c8bfae`, [#7](https://github.com/yugant99/IpManagement/pull/7); evolving `codex/part-2-evolving-feed`, `3218daade8de3fe61bd6df36da431411add4a3ad`, [#19](https://github.com/yugant99/IpManagement/pull/19) | #7 source accepted/open, inherited by Stage 3; #19 source accepted/open/draft against Stage 3, unexecuted, retained data owner |
| Foundation 1 / original state, same core task | `0e139a85b445f7d07968c855e770c525c5e4d91c`, [#10](https://github.com/yugant99/IpManagement/pull/10) | Open/draft, inherited through corrected #16; do not use old selector unchanged with schema v3 |
| Foundation 1 / rich CLI, same core task | `d7b1fd580b88f875883dbde975c9504ead58a6a9`, [#12](https://github.com/yugant99/IpManagement/pull/12) | Source accepted; GitHub MERGED into Stage 3 at `32d751fac381aef8bd53dcfdaa1f27639a64dc07`, outside main |
| Foundation 1 / state compatibility, same core task | `e6029d855abf13581b95fda20ade52f5a6c5792e`, [#16](https://github.com/yugant99/IpManagement/pull/16) | Source accepted including inherited state operations; MERGED into Stage 3 at `75a2e1395dd7a47bd40b2aa7343f8eb0f636b6f2`, runtime unverified |
| Foundation 1 / schema-v4 wording, same core task | `codex/part-1-state-schema4-docs`, `16c316d0afa5c22bccb5268eba5db113ada1680a`, [#22](https://github.com/yugant99/IpManagement/pull/22); exact base `16160806e91023a29eae501b824c6b43e5e56d87` | Source accepted and GitHub MERGED into Stage 4 at `ae0541185413554fad84bce75ece5f3dd051d6b4`. Only CLI help/state docs; no algorithm change or runtime acceptance |
| Stage 3, `01a0b8f0-7036-74d1-81c1-e388d17b4cf4` | `codex/stage-3-main-capabilities`, code `009e80197ab610e5a365d1e3dd4462588754d646`, report publication `63287e0ff281b678abbd8809ca9160739de8c537`, [#18](https://github.com/yugant99/IpManagement/pull/18) | Source accepted; open/draft against Stage 2; report-only delta read, retained for fixes |
| Stage 3 feature lanes | Inventory #13 `95a4efbc445adabf649df6439108a12d1232e4ff`; workflow #14 `b14f8ebd70b278fe35b3a18482802a657ea87950`; evidence #17 `170718dd931503c95e0f172b4ec9978250f55107` | GitHub MERGED into Stage 3, not main; corrections included in accepted #18 code |
| Create delivery-method documentation, `01a0b8db-76df-7511-b024-9d3deb589074` | `codex/delivery-method`, `c3e45fa43a1e9f59e6c9af298b14e2c0857ebaa2`, [#9](https://github.com/yugant99/IpManagement/pull/9) | Separate documentary checkpoint; lead review pending; user's **no-merge** restriction retained |
| Stage 4 scheduler/integration, `01a0bacd-a541-73e1-8a06-f674dd4a1bcd` | `codex/stage-4-scheduler-integration`, isolated `Ip_inventory-stage-4`; accepted code `54f8f8168108733d40d842263218f16b33df5868`, publication `117d05295473cf25d362adb320e6fef26ecdd74c`, [#25](https://github.com/yugant99/IpManagement/pull/25) | OPEN/draft against Stage 3. Source accepted after two owner fixes and independent delta closeout; retained for assigned fixes. No runtime acceptance |
| Stage 4 component lanes, coordinated by same task | Schedule UI #23 `d8f1c1a79475f2f6bdb5905a233a43bd139b212e`; adapter `cace14765a6c8f017ab214d03370129c0211bf0a` | #23 MERGED into Stage 4; adapter branch integrated without a separate PR. Original authors retained for assigned fixes |
| Stage 5, Execute Stage 5 acceptance handoff, `01a0baff-2143-7073-ad3d-4963a9cc0ca5` | `codex/stage-5-local-acceptance`, isolated `Ip_inventory-stage-5`; corrected preparation `7e37dde6ba18a08717b0ce56c4438522fc5f7008`, [#27](https://github.com/yugant99/IpManagement/pull/27) | OPEN/draft against Stage 4; preparation accepted. All 16 prepared scenarios now authorized for bounded local execution; results pending |
| Spencer / Part 6 | Approved `codex/part-6-container-startup`, preparation base Stage 2 `8a1a122737618748c58c5a8fc31b58a3b5f6f37e` | External task/PR/package checkpoint not registered. Updated feed asset contract available; no inference that work has started |

Correction: normal feature-branch Git merges caused GitHub to mark #12/#13/#14/#16/#17 merged into their target Stage 3 branch. The earlier lead claim that these PRs would stay open was incorrect. Main is still documentation only. PRs #5/#7/#8/#10/#18 remain open; inheritance in a candidate is different from their GitHub PR state and from runtime acceptance.

See [core reviews](handoffs/rich-seed-cli-lead-review.md) and [Stage 2/data review](handoffs/stage-02-lead-review.md). Shared CLI conflicts were resolved by core; integrated CLI source retains seed baseline/rich, serve, migrate, backup, restore and reset. None was executed.

Stage 4's inspected source lineage is #18 publication `63287e0ff281b678abbd8809ca9160739de8c537` plus exact #19 `3218daade8de3fe61bd6df36da431411add4a3ad`, combined at `a55d6a31fb3e4666445a5bd2ecfbd4173dda38db`. Initial publication `42cba908` includes schema v4, adapter, scheduler/UI, exact core #22 and lead docs through main `de535d1f8aca6b39b87a5debf01951e54dde88f0`. Timer fix `ed00d1b8b9d83a864dbbf2487b1a45a9efb5a2f2` and adapter fix `f0f4b82feae49c3083c4fdeb0c18b315b89c8761` combine at accepted code `54f8f816`. Publication `117d052` updates only API/report documentation; that delta was separately read. The adapter pin changes no fixtures and adds no runtime asset.

Exact PR #22 is now normally integrated into Stage 4; see [core review](handoffs/rich-seed-cli-lead-review.md). Its GitHub merge into that target is distinct from main integration. Core retains CLI/state ownership; Stage 4 retains schema/store/lifecycle/UI. No runtime evidence or demonstrated-row credit follows from this wording-only acceptance.

## Ownership

- Lead: global instructions/status/handoffs, shared contract decisions, questionnaire evidence and main acceptance.
- Stage 3: retained for assigned existing application defects; no automatic Stage 4 continuation. Do not race new shared-file edits with the registered Stage 4 worker.
- Stage 4 task `01a0bacd-a541-73e1-8a06-f674dd4a1bcd`: scheduler/feed adapter/status UI, minimal app/store/schema/common UI integration and wheel package inclusion; source integration/freeze record. Coordinator retains shared files; bounded agents use disjoint adapter/UI modules and isolated worktrees. Coordinate new schema policy with core. Follow the exact [kickoff](handoffs/stage-04-kickoff.md).
- Core: `backend/ipam_demo/state_ops.py`, `backend/ipam_demo/__main__.py`, `docs/STATE_OPERATIONS.md` and dedicated core handoffs. State-command correctness, stopped-service locking and explicit migration remain here.
- Stage 5 task `01a0baff-2143-7073-ad3d-4963a9cc0ca5`: `docs/handoffs/stage-05-report.md` and `docs/evidence/stage-05/`; acceptance preparation and later only explicitly authorized local observations. Existing owners retain application fixes. Continue in this task; do not create a duplicate or a new Stage 6.
- Data: `fixtures/`, `docs/SYNTHETIC_DATA.md`, `docs/handoffs/part-2-synthetic-data.md`. New pure package stays under `fixtures/evolving/ipam_synthetic_feed/`; original v1 clock/IDs/files remain unchanged. Expected answers are comparison-only.
- Delivery method: `docs/DELIVERY_METHOD.md`, `docs/handoffs/delivery-method.md`; proposed documentary support for 083/086/088/105, not demonstrated operations or provider promises.
- Spencer: `Dockerfile`, `compose.yaml`, `.dockerignore`, `scripts/ops/`, `docs/RUNNING.md`, `docs/parts/06-portability.md`, `docs/handoffs/part-6.md`. Approximately 6–8 hours, no presentation assignment or core state correctness. No build/pull/container/VM/deployment permission.

## Readiness

| Gate | Accepted state | Missing |
|---|---|---|
| Foundation / first path / frozen data | Exact source checkpoints reviewed and inherited by Stage 3 | Actual setup/import/rule/browser/migration evidence; main integration |
| Main capabilities | Stage 3 source accepted at `009e801` after three fixes | Actual calculations, UI/export, inventory, allocation/audit and team handoff evidence |
| Rich CLI and core state | Corrected source integrated in Stage 3 | Actual setup/refusal, backup/restore/reset/restart, migration/preservation/failure outcomes |
| Evolving scheduled acquisition | Producer #19 and corrected integrated Stage 4 source accepted | All actual callable/feed/cycle/replay/restart evidence; no execution yet |
| Local acceptance | Corrected preparation accepted at `7e37dde6`; bounded local execution authorized on 2026-09-19 | All 16 actual observations and lead evidence review; no results accepted yet |
| Delivery method | Separate PR #9 received | Lead review; no merge |
| PART6_READY | **No** | Accepted prerequisite/runtime/persistence evidence and package checkpoint |
| Portable release | Not accepted | Integrated candidate, built UI, startup, persistence and recipient evidence |
| Questionnaire | **0 rows demonstrated/substantiated at this lead checkpoint** | Actual per-row evidence, partial clauses and remaining gaps |

Denominator **111**. Historical 65/67/68 bundles are planning arithmetic, not fully satisfied-row counts. RFP-043's general import callback stays deferred; RFP-081 has source wiring without observed handoff; RFP-068 is now required. New scheduling does not earn live discovery, scale or provider evidence.

The read-only heartbeat inspects meaningful progress every 30 minutes through Monday morning, 2026-09-21; the app automation is the schedule source. It does not implement, test, merge or assign work. Preserve the original weekend budget and integration reserve: freeze unrelated additions. Next: [CURRENT_HANDOFF.md](CURRENT_HANDOFF.md).

The lead owns eventual application main merges after required evidence. [Stage 5's approved preparation handoff](handoffs/stage-05-kickoff.md) is now assigned to the registered existing worker above. Its initial preparation/report was `46c225defea8c933363354fe2d5bb6492ee67073`, corrected at accepted preparation **`7e37dde6ba18a08717b0ce56c4438522fc5f7008`**, on application pickup `117d052` plus published lead docs `07013a9` merged at `95f370713ecd2d983d76c15f9326cd9facac91b1`. These documentary changes do not alter the accepted application candidate or establish runtime evidence. PR #27 remains open; no merge into main is implied.

The bounded independent preparation review found one procedural issue: the primary populated restore comparison must first disable scheduling and capture null due state, otherwise a legitimate overdue startup cycle can change restored data before comparison. The owner corrected that sequence at `7e37dde6`; independent delta review closed it, and the lead read the full three-document correction and confirmed the pushed PR head. Enabled/overdue snapshot behavior remains a separate controlled case. Other inspected payloads/interfaces were consistent. No runtime result follows from this procedure review, and Stage 5 as a whole is not complete.

Local application E2E is separate from Spencer's portable package/recipient gate. The user answered the pending permission question directly in the persistent lead task on 2026-09-19. Continue the existing Stage 5 worker under the [recorded grant](handoffs/stage-05-execution-authorization.md); no repeated permission question or per-scenario confirmations. Runtime evidence remains pending, and the read-only heartbeat retains its original read-only limits.
