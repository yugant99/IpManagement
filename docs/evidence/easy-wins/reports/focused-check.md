# Easy-wins reports focused evidence

Code checkpoint: `a9c9fab` (`Test real family export and preset helpers`). Current branch is `codex/easy-wins-reports`; the provenance-doc commit records its updated head separately.

Command:

```text
PYTHONPATH=backend python3 -m unittest tests/test_easy_wins_reports.py
```

Observed result: 3 tests passed.

Covered behavior:

- family `4` selects only IPv4 finding subjects and calculations through the actual JSON export helper;
- invalid family values are rejected with `INVALID_INPUT`;
- an older preset without `family` retains its stored filter shape and stable revision when read;
- the actual preset CSV helper applies a saved `family=6` filter.

Not covered here: app.py HTTP wiring, persisted report-preset round trip, browser interaction, or a frontend build. The frontend build attempt stopped before compilation because `tsc` is not installed in this checkout. Inputs are synthetic/local and do not establish production or customer acceptance.
