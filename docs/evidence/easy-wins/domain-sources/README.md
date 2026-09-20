# Easy-wins focused evidence

This directory records the bounded source checks for the domain/source slice.

- `PYTHONPATH=backend python3 -m unittest tests.test_easy_wins_domain_sources` passed two focused scenarios: domain/region intersection for prefixes and pools, and receipt provenance/partial catalog state.
- Frontend build was attempted with `npm run build`; it was blocked before compilation because the checkout has no `frontend/node_modules/.bin/tsc`.
- No browser, integrated endpoint or deployment evidence is claimed. The catalog endpoint and API query wiring are pending the app owner’s `app.py` integration.
