# Read-only implementation seam inventory

Scout: contract_scout; 2026-09-22; baseline 04eba98cb8673406d1e5d38c5318fb963cc77ff7.
No application execution or tests. These are source facts, not behavior observations.

| Surface | Existing seam | Consequence for specification |
|---|---|---|
| Staged inventory | imports.py:_stage_inventory, import_envelope; source_batches/source_records | Preserve staged raw/grouped records and active-ledger immutability; comparison is new. |
| Saved-run comparison | reports.py:compare_runs | Compares calculation results, not migration candidate inventories. Do not mislabel it. |
| Writes/audit | app.py:write_operation and audited_write; BEGIN IMMEDIATE | Reuse transaction and post-rollback failure-audit conventions. |
| Allocation | workflow.py:_eligibility, create_request, decide_request | Exact candidate/version checks exist. No reservation record/check exists. |
| Uniqueness | allocations UNIQUE(scope_id,family,address) | Separate holds require shared transactional conflict checks; unique allocation alone is insufficient. |
| Identity | workflow.py:DEMO_ACTORS and require_actor | Two global demo actors, no trusted scoped principal boundary. |
| Egress | app.py run/import/raw/audit/report routes | Mixed-scope payloads, summaries, presets and direct-ID exports need explicit access treatment. |
| Exceptions | sync_exceptions, _exception_payload, update_exception | Reuse stable case identity, episodes, acknowledgement, healthy/unknown rules; do not duplicate queue. |
| External outcomes | allocation_requests downstream simulation fields | No ServiceNow ticket/delivery identity; simulated_success is not a vendor integration. |
| Synthetic feed | feed_adapter.py, scheduler.py | Local acquisition only; process lock is not distributed delivery or live discovery. |
| Schema | v5 plus store.py/state_ops.py migrations | One owner coordinates new schema, fresh initialization and state-command compatibility. |
| UI | FirstPath.tsx, Workflow.tsx, Corrections.tsx, CapacityReports.tsx | Extend existing shell and provenance views instead of introducing another frontend. |

Input remains versioned JSON, 10 MiB and 10,000 records. Raw candidate groups live under
typed_json.inventory_group; they are immutable source evidence. Comparisons need an active
snapshot version, not a second inconsistent validation/parser implementation.

Current code uses Python >=3.12,<3.13, FastAPI 0.141.1, Uvicorn 0.50.1, React 19.3.0,
TypeScript 7.0.2, Vite 8.3.0; supported Node range comes from frontend/package.json.
These versions were read from manifests, not executed or upgraded.

Vendor interfaces remain unselected/unobserved. No endpoint, ACL, table, webhook or vendor
idempotency feature is inferred from product names. A simulated local contract must label
its own semantics and keep vendor mapping a separately gated future artifact.
