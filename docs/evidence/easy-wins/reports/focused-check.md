# Easy-wins reports focused evidence

Candidate: `codex/easy-wins-reports` (local worker checkout).

Command:

```text
PYTHONPATH=backend python3 -m unittest tests/test_easy_wins_reports.py
```

Observed result: 3 tests passed.

Covered behavior:

- family `4` selects only IPv4 finding subjects;
- invalid family values are rejected with `INVALID_INPUT`;
- saved-run summary retains run ID, saved timestamp, demo clock and filter provenance, and counts only anomalous/unknown findings plus anomalous `pool_pressure` subjects in the selected family/scope.

Not covered here: app.py HTTP wiring, persisted report-preset round trip, browser interaction, or a frontend build. The frontend build attempt stopped before compilation because `tsc` is not installed in this checkout. Inputs are synthetic/local and do not establish production or customer acceptance.
