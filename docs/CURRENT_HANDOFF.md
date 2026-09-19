# Current implementation-chat handoff

**ACTIVE — Stage 3: main capabilities**

PR #7 and Stage 2 PR #8 are accepted **unmerged source checkpoints** after three bounded independent reviews. No actionable defects were found in the reviewed surfaces. Runtime acceptance and questionnaire demonstration remain pending. See the [lead review](handoffs/stage-02-lead-review.md).

Stage 3 has started in task `01a0b8f0-7036-74d1-81c1-e388d17b4cf4` under the [approved kickoff](handoffs/stage-03-kickoff.md). Do not create another Stage 3 worker. Its isolated worktree is `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-3`, branch `codex/stage-3-main-capabilities`. Pushed dependency integration `5578431c85ffa18071d6262d08a49a251b072afd` combines the approved inputs below and lead docs `1cde8dd7df0e3e0cf3a55b3d771843a1e4dd9a25`. Keep earlier workers for assigned fixes and this original task as persistent lead.

Intermediate source `01550ab8b84936e289b4bbb74dfbfce9d6272940` publishes schema v3, the rich seed helper, API wiring/interface documentation and shared migratable-version policy. Dependent module integration remains pending; this is not an accepted Stage 3 or runnable candidate. Rich-seed CLI PR #12 at `d7b1fd580b88f875883dbde975c9504ead58a6a9` passed bounded independent source review and remains unmerged/runtime-unverified. See [review and exact state-compatibility pickup](handoffs/rich-seed-cli-lead-review.md).

## Exact dependencies

| Dependency | Pushed checkpoint | State |
|---|---|---|
| Foundation, PR #5 | `c6131c38a460c13c3a189ee64a530042b2a2bf0f` | Draft, unmerged; inherited by Stage 2 |
| Stage 2, PR #8 | `8a1a122737618748c58c5a8fc31b58a3b5f6f37e` | Draft, unmerged; Stage 3 application base |
| Fixtures, PR #7 | `907f6e7bf32f23f36d270da49c3177b015c8bfae` | Open, unmerged; separate data dependency |

Main contains documentation only. Read current lead documents there before using an older application branch. The lead explicitly permits combining these exact dependencies and current lead documentation on the isolated Stage 3 feature integration branch, preserving commits. This does not authorize application PR merges into main or substituting later application commits.

## Parallel owners

All registered tasks use host `local`. Titles may change; task IDs identify owners.

| Role | Task ID | Reserved scope |
|---|---|---|
| Persistent lead | `01a0b845-6c8d-7021-a5c9-15e673db07c9` | Global contracts/status, acceptance, main integration |
| Stage 3 implementation | `01a0b8f0-7036-74d1-81c1-e388d17b4cf4` | Assigned application modules; coordinator owns store/schema/app/common UI |
| Foundation 1 / core state commands | `01a0b8ae-bd65-7331-b548-da5dca1e0d5e` | `state_ops.py`, `__main__.py`, state-command docs; PR #10 awaiting lead review |
| Implement Stage 2 first path | `01a0b8c2-f283-7cf1-9128-85e9164f5fe9` | Assigned Stage 2 fixes |
| Overseer / synthetic data | `01a0b8b9-82fb-7a11-bc50-ec3a5b234729` | Fixtures and data docs |
| Create delivery-method documentation | `01a0b8db-76df-7511-b024-9d3deb589074` | Delivery-method docs; PR #9 awaiting review, no merge |
| Spencer / Part 6 | External worker not registered | Packaging, operator/Part 6 docs |

Stage 3 owns assigned application/import/calculation/rule/inventory/workflow/UI work. One Stage 3 coordinator owns shared schema/store/API/UI integration. Full reserved paths and seed/CLI coordination are in the approved kickoff.

No tests, builds, runtime, browser or infrastructure commands are authorized by this handoff. `PART6_READY=no`; no portable release is accepted. Preserve the 111-row denominator and partial/documentary limits. This lead owns acceptance and the eventual Stage 4 prompt.
