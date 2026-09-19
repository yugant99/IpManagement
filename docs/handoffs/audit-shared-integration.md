# Audit response: shared schema, API and UI pickup

Stage 4 worker checkpoint for Main Lead 2.0. Scope: F1/F2/F3/F5 shared integration under the lead's audit-response contract. Global acceptance, final rehearsal, F4/F6/F7 accounting and main merge remain lead-owned. This report contains synthetic engineering evidence only.

## Frozen application

- Branch: `codex/audit-shared-integration`, from accepted main `a279f32df0ac7d2147b580dbff36dd88772bdeb2`.
- Application freeze: `01440664beac0b66850d01ad59c5a36dc147c617`.
- HTTP/browser-tested candidate: `437aa736b8c3260e15ef2f84ca347bf6c4f37985`.
- The only backend/frontend/fixture/dependency difference between those commits is the CLI migration help text adding v4. `python -m ipam_demo --help` was checked at the freeze. Application checks were not repeated for documentation/test merges.

| Frozen surface | Git object ID |
|---|---|
| `backend` tree | `14839081f82b5c6c35274bc2f22415ea04b5c21d` |
| `frontend` tree | `293ecd6c347c0d784c12bd76d961621c200b7d7e` |
| `fixtures` tree | `f7ae0533b3efa9fce618def206561a60d8d355ad` |
| `uv.lock` blob | `56671dad30939e0e1df3fdf0e44105316f15a3d1` |
| `pyproject.toml` blob | `931397380ed4f4cfa46e1c7737b0bcb5706faad8` |

