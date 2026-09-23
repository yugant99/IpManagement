# T021 offline API source review

Author: Claude Code `claude-opus-5-5` high, existing Max, session
`43675db1-2332-459d-9376-98a210e19298`. Independent reviewer: GPT-6 Sol high.
Common T021/T022 base: `cc4e281756b1847b1312d6b260b3f57bd7df0d98`. PR96.
Initial full source: `b57d9283b7ffdb24347afabf5706b4bd48c0e0ed`.
Final source: **`3007bf33dd3481f1b85723b0a1c4971036b5f089`**. Lead integration: `e6b76edaa9ae5b82a0c409fec151bf52168036bc`.

The complete reference covers the current HTTP route/role inventory, bootstrap and
configuration pins, errors, raw versus projected evidence, strict migration,
reservation, allocation, ticket and recipient-notice contracts, exact-key recovery,
current static occupancy, protected readiness/docs and global coordinator authority.
Examples are illustrative and unexecuted; vendor/provisioning interfaces stay absent
and ticket effects remain simulated.

Sol reviewed the complete document against the pinned source. Retained Opus fixed
all source findings and independently obtained closure at the final SHA:

- Protected health/acquire wrappers are future T024 requirements. Current wrappers
  are accurately described as legacy/unauthenticated. T024 supplies source/package
  preparation; actual builds, versions and runtime observations belong to T025.
  Context refresh never implies automatic mutation retry or a replacement key.
- Transaction authority distinguishes `write_operation` from the scheduler's own
  transactions and `authority_check`. Fresh checks refuse revocation/config changes
  already effective then; SQLite does not atomically fence an externally replaced
  config file after the final check. No stronger race guarantee is claimed.
- Ticket phase-2/3 AppError recovery pointers exclude 401/403/404. Clients retain
  original-context recovery information when a response omits pointers or is lost.
  Readback is manual and conditional on remaining uncertainty; a definitive current
  delivered/failed state needs no extra write. Original receipt and current state
  remain distinct.
- Parent `acknowledgement_version` alone never proves receipt; exact notification,
  own actor and timestamp evidence do. Default version 1 is not acknowledgement.
- The schedule quick reference distinguishes well-formed object refusal from
  possible request-validation 422. A dangling section reference was corrected.

A lead-only final prompt edit carries the user's stop-before-T024 instruction into
the copyable pickup; Sol included it in the reviewed final candidate. No remaining
source blocker was found. No tests, builds, imports, SQL/DB, application/browser or
runtime checks ran. T025 is unrun; no portable/human/customer acceptance, main merge,
questionnaire promotion or Tier B release follows from documentary source closure.
