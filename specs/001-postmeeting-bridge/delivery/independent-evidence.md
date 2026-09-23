# T025 independent evidence — candidate4 checkpoint

**State: IN PROGRESS; no T025 PASS claim.** This is an independent verification record for the exact candidate SHA `8eb3e231b7792fe8415455d2176e962b8f953d60`. Runtime work used disposable synthetic stores and loopback-only services. Application source was not edited. Credential values, configuration documents, raw databases, and full API exports are excluded from this repository. Sanitized summaries are in [`evidence/t025/`](evidence/t025/).

## Criterion matrix

| Criterion | Status | Observation at this checkpoint |
|---|---|---|
| Actual concurrent reservation race | PASS | Two barrier-started requests returned one `201` and one stale-review `409`; exactly one reservation persisted. |
| Authenticated browser, selected-domain list/detail/export | PASS | Fresh isolated Chrome context authenticated a disposable synthetic operator, selected `demo-core`, loaded inventory and prefix detail, selected a saved run, and downloaded a 2,359,059-byte domain export. |
| Browser memory, reload and revocation | PASS | Token absent from local/session storage after login and use; reload returned signed-out with blank password field. Disabling the disposable principal then issuing a protected request returned the UI to signed-out with blank field and no token in storage. |
| Wrapper negative cases | PASS | Invalid host, permissive token-file mode, malformed token file, symlink, wrong principal, expired token and wrong health domain failed before unauthorized action or with expected denial. |
| Notice legacy migration and immutable history | PASS | Legacy unbound notice renewed into a bound version; prior version/receipt remained readable, stale acknowledgement was refused, and route/eligibility transitions were separately retained. |
| Notice route change plus alarm escalation | PASS | Combined route change and age escalation produced one version increment; GET did not reroute; old recipient retained own old receipt; current recipient acknowledged the new version; changed reason conflicted; unrelated route edit did not renew it. |
| Full populated recovery compare/readiness | PASS | Same-config stopped restore compared all 32 tables equal, integrity check passed, schema/application IDs matched, six readiness booleans were true, and selected-domain reads succeeded. |
| Recovery mismatch, publication, cleanup and replacement failures | PASS | Manifest mismatch preserved target; injected publication/fsync/cleanup/replace errors were visible and reported exact retained scratch/preserved paths; failed active replacement left target unchanged. |
| Corrupt, unsupported, non-standalone and busy recovery refusal | PARTIAL | Manifest/snapshot mismatch, unsupported schema, non-standalone sidecar, and held state lock refused without target replacement. A separate integrity-corrupt snapshot refusal is not yet recorded. |
| Global callback denial and replay isolation | PASS | Domain operator callback and cross-domain replay were denied; denied replay exposed no receipt or batch identifiers. |
| Foreign detail/export isolation | PARTIAL | Foreign reservation, assessment, ticket and import detail reads returned non-disclosing `404`; a foreign export endpoint result is not yet separately recorded. |
| Mixed-domain raw envelopes | PASS | Mixed intended-domain envelope was refused before receipt/state change; duplicate intended row envelope was wholly refused. |
| Migration receipt identities/count equations/no active writes | PASS | Staged intended input: 55/55 accepted, 0 rejected, 0 duplicates; exact replay and changed-content conflict behaved distinctly. Assessment: 55 accepted = 0 added + 0 changed + 55 unchanged + 0 conflicting; one active-only object reported separately; no active inventory writes. Independent signoff succeeded and stale baseline was refused. |
| Migration invalid, duplicate, bounds and stale cases | PARTIAL | Duplicate whole-envelope refusal and stale-assessment refusal are recorded. A dedicated malformed-row/bounds matrix with receipt/no-receipt and state comparison is still needed. |
| Unknown evidence and saved DHCP measures | PARTIAL | An incomplete Central DHCP receipt produced 12 unknown findings; four previously anomalous findings became unknown, not healthy. Saved calculations are present, but a separate rendered saved-DHCP unit-label observation remains to be recorded. |
| Malformed schema-6 acknowledgement migration atomicity | PASS | Deliberately inconsistent `acknowledgement_version` made explicit migration fail; the clone remained byte-identical at schema 6 and the v7 history table was absent. |
| Recovery refusal for unsupported schema/non-standalone/busy | PASS | Separate disposable clones refused unsupported and sidecar-bearing restore inputs with unchanged target; a held exclusive lock refused backup with `DATA_IN_USE` and no snapshot. |

## Evidence limits and next cases

The only observed runtime evidence here is local synthetic evidence for this exact candidate. It does not establish a human portability rehearsal, production use, customer access, or deployment readiness. Exact outputs and injection details remain in the private T025 evidence root; Git contains only sanitized summaries.

Remaining before the verifier can adjudicate T025: independently run the integrity-corrupt snapshot refusal; foreign-domain export refusal; malformed-row and explicit bounds cases with before/after state; capture rendered saved DHCP units; then reconcile every matrix row against the T025 contract, package sanitized evidence, and send the exact candidate SHA and commit to Main Lead 6.0. Keep any unobserved criterion PARTIAL/NOT RUN.
