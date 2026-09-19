# Six parts, one integrated application

Planning budget: approximately 20 lead working hours, with Spencer's 6–8 hours overlapping. These are estimates, not 20 hours per agent. **Current priority and coverage live in `QUESTIONNAIRE_PRIORITIES.md` and the 111-row map.** `COVERAGE.md` and `GOALS.csv` preserve the earlier baseline; their 22/30 percentage is no longer the success headline.

## Ownership

| Part | Owner | Branch pattern | Main output |
|---|---|---|---|
| 1 | Lead/inventory agent | `codex/part-1-inventory` | Scoped data model, inventory API and common app wiring |
| 2 | Data agent | `codex/part-2-sources` | Synthetic source pack, imports, provenance and assessment export |
| 3 | Rules agent | `codex/part-3-reconciliation` | Computed states/findings with source evidence |
| 4 | UI/calculation agent | `codex/part-4-dashboard` | Shared dashboard/detail views and explained capacity forecast |
| 5 | Core workflow agent | `codex/part-5-workflow` | One-pool approval/allocation and audit |
| 6 | Spencer | `codex/part-6-portability` | Runnable artifact, persistence and recipient handoff |

These are work packages. Run only as many simultaneous lanes as available tools/contributors support. The lead integrates and can combine small lanes; do not spawn agents just to fill a diagram.

The persistent lead coordinates the five implementation stages in `CHAT_STAGES.md`: foundation, first complete path, main capabilities, integration/freeze, and acceptance/delivery. Fresh worker chats receive generated prompts at reviewed checkpoints; the original lead retains overall ownership throughout. Parts can overlap: richer synthetic data and Spencer's preparation can proceed alongside Stage 1. Runtime readiness remains event-driven. See `PROJECT_OVERSIGHT.md` for acceptance and reporting.

Current fold-ins: Parts 1/4 prioritize bounded subnet editing, custom fields and domain/IPv6 prefix planning; Parts 3/4 expose existing run history and one report preset; Part 5 adds the small exception queue. Lead owns the delivery method/roadmap draft. These target 12 new rows beyond the original 53. Actual import-triggered rerun and team handoff are the two conditional additions toward 67; scheduling follows only if time remains. Refer to the scope delta for exact acceptance and limitations. They do not change Spencer's runtime ownership.

## Sequence

1. **Hours 0–1.5:** freeze contracts, a small fixture and file ownership; establish backend/frontend entrypoints and dependency locks. Spencer can prepare Part 6 against the documented contract.
2. **Hours 1.5–6:** deliver source import → saved inventory/observations → one computed finding → browser evidence detail. UI and rules use the same fixture IDs and response shape.
3. **Hours 6–11:** complete rule conditions and controls, capacity view and fixed allocation flow. Publish `PART6_READY` only when actual runtime dependencies exist.
4. **Hours 11–14:** integrate core paths and packaging; choose remaining questionnaire additions only where their dependencies work. Repair interface failures before the conditional import/team additions. Defer scheduling first if time is tight.
5. **At hour 14, freeze new features. Hours 14–17:** integration repairs, portable startup and focused acceptance evidence when authorized; update goal status honestly.
6. **Hours 17–20:** recovery buffer, handoff and user rehearsal. Repair broken core paths; no architecture swap or new platform dependency.

If the first complete path is not integrated around hour 6, cut stretch work immediately. Preserve evidence correctness, actual calculations, persisted decisions and portability. A numerical completion percentage never excuses a broken essential path.

## Handoffs and integration

- Root publishes shared contracts before lanes diverge. Root alone coordinates shared schema/lockfile/app-shell changes.
- The shared backend occupancy/forecast calculation is the first G17 deliverable, consumed by G09 pressure and later by the G17 chart. Implement it before completing pressure; do not wait for the dashboard or duplicate the formula in a rule.
- Each lane provides a small commit set and a handoff with exact branch/commit, changed interfaces, working behavior and unverified limits.
- Keep approved fixes on the lane's branch; the lead integrates coherent commits rather than making parallel edits to the same files.
- Spencer's next action and readiness are defined in `handoffs/part-6.md`. He does not need to read private assessments or prepare a presentation.
- No repository infrastructure or deployment action is implied by this plan. Optional remote hosting uses the same application artifact after a separately scoped runtime decision.
