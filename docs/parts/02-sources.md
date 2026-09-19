# Part 2: sources and assessment

Owner: data agent. Core goals: G05–G08. Branch: `codex/part-2-sources`.

## Win

Load reproducible synthetic records and show where they came from, what was rejected and whether there is sufficient evidence to calculate a finding.

## Inputs and owned work

Use Part 1's scoped model. Own `fixtures/` and assigned import/export modules; coordinate schema changes with the lead. Keep expected scenario answers separate from rule inputs.

Seed synthetic intended inventory, DHCP lease intervals and routing observations with fixed IDs and a fixed demo clock. Cover healthy, six Pool Watch conditions, actual conflict, valid overlap, missing metadata, invalid input and stale/incomplete source cases.

## Output

Visible import counts/reasons, immutable raw record references, source ownership/authority/freshness/coverage, typed observations, and an illustrative assessment export. Accepted DHCP/routing imports can change rerun outcomes. A changed intended baseline remains staged; do not overwrite approved local allocations.

## Acceptance and limits

Accepted plus rejected plus duplicate records account for every input, with exclusive statuses. Identical whole-batch replay returns its original receipt with no new effects. Required rejected observations make effective completeness false. Publish the selected observation batch and effective coverage for Part 3; never silently fall back to an older complete batch. Core input is versioned JSON, not arbitrary format support. Read the identity/import sections in `docs/IMPLEMENTATION_DECISIONS.md`.

Missing source data remains unknown. Assessment workflow/maturity sections use fictional examples or "not assessed"; they cannot claim real organizational discovery. No live connectors, subscriber identity or arbitrary file-format platform.

Handoff: fixtures/schema, source-run IDs, fixed clock, expected outcomes for independent comparison, import errors and limits. Part 3 must not have to reverse-engineer the source format.
