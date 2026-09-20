# Bounded easy-win lead review

Main Lead 3.0, task `01a0c0c1-3952-7720-93c8-ff49192b8e13`, coordinates this 2026-09-20 follow-up under the [accepted contract](../EASY_WINS_CONTRACT.md). This is additional local synthetic evidence, not a new Part 7 or a replacement of historical acceptance. Portable startup/persistence and recipient proof remain deferred; `PART6_READY=no`.

## Review and evidence

The lead reviewed the production changes to request logging, import reconciliation, reports, inventory filters and source catalog, plus the changed UI and focused checks. Review corrections addressed staged inventory receipts without ordinary source/coverage fields, catalog refresh/pagination/provenance links, confirmation text tied to the returned import result, HTTP request-ID audit separation, and callback failures after a committed import. Unused backend summary code was removed; report checks now exercise the actual export and preset helpers. The saved-run summary derives its counts from the selected saved findings without inferring pressure from unknown evidence.

The evidence-only [PR #56](https://github.com/yugant99/IpManagement/pull/56), final head `0fc519afc81751e390f1e7080a426daf2cc9ea39`, is accepted and merged at `78fbb98544cc6a329f76a6c6e81ee83de42dac0c`. Its actual application observations use unchanged baseline `852010a311065a9cc0258fc4e3f5c1c1a889329a`; a later runner-only safety correction was source reviewed without rerunning the application. [Evidence handoff](easy-wins-evidence.md).

- RFP-006: meaningful saved filters and an ordered non-default column selection produced 26 CSV rows matching the saved selection and pinned preset revision.
- RFP-078: a real rejected preset change generated a retained failure audit. Audit CSV contained 14 rows, with the selected failure matching the audit list and HTTP request reference.
- RFP-033: accepted noncanonical IPv6 and timezone-offset timestamps became canonical typed values while original raw/envelope forms remained available.

The lead independently read the retained runtime identity and startup/shutdown log, summary, failed-attempt response and raw/typed record, and checked both CSV hashes against the handoff. The evidence uses a disposable store; original acceptance stores were not used. The runner now refuses an existing output root and checks port availability and its owned child's startup before mutation.

## Changed-candidate acceptance

Production code at `506c1379ab434b2970506d9727fd647d33fe4287` is accepted on the focused observations below; later publication commits change only tests/evidence documentation. Final [PR #58](https://github.com/yugant99/IpManagement/pull/58) head `7552680166b5df43ddb7d09505c6b7ded3316032` merged normally as `1782509b01deb7b83d8bff0731e6e3381274b6fa`. The integration retained coherent sibling commits by cherry-pick; contributor branches remain available. Domain PR #55 is closed as superseded by the reviewed integration; its branch is preserved. PR #9 remains OPEN / NO MERGE.

- Twelve unique focused backend checks were exercised: eleven in the initial combined run, then six import/logging checks after adding held-lock coverage and refining post-run rollback. Do not describe this as an observed combined twelve-test run. The failure probe raises after a real run write, observes its rollback while the import remains, then successfully retries. Busy is a controlled held shared lock, not a live concurrency/endurance claim.
- TypeScript/Vite build and the connected browser observations passed. Build used Node 23.11.0, outside the declared supported Node range; it establishes this local build only. Docker and supported target-runtime builds remain unverified. The only browser console error was a missing favicon (404).
- Ordinary routing import created batch `53e7a368-9b2b-4704-a60a-e8892122b761` and run `48f45365-389f-4970-a7ba-716497b58758`; identical replay reused the saved run. Staged inventory visibly returned a separate skipped reconciliation result and left the active ledger unchanged.
- IPv6 preset revision `ad9303d7575ae987c0c021987a6c57888bb5eac7413a6454ca91cfa73a67b319` produced 27 family-6 findings and zero pool calculations. The lead compared every CSV row with the direct JSON export; the findings API also returned 27.
- Combined domain/region/scope/family filters produced 12 North prefixes. Searching `10.40.2.1` preserved both `10.40.0.0/16` and `10.40.2.0/28`. The catalog displayed evaluated time, routing freshness/completeness and staged non-active/unknown evidence, plus receipt links/reload/pagination.
- The lead independently read the stopped disposable store to match the browser's saved-run summary: one anomalous finding, 108 unknown findings, four affected scopes and zero pressure pools. IPv4 filtering reduced unknown findings to 91; unknown results were not counted as pressure.
- Supported CLI launch (`python -m ipam_demo serve`) produced a successful schedule access log, response header and persisted audit detail sharing HTTP ID `dbcb9bb7-e6aa-417d-93b3-9fc048234167`. [Exact sanitized correlation](../evidence/easy-wins/import-logging/schedule-correlation.txt). Direct Uvicorn bypassed the CLI logging setup during an earlier check; no unconditional logger override was retained. A prior successful schedule row and its CSV details were also independently compared with the stopped store.

See the [integration handoff](easy-wins-import-logging.md), [domain/browser evidence](../evidence/easy-wins/domain-sources/README.md) and [report helper evidence](../evidence/easy-wins/reports/focused-check.md) for commands and artifact locations. The disposable service on port 8765 was stopped; the lead observed no listener afterward. Existing presenter-ready stores and historical snapshots were not promoted or replaced.

## Questionnaire decision

The lead privately reread only the nine affected original workbook clauses, then obtained an independent Luna/medium accounting challenge and final recount. RFP-005/006/026/035/043/077 become **Demonstrated** within the explicit local synthetic limits. RFP-033/036/078 stay **Partial**: normalization is not corrective cleansing, an imported-source catalog is not system discovery, and audit export is not compliance reporting.

Current accounting is **38 Demonstrated / 17 Partial / 10 Documentary / 46 Missing = 111**, with 111 unique row IDs. The previous 32/22/10/47 checkpoint is preserved in history. No aggregate fully-satisfied percentage follows. The separate workbook's earlier projected gains and rows 090/092/104/106 were not silently adopted.

## Preserved boundaries

The original Stage 5 record remains 14 passes/two partial cases, with its separate accepted addenda. The 15 catalog scenarios and 111 questionnaire rows remain different sets. This follow-up does not establish automatic discovery of existing systems, corrective cleansing, compliance certification, live provisioning, trusted enterprise identity, scale or customer Phase 1/2 outcomes. Human training/presenter practice and recipient acceptance remain unobserved. No Docker commands, image pulls, VM/cloud work, deployment or spending was performed.
