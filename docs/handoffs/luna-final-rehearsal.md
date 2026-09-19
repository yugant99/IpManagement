# Luna final native rehearsal handoff

Status: completed focused procedural evidence; a separate presenter-ready cycle-1 snapshot with pinned preset is prepared and independently verified through API/recovery plus one browser attempt. Saved-run selector interaction remains locator-unverified. This is not human presenter acceptance or portable Linux/container acceptance.

## Checkpoint

- Branch: `codex/luna-final-rehearsal-20260919`
- Base: `codex/stage-5-audit-acceptance` at `94a34b8a35d631b3b9b5bb987ba458f73484c324`
- Reviewed candidate: `289f53c7c5db1bd414c938add1ea207d591f9e64`
- Worktree: `/Users/yuganthareshsoni/Downloads/Ip_inventory-luna-final-rehearsal`
- Raw evidence root (private): `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-audit-artifacts/run-20260919-zzeadfai/final-rehearsal`

No application source was changed. The branch adds this sanitized handoff only.

## Observed path

- Initial native readiness: schema 5, static/data/process ready; scheduler disabled, config version 1, cycle 1 at `2026-09-01T06:00:00.000Z`.
- Initial run: `004246ef-9089-40ac-b029-a412d5c2d38d`.
- Central `.240.10` ghost: finding `60409eed-4098-48eb-8cb6-c0defaf227a3`, exception `4d7cd1b2-d85d-4eb0-8849-5881c94bf98d`. Escalation, handoff to `demo-approver`, acknowledgement, evidence-linked correction proposal `dc4ef177-1b96-461c-906d-f7013f7c586b`, independent approval, same-clock reconciliation `8614e9b9-0236-4014-9857-04ab757f87ad`, close → owner reopen → close were recorded.
- Lab metadata correction: prefix `a1526294-9c3c-5588-98b5-c0fa7cae2aa9`; version advanced and a reconciliation `bf718cfb-d6d7-4df1-883f-05d11dda4774` was saved.
- Controlled acquisitions: cycle 2 `e25f6397-0f9e-4257-8d9d-4e51f9553230`, cycle 3 `c8101c55-e53e-43cb-aa93-960c852da420`, cycle 4 `5b1e253c-7e7b-4bd1-b757-979685cc07fd` (North anomaly), cycle 5 `efadc3fa-b215-4f6a-b191-37892786d432` (North unknown/partial), cycle 6 `82e4a57f-d357-4153-814a-dc874cd64ba6` (North healthy and new Central `.243.10` ghost).
- Central `.243.10`: finding `ed9551be-2a8a-490a-9fdc-47a9dae687a6`, correction `0fc0e038-4632-453c-906d-f7013f7c586b`, reconciliation `ddd4afac-ca8a-435a-b60c-dee0586a3895`; both `.240` and `.243` were covered before closure.
- Allocation: request `a8ace63c-3893-465c-90b0-80840e073aae`, local allocation `68b33058-8ca3-4e71-8c76-eac7ef78545b`, candidate `10.40.2.3`; downstream status was explicitly `simulated_success`.
- Final cycle 7: operation `936322a6-e1de-4494-815f-2e31dcd7ea0c`, run `ab3ae7bd-5ed1-454c-9cc1-80d07f96d210`, clock `2026-09-02T18:00:00.000Z`. Central ghost evidence was `unknown` under stale/incomplete source evidence; the application did not reuse an older healthy result. Final preset revision: `fffa84479ab3406d119f068a416921d53a7222eaa024fe314d5d70dcc2b57831`.
- Initial preset revision: `7232911f9ebb408e473a951987667d00539ca8e3285aaa9128725431eef2b089`.

API request/response records, browser observations, semantic snapshots, exports and command logs are retained under the private raw evidence root. Named restore and browser records are `commands/final-restore.json` and `browser-restored-observation.json`; the browser observation after recovery visibly showed the restored synthetic inventory (60 prefixes) and the UI disclaimer that it is intended inventory, not live-use evidence.

## Snapshots and recovery

- Initial recovery target: `snapshots/demo-initial-cycle1.sqlite3`, SHA-256 `8f652f649c36af0a0d515098e3c2c32fea1a8a437eec3e2599b6978fea5e0239`.
- Presenter-ready recovery target: `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-audit-artifacts/run-20260919-zzeadfai/ready-cycle1-with-preset-v2/snapshots/demo-ready-cycle1-with-preset.sqlite3`, SHA-256 `ee8134aa583dbf4711251f8bcd23e9bec6305ce77672e40e7cd3def91f655b37`; cycle-1 run `004246ef-9089-40ac-b029-a412d5c2d38d`, preset revision `147f2054b8edf4f186bc3c8ac8b11d86bed4f08972f20e47da7cba763d6c71c6`, scheduler disabled.
- Fresh independent verification copy: `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-independent-ready-verification-20260919`; evidence includes browser rendering of 60 prefixes and the pinned preset, API readback of the expected revision/finding/schedule, stopped recovery and 17-table comparison. Saved-run selector interaction hit a locator timeout; no retry was made. Full note: `/Users/yuganthareshsoni/Documents/Codex/2026-09-19/luna-independent-reproduction-20260919/outputs/independent-agent-procedural-reproduction.md`.
- Final evidence snapshot: `snapshots/demo-final-evidence-cycle7.sqlite3`, SHA-256 `e5e50c01b4a7bc8a561b9ba4c2bcc96f317e165e3385b8e7ce39457148946a2d`.
- Restore completed while stopped: `database_replaced:true`, schema 5, `migration_required:false`.
- Rehearsal state was preserved at `data/ipam_demo.before-restore-20260920T012552-1896cd02967a4e18a754b50ec0ca27ed.sqlite3`.
- Restored state was left stopped after the final UI observation; scheduler remains disabled in the restored cycle-1 baseline. `snapshots/restored-semantic-comparison.json` compares 16 application tables plus `sqlite_sequence`; restored rows match the initial snapshot and the preserved final database differs as expected.

## Limits and defects

- This was an agent procedural reproduction, not a human presenter/recipient walkthrough.
- Prior historical-copy reproduction remains in the same note for provenance; the fresh ready-copy verification supersedes it for presenter-ready snapshot evidence. The browser selector limitation and human acceptance gap remain explicit.
- No portable Linux/container/recipient startup or external provisioning was established; downstream provisioning remained simulated.
- The first recorder restart did not persist its child after shell exit; a foreground owned session was used thereafter. This is a recorder/process-lifecycle defect, not an observed application defect.
- One intentional allocation attempt used occupied `10.40.2.2` and correctly returned `CANDIDATE_OCCUPIED`; the successful request used free `10.40.2.3`.
- One initial CLI attempt supplied malformed combined environment assignments and correctly returned `DATA_PATH_UNAVAILABLE`; the corrected commands completed backup and restore.
- The separate `.241` Central routing discrepancy and new-prefix missing-route policy remained visible and were not represented as ghost resolution.

## Lead/accounting routing

Send this checkpoint and raw-root pointer to Main Lead 2.0 (`01a0bb80-cf0d-7f60-8e46-1e825f42d276`) and the F6/F7 accounting lane. The evidence supports review of the bounded local observations; it does not by itself authorize questionnaire class changes or global completion.
