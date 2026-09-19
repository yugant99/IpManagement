# Stage 3 inventory editing and IPv6 planning

**READY FOR PROJECT-LEAD REVIEW — Stage 3. Source implementation only; integration and runtime evidence pending.**

- Owner: Stage 3 subagent `/root/inventory_planning`, coordinated by the active Stage 3 implementation task. Persistent project ownership remains with the original project-lead task.
- Worktree: `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-3-inventory`.
- Branch: `codex/stage-3-inventory-planning`.
- Code checkpoint: `aa3c37e422b09e7a3b38c9653e0b97ea3ed57620`. The later handoff publication commit preserves this code checkpoint.
- Integration base: `5578431c85ffa18071d6262d08a49a251b072afd`, the coordinator's agreed combination of Stage 2, fixture and current lead-document dependencies. This lane does not merge application work into `main`.
- Contract: `demo-v2-questionnaire`; bounded inventory additions from `QUESTIONNAIRE_SCOPE_DELTA.md`.
- Owned files: `backend/ipam_demo/inventory_commands.py`, `frontend/src/InventoryEditor.tsx`, `frontend/src/inventoryCommandsApi.ts`, and this report. No shared schema, seed, app shell, global status, fixture or reserved state/Part 6 files changed.

## Implemented source

| Rows / goals | Behavior | Remaining evidence or scope limit |
|---|---|---|
| RFP-003 / G04 | Child creation with strict CIDR, UUID scope, managed perimeter, same-scope/family containment and declared-ancestry overlap checks. Metadata changes are allowed; bounds changes require no children, direct allocations or attached pools. | API/runtime behavior unexecuted. No subtree rewrites, parent reassignment, family change or deletion. |
| RFP-027 / G04 | Owner, purpose, tags and at most 32 string custom fields persist through the API command and UI form. Reserved identity, version, provenance and actor fields cannot be shadowed by custom metadata. | No typed schema designer. |
| RFP-026 / G01–G03 | Domain/region selectors resolve to a real scope UUID and fetch that scope's persisted prefixes; scope namespace and identity remain visible. | This lane covers inventory organization. Separate scoped source evidence depends on the coordinator/evidence lane. Domain labels and demo actors do not supply tenancy or directory integration. |
| RFP-035, RFP-095 / G19 | IPv6 parent capacity and up to 20 first-free child candidates are computed using merged prefix-index intervals. The UI requests 10 candidates and persists selection through the same child command. All capacity counts are decimal strings. | No host enumeration or IPv6 subscriber allocator. Regional intent is a parent/child assignment inside the selected scope; no live geographic rollout. |

Writes use the shared `workflow.require_actor(actor_id, "inventory_edit")` permission and `workflow.audit_event(...)` helper. The fixed demo approver can edit inventory across registered scopes; no new domain-grant model was introduced. Roles remain server-derived.

The command runs within the coordinator's existing `BEGIN IMMEDIATE` writer transaction. It checks the reviewed prefix/parent version and actual `app_meta.baseline_version` before mutation. Every successful intended-state change increments the actual baseline and affected attached/ancestor pool versions; child creation increments its parent's prefix version, and edits increment the edited prefix version. Unchanged edits return `NO_CHANGE` without creating a success effect.

Original `origin` JSON is unchanged on edits. New children receive synthetic local-inventory origin references. The successful audit stores before/after state, versions and the reason in the same transaction. Failure audits must use the coordinator's post-rollback wrapper; the helper does not commit on its own.

## Integration interface

The coordinator agreed to own these API routes and the shared UI shell wiring:

| Route | Module call / shape |
|---|---|
| `GET /api/actors` | Plain array from `workflow.actors()`, with `id/name/role/team/permissions`. |
| `GET /api/prefixes/{id}/edit-context` | `edit_context(connection, prefix_id)` → prefix detail, scope, current baseline version, direct child count. Use the same read transaction for the prefix and version snapshot. |
| `GET /api/prefixes/{id}/child-preview?prefix_length=64&limit=10` | `preview_children(connection, parent_id, prefix_length, limit)` → parent/version/scope, baseline, string counts and candidate CIDRs. |
| `POST /api/prefixes` | `create_child(connection, payload)` → prefix detail, committed baseline, audit ID. |
| `POST /api/prefixes/{id}/edit` | `edit_prefix(connection, prefix_id, payload)` → the same mutation result shape. |

Create JSON fields are `actor_id`, `reason`, `scope_id`, `parent_id`, `expected_parent_version`, `expected_baseline_version`, `cidr`, `owner`, `purpose`, `tags`, `custom_fields`. Edit JSON replaces the scope/parent/expected-parent fields with `expected_version`. Unknown, missing or reserved top-level fields are rejected. Prefix identity, scope, family, parent and origin cannot be edited.

Render `InventoryEditor` with `scopes` and optional `onChanged` to refresh the shared inventory list after confirmed writes. It uses relative real API URLs and the existing error/loading/layout classes. Root owns the small `.inventory-form` CSS addition. The UI distinguishes a committed write from an unconfirmed error/timeout, presents the audit ID, and asks for a fresh review when saved versions have changed. Saved calculation runs retain their original ledger revision.

## Evidence, limitations and handoff

Actually performed: repository/contract/source inspection, agent-to-agent shared-interface coordination, owned staged-diff inspection and Git checkpoints. No application test, smoke check, type check, build, generator, runtime, browser, installation, container or infrastructure command was run. No functional questionnaire credit is claimed.

Unmerged dependencies: the coordinator's Stage 3 schema/audit table and API transaction/failure-audit routes; workflow actor/audit exports; common UI integration. This branch is a lane source checkpoint, not an independently runnable release. The root coordinates the bounded independent review and feature-branch merge, and records final pushed SHA/PR in its stage report. The lane branch is pushed before handoff; do not infer `main` integration or release acceptance from the push.

No unresolved product decision blocks this bounded slice. Actual conflict, concurrency, persistence, large IPv6-count and rendered-form behavior remain unverified under the user's no-check instruction. Required future evidence includes stale-version rejection, sibling overlap rejection, attached-pool bounds refusal, metadata origin preservation, atomic mutation/audit rollback and a persisted IPv6 child selected from the preview.

Suggested next prompt:

> Review and integrate the inventory lane `codex/stage-3-inventory-planning` from code checkpoint `aa3c37e422b09e7a3b38c9653e0b97ea3ed57620` into the isolated Stage 3 integration branch of `yugant99/IpManagement`. Read this handoff and source diff, reconcile the shared actor/audit helpers and transaction routes, and wire `InventoryEditor` into the common shell. Preserve separate unmerged dependency and runtime-evidence states, the 111-row denominator, reserved state/Part 6 ownership and the user's no-test/no-runtime constraint. Route any concrete defect to this inventory owner; the persistent project lead retains stage acceptance and `main` merge authority.
