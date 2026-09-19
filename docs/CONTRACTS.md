# Shared engineering contracts

Status: agent-decided design contract, with a **Stage 1 implementation checkpoint pending review and runtime evidence**. See [the concrete foundation API](FOUNDATION_API.md) and [native setup/status](FOUNDATION.md). Only inventory, explicit seed, serve/readiness and UI source are implemented at this checkpoint. Imports, calculations, writes/workflow and reset/backup/restore remain planned. The lead records any change here before another lane depends on it. These interfaces do not require generic adapter or workflow frameworks.

Contract revision: `demo-v2-questionnaire`. [Implementation decisions](IMPLEMENTATION_DECISIONS.md) supplies identity, import, calculation, API, workflow and state-operation details, with explicit scope changes in [QUESTIONNAIRE_SCOPE_DELTA.md](QUESTIONNAIRE_SCOPE_DELTA.md). The scope delta takes precedence only where it changes earlier exclusions, such as bounded inventory editing, history and the exception queue. The [75-question record](GRILL_75.md) preserves historical rationale; superseded answers never override current contracts.

## Repository ownership

| Surface | Owner |
|---|---|
| `backend/ipam_demo/`, app startup, schema, dependency locks | Lead; individual modules assigned to Parts 1–5 |
| `frontend/`, common shell and build configuration | Lead/UI owner; feature components assigned explicitly |
| `fixtures/` | Part 2, with documented input schema and separate expected outcomes |
| Root `Dockerfile`, `compose.yaml`, `.dockerignore`, `scripts/ops/` | Spencer, Part 6 |
| `docs/parts/06-portability.md`, `docs/handoffs/part-6.md`, `docs/RUNNING.md` | Spencer, Part 6 |
| `AGENTS.md`, development rules, status, shared contracts | Lead/integration |

Paths are ownership boundaries. Stage 1 supplies application files and locks; contributors must inspect current files before editing. The separate data lane owns `fixtures/`, while core owns its small packaged seed at `backend/ipam_demo/data/baseline.json`.

## Runtime supplied by the core team

- One Python API process serves the compiled frontend and `/api/*`. A small FastAPI/Uvicorn service is the selected implementation default; no extra service is needed for the demo.
- Backend module location: `backend/ipam_demo`. The project must install that module into the runtime; do not depend on an accidental developer working directory.
- UI: React/TypeScript with Vite, build through `npm ci` and `npm run build`, output `frontend/dist`. The UI uses relative API URLs.
- Runtime command: `python -m ipam_demo serve --host 0.0.0.0 --port 8000`.
- Container port: `8000`; local host binding defaults to `127.0.0.1`. A public URL is a later deployment decision.
- `IPAM_DATA_DIR` identifies writable app data, including `ipam_demo.sqlite3`. Native default: local `./data`; image default: `/data`, mounted outside the image.
- `IPAM_STATIC_DIR` identifies built UI assets. Packaging sets it to the image's static directory. No hardcoded developer paths.
- `/healthz`: readiness returns 200 for process/schema/initialized data ready, otherwise 503 with separate readiness booleans and a safe reason. An unseeded app serves setup-needed UI. The source catalog API supplies freshness separately. Part 6 consumes these results and avoids restart loops before explicit seed.
- Deterministic setup: `python -m ipam_demo seed --scenario baseline`. Existing initialized data must not be silently overwritten.
- Explicit destructive demo reset: `python -m ipam_demo reset --confirm`. Requires stopped service and exclusive app-data access; touches only the recognized app database and its own sidecars inside the configured location, reports changes and never recursively deletes the data directory. Never resets on startup.
- Consistent snapshot: `python -m ipam_demo backup --output PATH`, using SQLite's backup API to a new destination. Restore: `python -m ipam_demo restore --input PATH --confirm`, with stopped service and exclusive app-data access. Validate app identity/schema/integrity before replacing and preserve the old database. Core implements correctness; Part 6 documents/wraps the commands.
- Data resides on supported local filesystems/local Docker volumes, not network mounts. Missing/unwritable paths fail visibly without an ephemeral fallback. Unsupported schema preserves data and fails with a clear reason.
- Core chooses and pins actual runtime/dependency versions at implementation start. Part 6 consumes the committed locks rather than selecting a second set.