Coherent component history is retained: schema/store/seed `7dc057c6b18b0b3f0c0425bb17d0b427c4908969`; correction API `5ed6986`; backend collection `7c2246826e41b38c525b0bd429dc1c2e3a8eeaf2`; F3 UI `ca3fa498` (PR #36); F5 UI `97a28432` (PR #39); F1 UI `7afbf6f0`; core state/CLI checkpoint `d6197df8`. See the separate metadata, correction and history handoffs for backend owner evidence.

## Changed behavior

Schema v5 adds `correction_requests`, a separate pool `capacity_history_version`, and additive exception current-evidence/lifecycle fields. Explicit migrations accept v1–v4; startup never migrates implicitly. Legacy history already invalidated by the former version guards stays ineligible. Latest exception pointers initially remain null and mean not refreshed, not healthy. Fresh seed uses named pool columns so the new history default applies. Required v5 columns are checked centrally.

The correction API exposes context, paged list/detail, proposal and independent decision routes. Writes share the existing immediate transaction/failure-audit mechanism. Create and decision replay headers retain the allocation conventions. Ordinary and scheduled reconciliation use the same backend correction linkage; no second calculation path or external remediation is added.

The new Inventory corrections tab retains exact ambiguous proposals/decisions in session storage. It shows every recorded discrepancy, the original finding, the first linked saved run after approval evaluated for comparability, and latest post-approval evidence separately. A missing or incompatible finding in that first run means unknown resolution; the link does not wait for comparable evidence. Exception UI separates original/latest evidence, operational disposition, open/closed lifecycle and renewed notifications, with owner-only close/reopen controls. The editor lists affected own/ancestor pools for structural changes and accurately explains preservation of eligible history on metadata-only edits. Metadata finding detail shows saved evaluated values/versions and matching audit provenance.

Post-freeze copy clarification: the first-result heading and reconciliation description were corrected to this exact linkage behavior. Only these two UI strings and this handoff wording changed; the application freeze and tree IDs above identify the earlier checked candidate. The lead repins the publication head for the final build/rehearsal; no service, schema or calculation logic changed, and no owner checks were repeated for this copy edit.

Independent review found two UI issues and both were corrected: an unbound older computed result could appear under a later selected correction (`0ef3859` removes that duplicate evidence); hidden tabs could retain a stale latest result after navigation (`700a08b` refreshes corrections/exceptions on activation while preserving exact retries). Evidence displayed while a tab stays open is explicitly labeled a loaded snapshot with a refresh action.

## Checks actually performed

- Shared schema check: fresh rich v5 seed; constructed populated v4 migration preserving existing inventory/metadata/schedule columns; conservative history backfill; foreign-key integrity; malformed v5 missing-column refusal. Passed on disposable stores, then removed those temporary stores.
- Connected TypeScript check and Vite production build passed. Python 3.12.10 and the retained read-only Node 22.14.0 executable were used with a fresh isolated backend environment/frontend dependency install. Lockfiles were unchanged.
- **27 focused HTTP operations passed** against a fresh rich synthetic store: pending proposal leaves inventory unchanged; creation replay; unauthorized decision with recorded failure audit; independent approval; decision replay without duplicate success audit; actual ghost resolution linked to reconciliation; new-prefix route-policy unknown; audited metadata correction; metadata-only p95/forecast preservation; original-run immutability; original/latest exception separation; immediate handoff retry after ownership changed; healthy close/replay; closed-action refusal; stale retry after a later acquisition; and successful feed cycle 2 after supported correction.
- Browser checks passed: submit `.241.0/24` route registration as requester; observe requester approval disabled; switch approver, approve, reconcile and inspect separate original/first/latest results; observe closed exception acknowledgement disabled and explicit owner reopen succeed; inspect accurate North DHCP structural versus metadata warnings; inspect saved Lab metadata/audit provenance. After a run created in Source evidence, returning to Corrections refreshed the latest result. Browser console warning/error query was empty.
- Backend owner reported **22 focused tests passed** at `7c224682`, with independent F1/F5 source reviews finding no actionable issue. These were not rerun by this worker.
- Core owner reported **3 focused state tests passed** at `d6197df8`: genuine populated v4 snapshot/restore/migration preservation, v5 full-table preservation and bounded refusal/reset checks. SQL sentinels establish storage preservation, not workflow execution. No original Stage 5 store was touched.

## Retained local evidence

Root: `/Users/yuganthareshsoni/Downloads/Ip_inventory-audit-shared/artifacts/audit-response` (gitignored).

| Artifact | Meaning |
|---|---|
| `api_check.py`, `api-observations.json`, `api-summary.json` | Focused HTTP recipe, 27 actual responses and assertions |
| `browser-summary.json` | Observed UI actions and exact run/request references |
| `final-corrections.json`, `final-exceptions.json`, `final-schedule.json` | Post-check persisted API state; scheduling disabled at cycle 2 |
| `server.log`, `state/ipam_demo.sqlite3` | Disposable verification process log and retained synthetic store |

HTTP source run: `1a64ddfd-74ce-44a7-884c-0a76c2d8e89f`; correction `f21362c2-3530-405e-aa40-fac99af5a315`; linked result `4f1826bc-9470-4ad7-8c13-81422a6c957b`. Browser correction: `0a91eae6-b42a-42c1-a5a0-41bd8b6bef29`; linked result `c73e066c-1e03-478f-a040-eedb7b978af3`; navigation refresh result `4f7e6099-6bfd-4f5c-9b39-5010e1d91ecd`.

The browser's content-export capability was unavailable. UI evidence is the recorded DOM observations and inspected screenshot, summarized in the manifest, not an exported page recording. The browser tab was closed. Local service `127.0.0.1:8766` stopped cleanly; its log records application shutdown complete. Scheduling stayed disabled. This is not the separate OS-shutdown-during-acquisition acceptance case.

## Remaining gates and next owner

Main Lead 2.0 should review the connected application and pin this frozen code for Stage 5's one final rehearsal and dedicated presenter store/runbook. Reuse sufficient checks above. S5-09/S5-15 missing-case observations, final F1–F7 dispositions, the 15-scenario catalog, 16 acceptance cases and 111-row accounting remain separately recorded by their owners. Historical Stage 5's 14 passes/two partials are unchanged by this report. Spencer retains portable packaging and recipient acceptance; no container, VM, cloud, deployment, customer acceptance or complete-catalog claim is made.

Draft lead pickup: “Review the Stage 4 shared integration application freeze `01440664beac0b66850d01ad59c5a36dc147c617` and its publication head. Check code-tree equality after any documentation-only integration, combine the backend/core reviews and focused evidence, then pin one exact candidate for Stage 5's final local rehearsal. Preserve the existing artifacts and ownership limits; do not repeat unchanged suites or merge PR #9.”
