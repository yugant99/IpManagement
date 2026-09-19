# Synthetic IPAM pack

Version 1 is committed in [`v1/`](v1/). Generate it with Python 3.10+ and the standard library:

```sh
python3 fixtures/generate.py
```

Run from the repository root; the script resolves its own output directory. It writes only its named generated files under `fixtures/v1/`, reports each file/record count, and lets any read/write failure stop execution visibly. Generation is not transactional: a failed run can leave partial output; rerun successfully before publishing. It does not clean unknown files, touch application state, install dependencies or contact a network.

The default set has four scopes, 60 prefixes, eight pools, one preserved intended allocation, 2,000 lease intervals and 200 routing observations. Fixed clock: `2026-09-01T00:00:00.000Z`; history begins `2026-08-02T00:00:00.000Z`.

- [`v1/pack.json`](v1/pack.json): explicit default/opt-in file lists, actual generated counts, byte sizes and file SHA256 digests.
- [`SCHEMA.md`](SCHEMA.md): concrete file and field contracts; observation/policy formats are proposals for Stage 2.
- [`../docs/SYNTHETIC_DATA.md`](../docs/SYNTHETIC_DATA.md): scenarios, numeric expectations, provenance and integration boundary.
- [`v1/expected-outcomes.json`](v1/expected-outcomes.json): independently authored comparison oracle, **never a detection input**. The generator neither reads nor writes it.
- [`v1/foundation-baseline.json`](v1/foundation-baseline.json): unchanged published Stage 1 seed snapshot; the generator reads it but never overwrites it.
- [`v1/first-path/`](v1/first-path/): separate Stage 2 recipe for the existing foundation ledger: North route present, Lab route absent, and partial/stale/recovery controls. Use `pack.json.first_path`'s explicit lists.

Do not glob every JSON file into an importer. Only `pack.json.default_inputs` describes the default source set. `opt-in/` contains intentional partial/stale/invalid variants and a changed-replay conflict. The preserved baseline is a provenance dependency, not an additional batch to apply alongside the richer inventory.

No app import, rule execution, tests, smoke checks, builds or infrastructure operations were performed for this pack. The existing Stage 1 CLI does not accept these richer files.