`serve` and `seed` are implemented in Stage 1 source. They have not been executed; no command above is an instruction to run checks now. `reset`, `backup` and `restore` remain required future entrypoints and are explicitly absent from CLI parsing. Stage 1 uses exclusive local app-data locking; stop the service before seeding. `PART6_READY` remains false until the missing state commands and actual build/readiness prerequisites exist.

## Data and calculation boundary

Use scoped prefixes, individual allocations and pools for intended state; typed DHCP lease intervals and routing observations for evidence; source runs/raw records for provenance; saved calculation runs and findings; requests and audit for decisions. Combine simple storage structures when it preserves these facts. Do not build an event bus or event-sourcing system.

Common identity: `scope_id`, address family, address/prefix, and applicable time interval. Common evidence: `source_id`, `source_run_id`, `source_record_id`, `observed_at`, `ingested_at`, completeness and freshness. A human domain label alone is not proof of routing isolation.

Each finding response includes ID, rule/version, run ID, scoped subject, severity/state, explanation, input references, evaluated window, limitations and proposed next action. A saved run supplies both overview and detail/export values. Expected fixture labels never select findings.

The immutable saved run also carries capacity, occupancy, p95 value/status/window/sample counts and forecast value/status/basis. Retain old runs and source references for pinned `run_id` reads. Part 4's backend calculation is delivered before Part 3 pressure rules; UI and export only display its saved output. The questionnaire revision prioritizes a bounded two-run comparison using those existing records.

Core input is versioned JSON, limited to 10 MiB/10,000 records. Receipts use exclusive accepted/rejected/duplicate counts that sum to input; identical batch replay has no new effects. Effective completeness accounts for validation failures. See the companion decision sections for batch selection, scope and time rules.

Initial seed creates the intended inventory baseline. Changed intended-inventory imports are visibly staged and cannot overwrite later approved allocations. Accepted DHCP/routing imports become eligible evidence for reruns. Promotion of a changed intended baseline is deferred; disclose that limitation.

## Allocation boundary

One designated static IPv4 pool with authoritative local intended ledger; fixed request → review → local allocation flow. A request stores the exact candidate and reviewed pool/baseline version. Pending requests do not reserve or change inventory.

The server maps two demo actor identities to permissions and blocks self-approval. On approval it rechecks the exact candidate/version, persists allocation and successful audit together, and rejects conflicts/stale requests visibly. Repeated approval must not allocate twice. Rejection leaves inventory unchanged. Failed transactions remain visible; record failed-attempt audit after rollback when possible.

Approval checks current ledger and eligible contradictory observations, not saved findings. Imports/reruns do not themselves increment allocation concurrency tokens. Pool versions track relevant policy/range/assignment changes; baseline version tracks intended authority. Creation and decision retries are idempotent, terminal requests immutable, and lost audit writes visible. See the companion workflow section.

Downstream provisioning is explicitly simulated. Demo identity is not enterprise authentication. The UI may switch between labeled demo actors; it may not supply an arbitrary trusted role for a decision.

## Target platforms and readiness

Primary packaged target: ordinary Linux `amd64`. Local development machine observed as `arm64`; native development support does not prove an ARM container works. A second architecture/host is stretch unless it becomes a specified recipient requirement. Record exactly what was exercised.

Lead sets `PART6_READY=yes` only after the real runtime module, locks, UI build path, data-path behavior, health and state-management commands are present. Spencer may prepare documentation/package files beforehand, but cannot claim a runnable handoff from placeholders.
