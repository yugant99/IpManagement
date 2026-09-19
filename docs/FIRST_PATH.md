# First complete path: source and evidence walkthrough

This describes authored Stage 2 behavior and a source-reviewed fixture recipe. **No application import, migration, calculation, build or browser step below has been executed in this stage.** No observed run ID or screenshot exists. Runtime evidence remains pending explicit authorization.

## Dependencies and boundaries

Use the lead-approved foundation dependency from PR #5, then the Stage 2 branch/PR recorded in `handoffs/stage-02-report.md`. The separately owned fixture branch is `codex/part-2-synthetic-data`; the first-path inputs were published in commit `60df87025a9a76187638bcad1921981b851f6cbb`, unchanged in the final data-lane checkpoint `907f6e7bf32f23f36d270da49c3177b015c8bfae` ([PR #7](https://github.com/yugant99/IpManagement/pull/7)). Do not copy fixture generation into application code. The lead coordinates integration; this feature does not merge another owner's work or promote richer inventory.

The existing packaged seed has two scopes and six prefixes. The new first-path inputs refer to exactly those identities. Source imports do not insert, modify or delete intended inventory or allocations. Rich `inventory.json`, DHCP and expected-outcome files are outside the accepted Stage 2 format and return an explicit input error. One rule is implemented: G13 missing expected route, with G15 healthy/unknown controls. G05/G06/G07/G18 receive bounded contributions; their broader goals are not complete.

## Intended interaction after runtime work is authorized

Existing schema-v1 stores require stopped service and the explicit `python -m ipam_demo migrate` command; it recognizes the app identity, holds the existing data lock, adds only evidence tables in one transaction and advances to schema v2. Unknown versions remain unchanged. New stores use the same explicit foundation seed command and start with schema v2. Startup never runs the migration or seeds implicitly. See `FOUNDATION.md` for the inherited installation/runtime requirements and `STAGE2_API.md` for the concrete added interfaces. No reset, backup or restore command has been added; those remain core prerequisites for Spencer's Part 6.

Open the browser's first-path view and import, in this order, the three files listed under `first_path.default_inputs` in the fixture pack:

1. `fixtures/v1/first-path/inventory-policy.json`: source `synthetic-first-path-policy`, run `first-path-v1-policy`; six policies, explicit complete snapshots for North and Lab at `2026-09-01T00:00:00.000Z`. North DHCP and Lab require exact announcements; the other four prefixes explicitly do not.
2. `fixtures/v1/first-path/routing-north.json`: a positive route in North's fresh complete scoped view.
3. `fixtures/v1/first-path/routing-lab.json`: Lab's fresh complete scoped view, with zero records.

A successful upload shows a persisted receipt. Accepted/rejected/duplicate counts are exclusive and sum to input. A partial receipt is visibly incomplete. Raw rows, reject reasons, original envelope and source/run/record references remain available. The real ingestion time is separate from the fixed synthetic evaluation clock. Identical replay returns its original receipt and sequence; it does not replace a newer snapshot. Changed content under an existing identity is a conflict.

Use the explicit compute action. Overview, finding list and detail come from the same saved `run_id`. Opening an older run never reinterprets it using the latest imports.

## Why the expected result follows from input

These are design expectations from the source recipe, **not measured results**:

| Subject | Input and rule | Expected saved state |
|---|---|---|
| North `10.40.1.0/24` (`...b002`) | Exact announcement policy; same-scope IPv4 route active at the fixed clock | Healthy |
| Lab `10.40.1.0/24` (`...b006`) | Exact announcement policy; fresh complete empty Lab view | Anomalous, high severity |
| Four other intended prefixes | Explicit `expects_announcement: false` | Not applicable; not a health claim |

The North and Lab CIDRs have identical address text. North's route cannot satisfy Lab's policy because `scope_id` differs. Expected default overview: one anomalous, one healthy, zero unknown and four not applicable, total six. Those totals must be calculated from saved findings; the UI does not contain fixture answers.

Controls are later imports of the same declared source with distinct run identities, followed by an explicit new run:

- `routing-lab-partial.json`: an empty incomplete view makes Lab unknown. It must not reuse the complete predecessor.
- `routing-lab-stale.json`: covered end is ten minutes before the clock, beyond the five-minute routing freshness limit; Lab remains unknown.
- `routing-lab-recovery.json`: a new fresh complete view contains an active exact Lab route; Lab becomes healthy in the new run. The previous anomalous run stays unchanged. This is presence evidence, not external remediation.
- `inventory-policy-lab-partial.json`: a newer explicitly scoped policy snapshot omits Lab's policy; Lab becomes unknown rather than falling back per prefix. North's policy snapshot remains its own latest declared source/scope view.

Apply controls individually in the documented order or use separately initialized stores when comparing isolated scenarios. Replaying the original batch cannot restore it as newest; use an explicit new source-run identity. No rule, importer or UI reads `expected-outcomes.json`. Multiple competing policy/routing sources declaring a scope yield unknown authority ambiguity, so do not mix rich-pack and first-path feed identities as if they were a single authority.

## Remaining evidence

Source review establishes intended wiring, not executable correctness. Pending: authorized schema-v1 preservation/migration observation, actual receipts and replay/conflict behavior, computed default/unknown/recovery runs, half-open interval and scope controls, API/detail agreement, frontend type/build and browser interaction. No real network source, subscriber telemetry, traffic, allocation workflow, capacity/forecast, six-rule completion, packaging or persistence acceptance is claimed.
