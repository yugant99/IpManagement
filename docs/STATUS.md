# Current project status

## Authorization and evidence

- Persistent lead remains task `01a0b845-6c8d-7021-a5c9-15e673db07c9`, regardless of its sidebar title.
- Stage 3 PR #18 is accepted as a **source checkpoint at `009e80197ab610e5a365d1e3dd4462588754d646`**, after three independent reviews and owner fixes for three findings. No runtime/browser/import/calculation/state/persistence result is accepted. See [Stage 3 lead review](handoffs/stage-03-lead-review.md).
- User scope change: evolving synthetic feed, **every six hours configurable, with manual Run now**. RFP-068 is now required. Follow [SCHEDULING_CONTRACT.md](SCHEDULING_CONTRACT.md); original fixtures stay unchanged. Producer PR #19 at `3218daade8de3fe61bd6df36da431411add4a3ad` is [source accepted](handoffs/evolving-feed-lead-review.md), unmerged as a GitHub PR and unexecuted. Stage 4 is now active in task `01a0bacd-a541-73e1-8a06-f674dd4a1bcd`; do not create a duplicate.
- No tests, builds, smoke/type/parser/import checks, generators, installs, runtime/browser/state/migration/container/VM or infrastructure commands are authorized by this checkpoint. Source/Git/document inspection is distinct from application execution. Application main integration still requires evidence.
- No cloud spending, public exposure, external submission or provider commitment is granted. Status records decisions; latest user instructions govern. Private attachments and local assessment stay outside Git.

## Integration and task registry

Repository: `yugant99/IpManagement`. Main contains documentation only. All registered tasks use host `local`; titles do not reassign ownership.

