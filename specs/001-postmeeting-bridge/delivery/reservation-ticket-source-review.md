# T012/T013 independent source review

Lead: Main Lead 5.0 / GPT-6 Astra. Reviewer: GPT-6 Sol high, task path `/root/sol_bridge_review` in this lead's tree. Full feature authors: Muse 1.3 high via OpenCode (T012), Opus 5.5 high via Claude Code (T013). Shared source base `b557137279f09abb6979618d6eea7ca24fc27ef7`.

## Shared wire review

Sol inspected the pickup and frozen wire read-only. Lead settled new intent-backed local decisions as downstream_status=not_requested and refused simulate_failure=true, preserving historical request hashes/status/replay. Existing conservative pending/routing_blocked/unknown linked-hold release refusal stays explicit; no new attempt after released hold/rejected request, readback/history remain available. Three attempt phases share the existing ticket.attempt identity and durable ordinal. Sol found no material contradiction in the freeze. No source or runtime acceptance of a later implementation follows from that contract review.

## T012 initial candidate

Draft PR82, exact candidate `c5b59cb4a47e07a87b594f13bee0ca7316c0d965`. App/models only. Independent full review returned three findings:

1. Missing ReservationHistoryEntry import would break reservation detail history serialization.
2. No exact-key HTTP recovery after lost create/proposal response and reload; list/detail IDs alone cannot resolve the saved original-context key. Lead amended the wire in `f33fdfab2d22d4c129bb9339316b2504a1f1fc31` using existing receipts/proposal rows.
3. Release decision must check Approver after target scoping and before leaf payload validation, preserving403 forbidden-operation precedence for a same-domain Viewer and404 for a foreign target.

The same Muse session owns the correction batch. Source acceptance is held until exact corrected SHA and independent delta closure. Other inspected paths preserve T011 normalized hashes, selected-domain filtering before pagination, validated mutation projection and replay target authorization. Generated OpenAPI response typing is deferred to the T021 exact-candidate documentation gate.

## T013 and combined review

Implementation ongoing. No exact source candidate or acceptance recorded. Sol must independently inspect complete T013 source and combined T012/T013 interfaces before integration. T014 remains dependency-held until that gate.

## Evidence boundary

Only Git/source inspection and model-route/usage/tool-permission preflight ran. No application tests, builds, typechecks, imports, database operations, services or browser application checks. T025 runtime remains gated on all prerequisites and fresh disposable synthetic data. Portable/human evidence remains pending, no questionnaire promotion, Tier B locked.
