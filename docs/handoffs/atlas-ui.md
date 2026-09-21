# Atlas UI handoff

Status: ready for project-lead review; this is a frontend presentation and interaction checkpoint, not global project acceptance.

## Candidate

- Branch: `codex/atlas-ui`
- Initial shell checkpoint: `57e55103029396ddf267ac8450aa041b64164518` (PR #60)
- Production/source checkpoint: `2e81cc289ccfe7829afc19945d157b56d5397b46` (view-scroll reset, panel gutter, token cleanup, and rail-label copy correction).
- Docs-only publication head before this reproducibility correction: `7e1f1378b564fed5948132f2f75784eebe2415f2`; the final worker message reports the new docs-only head.
- Owned paths: `frontend/src/App.tsx`, `frontend/src/styles.css`, `frontend/src/Workflow.tsx`, `frontend/src/Corrections.tsx`, `frontend/src/Schedule.tsx`, `frontend/src/CapacityReports.tsx`, and this handoff.
- No backend, schema, API, fixture, lockfile, status, or acceptance-store changes.

## What changed

Atlas is the approved light paper/white-appbar direction: grouped operational rail navigation, sticky desktop rail with narrow horizontal navigation, scoped inventory workspace, readable tables, and literal current-workflow versus saved-evidence labels. Existing API calls, view state, permissions, saved-run IDs, retries, and prefix-detail focus return remain unchanged.

Rail navigation now resets document scroll to the destination workspace top without resetting view-local filters, forms, or loaded data. This prevents a long schedule/report scroll position from opening the next view below its heading.

## Supported setup and start

From the repository root, using a fresh disposable store and isolated Python environment:

```sh
ATLAS_ROOT="$PWD"
ATLAS_STORE="$(mktemp -d /tmp/ipam-atlas-store.XXXXXX)"
ATLAS_UV_PARENT="$(mktemp -d /tmp/ipam-atlas-uv.XXXXXX)"
export UV_PROJECT_ENVIRONMENT="$ATLAS_UV_PARENT/venv"
uv sync --frozen --python 3.12
cd "$ATLAS_ROOT/frontend"
npx --yes node@24 node_modules/typescript/bin/tsc --noEmit
npx --yes node@24 node_modules/vite/bin/vite.js build
cd "$ATLAS_ROOT"
PYTHONPATH="$ATLAS_ROOT/backend:$ATLAS_ROOT/fixtures/evolving" \
IPAM_DATA_DIR="$ATLAS_STORE" \
"$UV_PROJECT_ENVIRONMENT/bin/python" -m ipam_demo seed --scenario rich \
  --inventory "$ATLAS_ROOT/fixtures/v1/inventory.json"
IPAM_DATA_DIR="$ATLAS_STORE" \
IPAM_STATIC_DIR="$ATLAS_ROOT/frontend/dist" \
IPAM_SYNTHETIC_FEED_DIR="$ATLAS_ROOT/fixtures/v1" \
PYTHONPATH="$ATLAS_ROOT/backend:$ATLAS_ROOT/fixtures/evolving" \
  "$UV_PROJECT_ENVIRONMENT/bin/python" -m ipam_demo serve --host 127.0.0.1 --port 8000
```

The verified preview used Python 3.12.10 with frozen project dependencies: FastAPI 0.141.1 and Uvicorn 0.50.1. The current preserved compiled UI/API preview is separate from the fresh-store sequence above: [http://127.0.0.1:8000/](http://127.0.0.1:8000/), disposable store `/tmp/ipam-atlas-f234-rich-20260921`, API PID 64292. Do not reseed that fixed review store; stop it with Ctrl-C only when the preview is no longer needed. Do not use retained acceptance stores.

## Verified focused flow

On the final rich preview, the worker observed:

1. Inventory loaded 60 real synthetic prefixes.
2. Network scope, domain, region, IPv4/IPv6 family, and IP search (`10.40.2.1`) returned scoped results; the IP search preserved the containing parent and matching child.
3. Source evidence exposed the imported-source catalog and the `Reconcile after this import` opt-in. Uploading `fixtures/v1/observations/dhcp-north.json` committed 750 accepted rows and a succeeded reconciliation run.
4. Synthetic acquisition exposed saved schedule state. `Run now` with reason `Atlas locked rich demo cycle` committed cycle 1 and saved run `32ef5528-2b16-4050-ad5e-533dde438289`.
5. Capacity and reports loaded that saved run, showed occupancy/history/forecast values, saved a report preset, and returned HTTP 200 JSON export with keys `calculations`, `exported_findings`, `findings`, `overview`, and `selected_batches`.
6. Requests and exceptions loaded the current workflow, stored audit history, and 11 open exception records with acknowledgement-due state.
7. Inventory corrections loaded the saved run selector, correction workflow sections, and permission-gated proposal controls.
8. Switching from a scrolled long view to Reconciliation reset the destination to its top heading; view-local state was not reset. Prefix detail close returned focus to its originating inventory row in the earlier baseline pass.

Lead independently observed desktop and 390px narrow layouts, no document overflow, usable grouped narrow navigation, and keyboard movement through Requests and exceptions → Corrections plus skip-link focus. Those observations remain lead-owned evidence.

## Checks and limits

- Node 24.21.0 isolated runtime: TypeScript no-emit and Vite production build passed.
- The compiled bundle contains the final `CapacityReports.tsx` guidance copy (`compute a run in Reconciliation`). The populated saved-run selector also has explicit `min-width: 0` and `width: 100%` sizing for narrow workspaces.
- `git diff --check` passed.
- No broad backend suite was run; checks were limited to the named UI workflows and the supported local runtime.
- Synthetic/local only. No live discovery, external provisioning, production identity, portable recipient acceptance, or questionnaire status credit follows from this handoff.