| Owner / task | Branch / checkpoint / PR | Actual state |
|---|---|---|
| Persistent lead, Synthetic data builder, `01a0b845-6c8d-7021-a5c9-15e673db07c9` | Lead documentation branches into main | Global status/contracts, acceptance and main integration stay here |
| Foundation 1, `01a0b8ae-bd65-7331-b548-da5dca1e0d5e` | `codex/part-1-foundation`, `c6131c38a460c13c3a189ee64a530042b2a2bf0f`, [#5](https://github.com/yugant99/IpManagement/pull/5) | Source reviewed; open/draft, inherited by Stage 2/3, outside main |
| Implement Stage 2 first path, `01a0b8c2-f283-7cf1-9128-85e9164f5fe9` | `codex/part-2-first-path`, `8a1a122737618748c58c5a8fc31b58a3b5f6f37e`, [#8](https://github.com/yugant99/IpManagement/pull/8) | Source accepted; open/draft, inherited by Stage 3; retained for assigned fixes |
| Overseer / data, `01a0b8b9-82fb-7a11-bc50-ec3a5b234729` | Frozen data `907f6e7bf32f23f36d270da49c3177b015c8bfae`, [#7](https://github.com/yugant99/IpManagement/pull/7); evolving `codex/part-2-evolving-feed`, `3218daade8de3fe61bd6df36da431411add4a3ad`, [#19](https://github.com/yugant99/IpManagement/pull/19) | #7 source accepted/open, inherited by Stage 3; #19 source accepted/open/draft against Stage 3, unexecuted, retained data owner |
| Foundation 1 / original state, same core task | `0e139a85b445f7d07968c855e770c525c5e4d91c`, [#10](https://github.com/yugant99/IpManagement/pull/10) | Open/draft, inherited through corrected #16; do not use old selector unchanged with schema v3 |
| Foundation 1 / rich CLI, same core task | `d7b1fd580b88f875883dbde975c9504ead58a6a9`, [#12](https://github.com/yugant99/IpManagement/pull/12) | Source accepted; GitHub MERGED into Stage 3 at `32d751fac381aef8bd53dcfdaa1f27639a64dc07`, outside main |
| Foundation 1 / state compatibility, same core task | `e6029d855abf13581b95fda20ade52f5a6c5792e`, [#16](https://github.com/yugant99/IpManagement/pull/16) | Source accepted including inherited state operations; MERGED into Stage 3 at `75a2e1395dd7a47bd40b2aa7343f8eb0f636b6f2`, runtime unverified |
| Stage 3, `01a0b8f0-7036-74d1-81c1-e388d17b4cf4` | `codex/stage-3-main-capabilities`, code `009e80197ab610e5a365d1e3dd4462588754d646`, report publication `63287e0ff281b678abbd8809ca9160739de8c537`, [#18](https://github.com/yugant99/IpManagement/pull/18) | Source accepted; open/draft against Stage 2; report-only delta read, retained for fixes |
| Stage 3 feature lanes | Inventory #13 `95a4efbc445adabf649df6439108a12d1232e4ff`; workflow #14 `b14f8ebd70b278fe35b3a18482802a657ea87950`; evidence #17 `170718dd931503c95e0f172b4ec9978250f55107` | GitHub MERGED into Stage 3, not main; corrections included in accepted #18 code |
| Create delivery-method documentation, `01a0b8db-76df-7511-b024-9d3deb589074` | `codex/delivery-method`, `c3e45fa43a1e9f59e6c9af298b14e2c0857ebaa2`, [#9](https://github.com/yugant99/IpManagement/pull/9) | Separate documentary checkpoint; lead review pending; user's **no-merge** restriction retained |
| Stage 4 scheduler/integration, `01a0bacd-a541-73e1-8a06-f674dd4a1bcd` | `codex/stage-4-scheduler-integration`, isolated `Ip_inventory-stage-4`; inspected local dependency integration `ef4158536f437710677440eb973a5fe242be9962` | Active under [approved kickoff](handoffs/stage-04-kickoff.md); exact #18 publication, #19 feed and lead docs combined locally. No pushed Stage 4 checkpoint/PR observed at registration; no Stage 4 acceptance |
| Spencer / Part 6 | Approved `codex/part-6-container-startup`, preparation base Stage 2 `8a1a122737618748c58c5a8fc31b58a3b5f6f37e` | External task/PR/package checkpoint not registered. Updated feed asset contract available; no inference that work has started |

Correction: normal feature-branch Git merges caused GitHub to mark #12/#13/#14/#16/#17 merged into their target Stage 3 branch. The earlier lead claim that these PRs would stay open was incorrect. Main is still documentation only. PRs #5/#7/#8/#10/#18 remain open; inheritance in a candidate is different from their GitHub PR state and from runtime acceptance.

See [core reviews](handoffs/rich-seed-cli-lead-review.md) and [Stage 2/data review](handoffs/stage-02-lead-review.md). Shared CLI conflicts were resolved by core; integrated CLI source retains seed baseline/rich, serve, migrate, backup, restore and reset. None was executed.

Stage 4's inspected source lineage is #18 publication `63287e0ff281b678abbd8809ca9160739de8c537` plus exact #19 `3218daade8de3fe61bd6df36da431411add4a3ad`, combined at `a55d6a31fb3e4666445a5bd2ecfbd4173dda38db`, then published lead docs `d1551a0ac1c1bc5ef0c3125827be8d200ce59ab5` at `ef4158536f437710677440eb973a5fe242be9962`. These are local Git commits read by the lead, not claimed pushed scheduler implementation or runtime evidence.

## Ownership

- Lead: global instructions/status/handoffs, shared contract decisions, questionnaire evidence and main acceptance.
- Stage 3: retained for assigned existing application defects; no automatic Stage 4 continuation. Do not race new shared-file edits with the registered Stage 4 worker.
- Stage 4 task `01a0bacd-a541-73e1-8a06-f674dd4a1bcd`: scheduler/feed adapter/status UI, minimal app/store/schema/common UI integration and wheel package inclusion; source integration/freeze record. Coordinator retains shared files; bounded agents use disjoint adapter/UI modules and isolated worktrees. Coordinate new schema policy with core. Follow the exact [kickoff](handoffs/stage-04-kickoff.md).
- Core: `backend/ipam_demo/state_ops.py`, `backend/ipam_demo/__main__.py`, `docs/STATE_OPERATIONS.md` and dedicated core handoffs. State-command correctness, stopped-service locking and explicit migration remain here.
- Data: `fixtures/`, `docs/SYNTHETIC_DATA.md`, `docs/handoffs/part-2-synthetic-data.md`. New pure package stays under `fixtures/evolving/ipam_synthetic_feed/`; original v1 clock/IDs/files remain unchanged. Expected answers are comparison-only.
- Delivery method: `docs/DELIVERY_METHOD.md`, `docs/handoffs/delivery-method.md`; proposed documentary support for 083/086/088/105, not demonstrated operations or provider promises.
- Spencer: `Dockerfile`, `compose.yaml`, `.dockerignore`, `scripts/ops/`, `docs/RUNNING.md`, `docs/parts/06-portability.md`, `docs/handoffs/part-6.md`. Approximately 6–8 hours, no presentation assignment or core state correctness. No build/pull/container/VM/deployment permission.

## Readiness

| Gate | Accepted state | Missing |
|---|---|---|
| Foundation / first path / frozen data | Exact source checkpoints reviewed and inherited by Stage 3 | Actual setup/import/rule/browser/migration evidence; main integration |
| Main capabilities | Stage 3 source accepted at `009e801` after three fixes | Actual calculations, UI/export, inventory, allocation/audit and team handoff evidence |
| Rich CLI and core state | Corrected source integrated in Stage 3 | Actual setup/refusal, backup/restore/reset/restart, migration/preservation/failure outcomes |
| Evolving scheduled acquisition | Required contract and PR #19 producer source accepted | Scheduler source integration and all actual callable/feed/cycle/replay/restart evidence |
| Delivery method | Separate PR #9 received | Lead review; no merge |
| PART6_READY | **No** | Accepted prerequisite/runtime/persistence evidence and package checkpoint |
| Portable release | Not accepted | Integrated candidate, built UI, startup, persistence and recipient evidence |
| Questionnaire | **0 rows demonstrated/substantiated at this lead checkpoint** | Actual per-row evidence, partial clauses and remaining gaps |

Denominator **111**. Historical 65/67/68 bundles are planning arithmetic, not fully satisfied-row counts. RFP-043's general import callback stays deferred; RFP-081 has source wiring without observed handoff; RFP-068 is now required. New scheduling does not earn live discovery, scale or provider evidence.

The read-only heartbeat inspects meaningful progress every 30 minutes through Monday morning, 2026-09-21; the app automation is the schedule source. It does not implement, test, merge or assign work. Preserve the original weekend budget and integration reserve: freeze unrelated additions. Next: [CURRENT_HANDOFF.md](CURRENT_HANDOFF.md).
