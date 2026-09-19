# Rich-seed CLI handoff

**READY FOR PROJECT-LEAD REVIEW — Rich-seed CLI.** Source implemented and reviewed; runtime behavior remains unverified. No merge or release acceptance is claimed.

## Pickup and exact dependency

| Field | State |
|---|---|
| Repository | `https://github.com/yugant99/IpManagement` |
| Worker | `Foundation 1`, task `01a0b8ae-bd65-7331-b548-da5dca1e0d5e` |
| Worktree | `/Users/yuganthareshsoni/Downloads/Ip_inventory-rich-seed-cli` |
| Branch | `codex/part-1-rich-seed-cli` |
| Code checkpoint | `0b64a3be26f666dd31af483a3b887cb0aa663b07` |
| Exact lead-approved base | `1d67cc45ffcf72409aad37555b996ccfefe882b6`, rich-seed helper on `codex/stage-3-main-capabilities` |
| PR target | `codex/stage-3-main-capabilities`; dependent, no merge by this worker |
| Inherited dependencies | Stage 2 [PR #8](https://github.com/yugant99/IpManagement/pull/8) at `8a1a122737618748c58c5a8fc31b58a3b5f6f37e`, rich fixtures [PR #7](https://github.com/yugant99/IpManagement/pull/7) at `907f6e7bf32f23f36d270da49c3177b015c8bfae`, lead documents at `1cde8dd7df0e3e0cf3a55b3d771843a1e4dd9a25` |
| Separate state lane | [PR #10](https://github.com/yugant99/IpManagement/pull/10), unchanged at `0e139a85b445f7d07968c855e770c525c5e4d91c` |

The final publication SHA and PR URL are recorded in the worker response and PR description. This report follows the code checkpoint in a documentation commit. Inspect current refs before integration; do not reset another worker's checkout.

Stage 3 requested the reserved CLI wiring after publishing `seed_rich(directory, inventory_path)`. The persistent lead explicitly approved the exact dependency and these two owned files before CLI edits: `backend/ipam_demo/__main__.py` and this handoff. No seed/store/schema/fixture/lock/UI/packaging/global documentation edits were made. This is setup support for the existing Part 1 inventory and Part 2 synthetic-data work (G01–G03/G05), not additional demonstrated questionnaire coverage.

## Authored behavior

The following commands describe the authored interface; none was executed in this task. From the repository root, with the backend installed, an existing writable `IPAM_DATA_DIR`, and the service stopped:

```sh
python -m ipam_demo seed --scenario baseline
python -m ipam_demo seed --scenario rich --inventory fixtures/v1/inventory.json
```

Choose one setup mode for a fresh/uninitialized store. `--scenario` is still required; there is no automatic/default rich setup. Baseline continues to use the packaged baseline helper. Rich calls the existing Stage 3 helper with the explicit file path; the CLI does not locate, generate or alter fixtures.

Rich without a nonempty `--inventory` value and baseline with any `--inventory` value fail before `data_directory()` or a seed helper is called. They use the existing JSON error envelope on stderr with code `INVALID_SEED_OPTIONS`, status 422, and exit 1. Missing required parser arguments and unsupported scenarios retain argparse's normal error/exit behavior. Existing serve, migrate, and common error handling are unchanged.

The inherited helper enforces the exclusive application lock, rejects initialized data, validates the rich source identity, original baseline records/IDs and fixed clock, and applies the 10 MiB / 10,000-record bounds. Inventory insertion uses its existing transaction. Those mechanisms were read, not executed or reimplemented here. No evidence import or reconciliation is triggered by this CLI wiring.

The rich fixture retains envelope `scenario: baseline` for its existing format contract. The helper's success payload distinguishes it with `setup_mode: rich`, `source_id: synthetic-inventory-rich`, and `source_run_id: rich-v1-inventory`. The CLI prints that payload unchanged. Do not interpret the envelope scenario alone as the selected setup mode.

## Evidence and limits

Observed: the exact base/owned Git diff, a separate worktree, source-level helper/call-site alignment, and an independent bounded CLI source review with no actionable findings. Baseline flag rejection and rich required-path validation occur before data access in the authored control flow.

Not run: application installation, CLI/seed/state commands, Python imports or compilation, tests, syntax/type checks, builds, smoke/browser checks, or infrastructure operations. No tests were added. Actual parser exits/error JSON, file failures, locking, initialized-store refusal, transaction behavior, resulting inventory and downstream calculations remain unverified. No application database was created by this task; `PART6_READY` is unchanged.

## Integration instructions

1. Review this narrow PR against `codex/stage-3-main-capabilities`; its required helper was published at the exact base above. Keep the CLI commit and this handoff together when the lead coordinates integration. The worker does not merge.
2. PR #10 is a separate, unmerged dependency and is not included here. When the lead combines it with Stage 3, preserve both its `state_ops` import/parser/dispatch and this rich seed import/parser/dispatch. Do not replace the entire CLI with either branch's copy. Preserve migrate and serve behavior.
3. Stage 3 subsequently published schema v3 at `f241b0752c0e2aa46b3cbde7a67f30c6f5e6541e`. That commit is not this feature's base. Source review found that PR #10's v1/current validator would reject v2 stores after the version bump. The state and schema owners have coordinated a separate compatibility proposal; no such fix is included or claimed here. Integrating the state lane with v3 requires resolving that issue explicitly.
4. Spencer's packaging and operator files remain his responsibility. The explicit inventory file must be available at the chosen runtime path; this CLI does not bundle the rich fixture or alter packaging. Lead/runtime authorization is still required for execution evidence.

Next owner: the persistent lead for source review/integration and the Stage 3 owner for the resulting application checkpoint. This worker remains available for a separately approved schema/state compatibility change. No new implementation stage is started by this handoff.
