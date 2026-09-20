# Easy-wins existing-path evidence

This directory indexes focused local evidence captured against candidate
`852010a311065a9cc0258fc4e3f5c1c1a889329a` on 2026-09-20. Raw JSON, CSV,
SQLite and runtime logs remain outside Git under the disposable root recorded
in `docs/handoffs/easy-wins-evidence.md`.

The reproducible entrypoint is
[`scripts/evidence/easy_wins_existing.py`](../../../../scripts/evidence/easy_wins_existing.py).
It starts the exact checkout's API on loopback, uses a fresh rich synthetic
store, and compares only the requested report, audit and import paths.

The run proved:

- RFP-006: saved run `249eb21b-4e0e-4ddc-bc87-73119b2a1b80`, preset revision
  `1ee51bd935bbdd36958274393ff4cdb73aa031629aa8e0ad6f340d9845e1efd2`,
  nonempty filters `scope_id=2c4a5913-e80c-53e9-9ba1-fd6c87ec6f4c` and
  `evidence_state=healthy`, ordered columns
  `subject,scope_id,evidence_state,rule_id`, and 26 matching CSV rows.
- RFP-078: failed request
  `bd0096fc-678c-4b68-8124-ae1e6c9f7b4d`, audit row
  `f0dd07c2-36e5-45e8-bd0e-3802a776b660`, `audit_recorded=true`, and a
  14-row audit CSV whose selected failure row matched the audit list fields
  and details.
- RFP-033: batch `a6eb653d-08e5-4b2b-9b5e-23323f853d73`, source record
  `normalization-ipv6-001`, raw input CIDR
  `2001:0DB8:0080:0000::/64`, canonical typed CIDR
  `2001:db8:80::/64`, and offset timestamps canonicalized to
  `2026-09-01T00:00:00.000Z` while the original envelope/row was retained.

These are synthetic/local observations only. They do not demonstrate a custom
dashboard designer, a complete system configuration audit, heterogeneous live
integrations, cleansing policy, or portable/deployed acceptance.
