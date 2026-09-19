# Scope changes from questionnaire reprioritization

Planning only; companion to `CONTRACTS.md` revision `demo-v2-questionnaire`. [QUESTIONNAIRE_PRIORITIES.md](QUESTIONNAIRE_PRIORITIES.md) controls priority and [QUESTIONNAIRE_ROW_MAP.md](QUESTIONNAIRE_ROW_MAP.md) controls row accounting. The earlier 75-question transcript remains historical evidence, not a rule against these explicitly authorized planning changes.

## Parts 1 and 4: inventory and prefix planning

- Prioritize a bounded G04/G19 slice: child-prefix creation, safe modification, extra string key/value metadata, and IPv6 prefix planning. Scope records may carry domain/region context; these labels never replace `scope_id` or establish tenant/identity isolation.
- Prefix edits go through the API, a permitted demo actor, existing scope/CIDR/parent/conflict validation and audit. Local intended-ledger writes update its revision and any affected pool version so stale reviews fail. Editing a label does not silently relocate an allocation.
- Allow changing an empty prefix's bounds only when parent containment and sibling relationships remain valid. For this weekend, refuse bounds edits to any prefix with allocations, children or an attached pool: even an allocation-empty pool may have configured ranges/exclusions that would be stranded. Permitted metadata edits remain separate. No destructive subtree rewriting, deletion cascade, field-schema designer or automatic promotion of an imported IPAM baseline.
- Preserve original seed/import evidence separately from current intended state. Custom metadata cannot overwrite reserved identity/version fields.
- IPv6 planning operates on parent/child prefix lengths, counts and a bounded first-free child preview. Persist a selected child as an intended prefix under a fictional region parent, using the same validated creation path. Count delegated prefixes, never enumerate hosts; serialize counts beyond JavaScript's safe integer range without precision loss.
- A region label alone cannot satisfy geographic allocation, and a domain dropdown alone cannot satisfy multi-domain operations: show separately scoped inventory/sources and an actual persisted regional parent/child assignment. Keep these claims bounded to network inventory.

## Parts 3 and 4: history and exports

- Prioritize G16's history portion: list and compare two existing immutable runs by stable scope/rule/subject. Retain old evidence and unknown outcomes. Scheduling is a separate conditional extension, not inferred from run history.
- Include a minimal G20 report preset when it can reuse existing filters: save selected filters/columns, pin run ID and export actual data. Audit export uses stored audit events. No report builder or compliance certification claim.

## Part 5: exception queue

- Prioritize G25's bounded queue: finding reference, owner, acknowledgement/escalation state and reason/history. Notify inside the app when real new findings appear; no email/ServiceNow integration claim.
- Keep exception workflow state separate from computed anomaly state. Acknowledgement cannot make a detected conflict healthy or a source complete.
- For conditional RFP-081 evidence, record a handoff from one named fictional team to another with assigned actor, recipient acknowledgement and audit. Fixed roles/teams only; broader cross-team operating processes remain partial.
- Release/reclaim/remediation (G23) and configurable lifecycle workflows (G24) remain deferred. Do not weaken exact-candidate allocation or evidence rules to add them.

## Conditional import trigger and schedule

- RFP-043: after committing accepted DHCP/routing evidence, optionally invoke the same reconciler with `trigger=import` and the source-run ID. An idempotent whole-batch replay must not create duplicate triggered effects. Staged IPAM changes are not silently promoted. Import and reconciliation outcomes are separate: a run failure/busy result cannot undo a completed import or masquerade as a successful rerun.
- RFP-068, later option: a small timer in the single API worker uses the same run lock, saved off/interval setting and last/next/error state. Wall time drives scheduling, while the explicit demo clock drives synthetic calculations. Do not duplicate timers under development reload or add a queue, missed-run catch-up system or worker service. Missing/failed runs remain visible.

## Lead-owned delivery documents

Use one compact `docs/DELIVERY_METHOD.md` and a proposed roadmap section rather than a document framework. Cover review cadence and checklist (083), tracked improvements/feedback (086), per-domain migration waves with entry/exit criteria and rollback (088), and a proposed 24-month sequence with dependencies (105). Reuse this material for existing assessment, ownership, training/methodology and knowledge-transfer rows where relevant.

The migration method is design evidence; changed-baseline promotion and live migration execution remain absent. The roadmap is a proposal requiring product-owner adoption, not a promised release schedule. Staff, references, licensing/support terms and compliance assertions require genuine provider evidence and are not synthesized.

## Estimates and readiness

No runtime entrypoints or Part 6 ownership change. No new services or database. Product expansions are estimated at 4–7 focused lane hours plus 2–3 for shared delivery documents; short event/team extensions are conditional, scheduling last. These are included by prioritization and overlapping bounded lanes within the intended weekend, not by consuming all integration time.

Nothing in this revision authorizes application execution, tests, containers, infrastructure spending or external submissions. Current work remains planning. Later implementation reports exact commit/scenario evidence and row-level remaining gaps.
