# T018 notice and occupancy UI

Full feature owner: Muse1.3 high in OpenCode after integrated T015 and T017A.
Lease: frontend/src/Workflow.tsx, frontend/src/workflowApi.ts and
frontend/src/CapacityReports.tsx. Retain the existing reservation/ticket, exception,
report and context-isolation behavior. Use actual strict T017A DTOs and
notice-recipient-wire.md; no invented API fields, delivery service or owner mapping.
Independent Sol reviews the whole feature before source integration.

Show scoped notice list/detail, alert versus alarm, current notification version,
server due/evaluation times, resolution and receipt as separate facts. Explicit
manual evaluate only; GET never changes state, no background scheduler or automatic
POST retry. Evaluation failure remains unknown until authorized readback; a later
manual evaluation is a new explicit evaluation, not proof of the earlier response.
Expiry/acknowledgement never frees a hold or resolves its condition.

Only offer acknowledgement when server is_current_recipient and current state
allows it, with current exact version and explicit reason. Fresh server authority
remains decisive. Show unassigned, recipient unavailable, awaiting receipt,
legacy-unbound and acknowledged distinctly. Respect redacted recipient/actor/reason
fields; a configured recipient is not proven business owner. Old operator-only
acknowledgement is legacy history, never recipient receipt or delivery proof.

Before acknowledgement persist a minimal pointer with original principal/domain/
configuration, notice ID and notification_version; include parent reservation ID
only if needed to reconcile routing. No reason/body/token/recipient directory or
raw receipt in storage. Reuse the existing workflow write lock so an unresolved
notice ack blocks conflicting replacement writes. Keep exact same-context retry
payload in memory only. Changed context clears protected data/payloads and
quarantines the pointer; current authorized readback by original principal/domain
can confirm the original exact-version own receipt after renewal. Use GET
/api/reservation-notices/{id}/notifications/{version}. A missing/denied/mismatched
receipt stays unknown, never authorizes silent replacement or pointer deletion.
Display recovered original receipt separately from mutable current notice/version.

Show current-static-IPv4 occupancy using the actual current-static-occupancy API:
pool/scope/domain/family, as_of, unit, active allocations, reserved holds including
expired, total, assignable capacity and remaining, with server provenance. Use the
same identity/units in workflow and capacity views. Keep this separate from saved
DHCP lease calculations, saved run/time, p95/history/forecast and their unknowns.
Do not rewrite saved findings or combine metrics into one total. Preserve existing
capacity thresholds, source completeness caveats and safe child editing. No traffic,
hijack attribution, health monitoring or new IPv6 delegation/host metric is implied.

Context changes and aborted/stale requests must never display prior-domain data.
Use existing task-oriented accessible forms/tables and visible errors. No tests,
builds, typechecks, lint, imports or browser/application runtime before T025.
