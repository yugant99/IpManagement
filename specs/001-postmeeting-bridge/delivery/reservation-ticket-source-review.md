# T012/T013 independent source review

Lead: Main Lead 5.0 / GPT-6 Astra. Reviewer: GPT-6 Sol high, task path `/root/sol_bridge_review` in this lead's tree. Full feature authors: Muse 1.3 high via OpenCode (T012), Opus 5.5 high via Claude Code (T013). Shared source base `b557137279f09abb6979618d6eea7ca24fc27ef7`.

## Shared wire review

Sol inspected the pickup and frozen wire read-only. Lead settled new intent-backed local decisions as downstream_status=not_requested and refused simulate_failure=true, preserving historical request hashes/status/replay. Existing conservative pending/routing_blocked/unknown linked-hold release refusal stays explicit; no new attempt after released hold/rejected request, readback/history remain available. Three attempt phases share the existing ticket.attempt identity and durable ordinal. Sol found no material contradiction in the freeze. No source or runtime acceptance of a later implementation follows from that contract review.

## T012 initial candidate

Draft PR82, exact candidate `c5b59cb4a47e07a87b594f13bee0ca7316c0d965`. App/models only. Independent full review returned three findings:

1. Missing ReservationHistoryEntry import would break reservation detail history serialization.
2. No exact-key HTTP recovery after lost create/proposal response and reload; list/detail IDs alone cannot resolve the saved original-context key. Lead amended the wire in `f33fdfab2d22d4c129bb9339316b2504a1f1fc31` using existing receipts/proposal rows.
3. Release decision must check Approver after target scoping and before leaf payload validation, preserving403 forbidden-operation precedence for a same-domain Viewer and404 for a foreign target.

Muse corrected the initial findings in `177871f165495c390d954b3afd12899e194fe693`. Sol then required stronger canonical receipt reconciliation and original-versus-current proposal separation. Muse completed those fixes at `82187a77fb3a75bd9e3d9096c7d85ea4e7c43d0e`; independent delta review closed all six recovery findings. Sol then caught slash-bearing key transport; Muse changed recovery to query transport at `0e8fb4b3168261328d7832781453dfb14f40e8d3`, independently closed. This is the final T012 source-accepted SHA. Other inspected paths preserve T011 normalized hashes, selected-domain filtering before pagination, validated mutation projection and replay target authorization. Generated OpenAPI response typing is deferred to the T021 exact-candidate documentation gate.

## T013 and combined review

Draft PR83 initial complete core is `8d0b49e88bb8355a4f746cd1e1cdb721bb4dd12e`. Sol independently reviewed the full core, schema and combined call. Blocking finding: zero-attempt definitive absence did not resolve a rejected request's intent, permanently preventing unused hold release. Additional corrections: inaccurate provisioning wording and mutation authorization before payload semantics. Lead and Sol settled the bounded zero-attempt/disabled-acknowledgement clarification in the shared wire. Opus corrected these at `e328f75d801afb668617a774001df1abe1f13430`. Sol found three remaining integrity/current-summary defects; Opus closed them, plus equal-millisecond event ordering, at `57dd77362f612f2a6a4f65b0e7a6dde80eddf12f`. Sol independently confirmed generic integrity failure for impossible zero-attempt states/malformed stored resolution, current-state/latest-attempt summary reasons, and causal history ordering. All reported blocking source findings are closed at that exact SHA.

Source review otherwise found compatible T012 configuration forwarding, atomic request/intent/audit, retained legacy hashes, local downstream_status=not_requested, immutable correlation/digest and attempted route, durable ordinal reservation before effect, distinct effect/observation transactions, no repeated effect on replay, matching actual-ID readback, and schema-compatible records. Sol independently confirmed combined invariants at final T012/T013 SHAs. Lead source integration is `6599ae493edcb897a407d90570b68efd5affcea2`, preserving both feature histories without conflict edits. This releases T014 source work only; it establishes no runtime acceptance.

## Evidence boundary

Only Git/source inspection and model-route/usage/tool-permission preflight ran. No application tests, builds, typechecks, imports, database operations, services or browser application checks. T025 runtime remains gated on all prerequisites and fresh disposable synthetic data. Portable/human evidence remains pending, no questionnaire promotion, Tier B locked.

## T014-discovered reassignment receipt correction

Two same-principal reassignment operations could be confused if saved assignment
version pointed to a later own assignment. Opus retained the original T013 lease
and added an atomic exact receipt-to-audit anchor at c878cf5, then the shared
recover_reassignment validator used by core POST replay at
`a5ce063f2e350fe854c9e10a0d35cd439dd042e2`. Sol independently closed this correction: 
current authorization before saved data, strict types/positive versions, unique
anchor, canonical actor/scope/route/time/before-after identity and original digest.
This supersedes57dd7736 as the final T013 source candidate. T014 GET must use the
same helper before its source acceptance. No runtime or older-receipt migration
was inferred; unanchored old source receipts fail visibly instead of guessing.
