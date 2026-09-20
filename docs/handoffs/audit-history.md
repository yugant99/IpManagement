# F3: capacity history and inventory versions

Status: implemented and three focused local tests passed; independent review, shared UI warning integration and final rehearsal remain with the coordinating owners. Main Lead 2.0 retains acceptance and integration authority.

## Exact source and ownership

- Branch/worktree: `codex/audit-capacity-history`, `/Users/yuganthareshsoni/Downloads/Ip_inventory-audit-history`.
- Code checkpoint: `d9b0c1743bc0ba17a636aa2954eb456ece703014`.
- Starting main: `a279f32df0ac7d2147b580dbff36dd88772bdeb2`.
- Shared schema dependency merged normally: `7dc057c6b18b0b3f0c0425bb17d0b427c4908969`, from `codex/audit-shared-integration`. Stage 4 owns schema/store/seed compatibility and frontend integration.
- Inventory/history agent owns `calculations.py`, `tests/test_capacity_history.py` and this handoff. The coordinator authored the included `inventory_commands.py` changes and explicitly delegated their inclusion in this coherent F3 checkpoint.
- No fixture files, existing stores, historical acceptance artifacts or customer documents changed.

## Contract and resulting behavior

`pools.capacity_history_version` is an integer, defaults to `1` and must be at least `1`. This token describes support for historical geometry; existing pool, prefix and ledger versions retain their concurrency purpose. Calculations read the token directly from the pool table rather than depending on an HTTP response model.

- Metadata-only changes to owner, purpose, tags or custom fields continue to bump the existing concurrency versions and append audit, but leave the capacity-history token unchanged. Previously eligible p95/history/forecast therefore remain eligible when the source coverage remains valid.
- Child creation and supported empty-prefix bounds changes increment the capacity-history token for pools attached to the affected prefix or its ancestors. Unrelated pools are unaffected. These structural changes conservatively invalidate unsupported historical calculations.
- History eligibility requires token `1`, complete applicable source coverage and the existing sample/window rules. A changed token yields `capacity_history_changed` for unavailable historical p95/forecast. It cannot become eligible merely because later metadata changes or source runs arrive; recovering structural history needs a separately defined policy. This slice supplies no capacity timeline, cutoff or automatic reset.
- Current occupancy remains independently calculated. Complete current evidence of exhaustion remains `exhausted` even when historical geometry is unsupported. Positive observed lease overlap also remains usable; this change does not erase saved runs or turn every pool result into unknown.
- The coordinated migration initializes legacy pools conservatively: token `1` only when both old pool version and attached prefix version equal `1`; otherwise token `2`. A legacy pool with metadata-only past changes can therefore remain conservatively ineligible because this migration does not reconstruct its historical change semantics. Migration evidence belongs to the shared schema owner.

`edit_context` now supplies `history_impact: {metadata: [], structural: [{pool_id, name, cidr}]}`. Structural entries list affected attached/ancestor **DHCP IPv4** pools, so the UI can warn accurately without claiming static/IPv6 capacity history was previously available. The inventory command still conservatively maintains tokens on all affected pools. Stage 4 owns rendering the warning and the current/old-result distinction in the shared UI.

## Focused verification actually performed

The latest audit-follow-up request authorized focused local tests using disposable synthetic stores. The following command ran once after the exact coordinated schema merge and final code edits:

```sh
PYTHONPATH=backend PYTHONDONTWRITEBYTECODE=1 /Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12 -m unittest discover -s tests -p test_capacity_history.py -v
```

Observed: **3 tests passed**, `Ran 3 tests in 0.368s`, `OK`.

| Test | Observed assertions |
|---|---|
| Metadata preserves eligible history and concurrency guards | All four metadata categories changed through the actual editor command. Ordinary pool/prefix/ledger versions advanced; history tokens stayed `1`; history, p95 and forecast matched prior values. A stale inventory edit and an allocation review predating the edit were rejected. Old stored run JSON remained byte-identical. |
| Child creation invalidates ancestor history only | A new descendant incremented the two ancestor pool history tokens, exposed the matching warning pool IDs, retained current occupancy and positive lease overlap, and returned the explicit historical-unavailable reason. The isolated Lab pool remained eligible and old stored run JSON was unchanged. |
| Empty bounds change retains current exhaustion | Safe empty-child bounds editing invalidated ancestor historical p95. Complete current occupancy at 100% still yielded `exhausted` with zero days to full. A subsequent metadata edit did not reset the history token or restore unsupported history. |

Tests used fresh `TemporaryDirectory` stores with synthetic scoped controls derived in memory from the packaged baseline. The real seed, importer, inventory command, allocation guard and reconciler paths were exercised. Connections and temporary stores were cleaned up by the test harness. No existing demo or Stage 5 store was opened, no dependencies were installed, and no browser/build/infrastructure action was performed for this lane.

## Remaining owner actions

The coordinator should perform a bounded independent review of this code checkpoint and integrate it with F1/F2/F5. Stage 4 should render the supplied warning contract and establish its schema/migration evidence. The final authorized rehearsal should demonstrate metadata correction with preserved history and a structural warning from the integrated UI. This focused result does not substitute for migration compatibility, the final integrated rehearsal or portable recipient acceptance.
