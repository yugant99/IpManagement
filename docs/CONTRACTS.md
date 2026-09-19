# Shared engineering contracts

Status: agent-decided design contract. **Not implemented.** The lead records any change here before another lane depends on it. These interfaces remove guesswork; they do not require generic adapter or workflow frameworks.

## Repository ownership

| Surface | Owner |
|---|---|
| `backend/ipam_demo/`, app startup, schema, dependency locks | Lead; individual modules assigned to Parts 1–5 |
| `frontend/`, common shell and build configuration | Lead/UI owner; feature components assigned explicitly |
| `fixtures/` | Part 2, with documented input schema and separate expected outcomes |
| Root `Dockerfile`, `compose.yaml`, `.dockerignore`, `scripts/ops/` | Spencer, Part 6 |
| `docs/parts/06-portability.md`, `docs/handoffs/part-6.md`, `docs/RUNNING.md` | Spencer, Part 6 |
| `AGENTS.md`, development rules, status, shared contracts | Lead/integration |

Paths are reserved ownership boundaries; application files do not exist yet. Contributors must inspect current files before editing.

## Runtime supplied by the core team

- One Python API process serves the compiled frontend and `/api/*`. A small FastAPI/Uvicorn service is the selected implementation default; no extra service is needed for the demo.
- Backend module location: `backend/ipam_demo`. The project must install that module into the runtime; do not depend on an accidental developer working directory.
- UI: React/TypeScript with Vite, build through `npm ci` and `npm run build`, output `frontend/dist`. The UI uses relative API URLs.
- Runtime command: `python -m ipam_demo serve --host 0.0.0.0 --port 8000`.
- Container port: `8000`; local host binding defaults to `127.0.0.1`. A public URL is a later deployment decision.
- `IPAM_DATA_DIR` identifies writable app data, including `ipam_demo.sqlite3`. Native default: local `./data`; image default: `/data`, mounted outside the image.
- `IPAM_STATIC_DIR` identifies built UI assets. Packaging sets it to the image's static directory. No hardcoded developer paths.
- `/healthz`: lightweight readiness with status, schema readiness and data readiness; no secrets. The source catalog API supplies detailed source freshness. Part 6 consumes these results; it does not implement reconciliation health itself.
- Deterministic setup: `python -m ipam_demo seed --scenario baseline`. Existing initialized data must not be silently overwritten.
- Explicit destructive demo reset: `python -m ipam_demo reset --confirm`. Operates only on the configured demo data location and reports what changed. Never resets on every startup.
- Consistent snapshot: `python -m ipam_demo backup --output PATH`; restore: `python -m ipam_demo restore --input PATH --confirm`, with the application stopped for restore. Core implements database correctness; Part 6 documents/wraps the commands. Do not copy an active SQLite main file without accounting for its journal.
- Core chooses and pins actual runtime/dependency versions at implementation start. Part 6 consumes the committed locks rather than selecting a second set.

Every command above is a required future entrypoint, not an instruction to run it now. `PART6_READY` is false until they and their dependency/build artifacts actually exist.

## Data and calculation boundary

Use scoped prefixes, individual allocations and pools for intended state; typed DHCP lease intervals and routing observations for evidence; source runs/raw records for provenance; saved calculation runs and findings; requests and audit for decisions. Combine simple storage structures when it preserves these facts. Do not build an event bus or event-sourcing system.

Common identity: `scope_id`, address family, address/prefix, and applicable time interval. Common evidence: `source_id`, `source_run_id`, `source_record_id`, `observed_at`, `ingested_at`, completeness and freshness. A human domain label alone is not proof of routing isolation.

Each finding response includes ID, rule/version, run ID, scoped subject, severity/state, explanation, input references, evaluated window, limitations and proposed next action. A saved run supplies both overview and detail/export values. Expected fixture labels never select findings.

Initial seed creates the intended inventory baseline. Changed intended-inventory imports are visibly staged and cannot overwrite later approved allocations. Accepted DHCP/routing imports become eligible evidence for reruns. Promotion of a changed intended baseline is deferred; disclose that limitation.

## Allocation boundary

One designated IPv4 pool; fixed request → review → local allocation flow. A request stores the exact candidate and reviewed pool/baseline version. Pending requests do not reserve or change inventory.

The server maps two demo actor identities to permissions and blocks self-approval. On approval it rechecks the exact candidate/version, persists allocation and successful audit together, and rejects conflicts/stale requests visibly. Repeated approval must not allocate twice. Rejection leaves inventory unchanged. Failed transactions remain visible; record failed-attempt audit after rollback when possible.

Downstream provisioning is explicitly simulated. Demo identity is not enterprise authentication. The UI may switch between labeled demo actors; it may not supply an arbitrary trusted role for a decision.

## Target platforms and readiness

Primary packaged target: ordinary Linux `amd64`. Local development machine observed as `arm64`; native development support does not prove an ARM container works. A second architecture/host is stretch unless it becomes a specified recipient requirement. Record exactly what was exercised.

Lead sets `PART6_READY=yes` only after the real runtime module, locks, UI build path, data-path behavior, health and state-management commands are present. Spencer may prepare documentation/package files beforehand, but cannot claim a runnable handoff from placeholders.
