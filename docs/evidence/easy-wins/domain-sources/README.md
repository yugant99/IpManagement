# Easy-wins focused evidence

This directory records the bounded source checks for the domain/source slice.

- `PYTHONPATH=backend python3 -m unittest tests.test_easy_wins_domain_sources` passed three focused scenarios, including staged receipt safety and latest partial selection.
- The integrated frontend build passed after `npm ci` from the unchanged lockfile; Node 23.11.0 is outside the repository's declared supported range.
- Connected browser and integrated endpoint evidence is recorded below; no deployment evidence is claimed.

## Minimal connected browser observation

Observed on the integrator-owned disposable localhost candidate after frontend build completion: integration code chain ending `506c137`, task owner `01a0c0f0-5735-7e52-9f5a-ec45ac8ac99c`, `http://127.0.0.1:8765`. Only the bounded selector, source evidence/catalog, staged import callback, and saved-run report actions below were exercised:

- Intended inventory exposed Network scope, Domain, Region and Address family selectors plus Clear filters. North + `demo-core` + North + IPv4 returned 12 prefixes. IP query `10.40.2.1` returned two scoped results: containing `10.40.0.0/16` and child `10.40.2.0/28`.
- Source Evidence exposed the opt-in “Reconcile after this import” checkbox. Uploading the synthetic inventory envelope with it checked showed import saved separately from reconciliation: `skipped`, with staged inventory not promoted or reconciled.
- The receipt showed “Inventory staged — active ledger unchanged” and no coverage. The Imported-source catalog showed its evaluated clock, non-discovery limitation, fresh/complete routing coverage, and staged row as “Not applicable — staged candidate”, `not_applicable` freshness, and unknown completeness.
- Reload catalog was visible and the catalog refreshed after the staged import; no active inventory promotion was inferred.
- Saved-run summary showed 1 anomalous, 108 unknown, 4 affected scopes and 0 pressure pools. Selecting IPv4 changed unknown to 91 and the visible export URL included `family=4`; “Save current run and filters” was visible.
- Browser console contained one non-functional `/favicon.ico` 404 and no warnings. No broad E2E was run.
