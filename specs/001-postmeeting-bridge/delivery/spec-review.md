# Main Lead 4.0 bounded specification review

Reviewed input: `9df8393171af632b126a9801fe4cca73b1c575d1`, original base
`04eba98cb8673406d1e5d38c5318fb963cc77ff7`. Independent source adviser: Codex Astra
`/root/spec_review`; this is not a Grok, Luna or Fable invocation. No model voting.

| Finding | Source and impact | Lead correction |
|---|---|---|
| L4-01: action matrix incomplete | C-A roles omitted inventory_edit; inventory_commands.py:430 also requires it when approving an existing correction. Default deny would break promised editing/correction continuity. | Operator explicitly retains safe direct edits; Approver authorizes only the independently reviewed correction mutation. Add inventory_commands.py to T005; do not grant Approvers blanket direct edits. |
| L4-02: UI context surfaces missing | T006 omitted Corrections.tsx, InventoryEditor.tsx and Workflow.tsx actor pickers. Corrections.tsx:32–46 restores an unscoped payload before authentication; :155–162 stores it. | Add all three components to T006. Bind protected state/retry to principal/domain/config revision; suppress late responses, clear views, remove legacy unscoped restoration. Ambiguous operations retain minimal original-context recovery pointers and require authenticated readback before replacement. |
| L4-03: final advisory dependency | T027 promised both design and candidate review but depended only on T001. | Keep 40 task IDs; FABLE-DESIGN follows T001, final T027 depends T024/T025 and pins their exact candidate. Early design advice cannot complete final review. |

Independent source review recommended adoption after L4-01/L4-02 and found no further
migration/history/ticket blocker. T003 already owns store.py, which supplies schema
recognition and explicit upgrade to state_ops.py and the CLI. T023 may retain final
recovery/readiness integration; no application migration was run during this review.

The supplied candidate is retained as reviewed input; the amended candidate receives a
separate exact SHA after publication. Source agreement is not behavior evidence. Every
Tier A runtime criterion, independent QA gate and later human outcome remains open.
The existing public evidence ledger is unchanged. Final original-spec versus amendment
readback is retained in the lead checkpoint, including any remaining findings.

Independent delta review closed L4-01/L4-02 and confirmed L4-03/lead-history addenda.
It found one mechanical lease-format defect: new files in task-graph.csv used spaces
instead of semicolons. The lead corrected those T005/T006 file separators before adoption.
Main Lead 4.0 accepts the corrected specification as source design, with route/capacity
and future runtime/human gates retained. The supplied 9df8393 candidate is not accepted
unamended. Publication identifies the exact corrected base separately.
