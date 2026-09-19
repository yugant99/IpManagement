# Six parts, one integrated application

Planning budget: approximately 20 lead working hours, with Spencer's 6–8 hours overlapping. These are estimates, not 20 hours per agent. The scorecard and limits live in `COVERAGE.md` and `GOALS.csv`.

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

## Sequence

1. **Hours 0–1.5:** freeze contracts, a small fixture and file ownership; establish backend/frontend entrypoints and dependency locks. Spencer can prepare Part 6 against the documented contract.
2. **Hours 1.5–6:** deliver source import → saved inventory/observations → one computed finding → browser evidence detail. UI and rules use the same fixture IDs and response shape.
3. **Hours 6–11:** complete rule conditions and controls, capacity view and fixed allocation flow. Publish `PART6_READY` only when actual runtime dependencies exist.
4. **Hours 11–14:** integrate core paths and packaging. Repair interface failures before adding stretch work.
5. **Hours 14–17:** portable startup and focused acceptance evidence when authorized; update goal status honestly.
6. **Hours 17–20:** feature freeze, recovery buffer, handoff and user rehearsal. No architecture swap or new platform dependency.

If the first complete path is not integrated around hour 6, cut stretch work immediately. Preserve evidence correctness, actual calculations, persisted decisions and portability. A numerical completion percentage never excuses a broken essential path.

## Handoffs and integration

- Root publishes shared contracts before lanes diverge. Root alone coordinates shared schema/lockfile/app-shell changes.
- Each lane provides a small commit set and a handoff with exact branch/commit, changed interfaces, working behavior and unverified limits.
- Keep approved fixes on the lane's branch; the lead integrates coherent commits rather than making parallel edits to the same files.
- Spencer's next action and readiness are defined in `handoffs/part-6.md`. He does not need to read private assessments or prepare a presentation.
- No repository infrastructure or deployment action is implied by this plan. Optional remote hosting uses the same application artifact after a separately scoped runtime decision.
