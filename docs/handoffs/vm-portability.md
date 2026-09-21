# VM portability experiment — deployment-owner handoff

**READY FOR PROJECT-LEAD REVIEW — Stage 5 / Part 6.** Bounded deployment,
recovery and transfer evidence; no global acceptance or questionnaire decision.
Main Lead 3.0 owns review, merge, accounting and provider cleanup.

## Source, ownership and authorization

- Worker task: `01a0c163-9686-7001-81d1-d6abbfad41ec`, deployment owner.
- Worktree: `/Users/yuganthareshsoni/.codex/worktrees/6380/Ip_inventory`;
  branch `codex/vm-portability`. Owned changes: this handoff and `docs/RUNNING.md`.
- Exact deployed source: **`eab1d3376633bf3280ff7bd8834fe46c88353d9a`**.
  One baseline build, zero rebuilds, no application or packaging source repair.
  Publication changes are documentation only; no unmerged runtime dependency.
- The explicit user-authorized VM experiment superseded historical no-cloud/
  no-Docker wording only for the sole existing DigitalOcean Droplet `602245599`.
  No local Docker, additional VM, public app ingress, infrastructure creation,
  self-merge or worker deletion of provider resources occurred.
- Evidence potentially relevant to RFP-090/020/023 is submitted for lead review.
  This worker changes no row classifications or global status.

Private evidence root (not committed):
`/Users/yuganthareshsoni/Downloads/Ip_inventory-vm-evidence/20260921T0030Z`.
`HANDOFF.md` there contains provisioning/SSH details. Provider credentials and
private-key contents were never copied to the VM or evidence bundle.

## Runtime identity and isolation

Ubuntu 24.04.4 LTS, kernel `6.8.0-124-generic`, Linux x86_64/amd64, 2 vCPU,
4 GB RAM and 80 GB local disk; Toronto `tor1`. Docker Engine **29.8.1**,
containerd **2.3.5**, Compose plugin **5.5.1**, host Python **3.12.3**.
The old runbook's v2 wording was not the actually installed Compose version;
the existing `docker compose` wrappers worked without reinstalling or rebuilding.

Image runtime Python **3.12.10**, FastAPI **0.141.1**, Uvicorn **0.50.1**;
Node build **22.12.0**, npm **10.9.0**, uv build **0.7.13**, Vite **8.3.0**.
The committed Python/npm locks were consumed unchanged. Full installed Python
versions are in `remote-evidence/runtime-versions.json`.

| Identity | SHA-256 |
|---|---|
| Exact public Git source archive | `2bc3ecec471d8f90b3aec0c8a3537a4d0f6e06c8b951f26eb16a3db499196d7c` |
| `uv.lock` | `fe1cf1c2db576fba3addfa775b77f40266ba21e3231b7ebc650fe39b21e5c7d2` |
| `frontend/package-lock.json` | `03db1e10ba940f0dbd95af31a96226125502a0b3caf2e61d67c81dd697de4529` |
| Docker-reported image ID / OCI index digest | `68c18cee17adcc6baa17f95a2ef122286d88ee1e131f5f2539707f6276dae69e` |
| Runtime image manifest | `a9139c3528923a3a33f15253218dc4b8ce37e9c79119b86640aa4b5104c60aaf` |
| Runtime image config | `1d9f1f111f2831a18583c7d35b9191744f70aba07b233f9334a70af18641393d` |
| Exported `image.tar` | `077811e3fbe26cd2c29403e20c20e97eb4f1af9c86ef2de0c462261b000f9730` |
| Populated baseline snapshot, 11,558,912 bytes | `dd03d3ed68e904b90c9a49f5a4c429f9faff6fdeac71fbef06997cac7ee1908b` |
| Preserved prior-target snapshot | `13508ec50e02f1e82208691edecd0b177148c1c5e25da93ec61d43dac9cde776` |
| Fresh native transfer snapshot | `1367c93c073ab2716c8253e3452bb036fcaae402586dcbe927aaa759f65bbb79` |

Build-resolved base digests (tags remain mutable; use the exported image for
this exact artifact):

- `python:3.12.10-slim-bookworm`:
  `fd95fa221297a88e1cf49c55ec1828edd7c5a428187e67b5d1805692d11588db`.
- `node:22.12.0-bookworm-slim`:
  `35531c52ce27b6575d69755c73e65d4468dba93a25644eed56dc12879cae9213`.
- `ghcr.io/astral-sh/uv:0.7.13`:
  `6c1e19020ec221986a210027040044a5df8de762eb36d5240e382bc41d7a9043`.

Fresh-engine inspection showed no volumes or containers before the baseline;
`ipam_demo_data` was reserved for this experiment. Project names alone do not
isolate that explicitly named global volume. Subsequent exact-source copies
changed only `volumes.ipam_data.name`; each also used a distinct project:

| Remote source copy | Project | Volume |
|---|---|---|
| `/root/ipam-baseline` | `ipam-demo` | `ipam_demo_data` |
| `/root/ipam-recovery` | `ipam-recovery` | `ipam_vm_recovery_20260921` |
| `/root/ipam-recipient` | `ipam-recipient` | `ipam_vm_recipient_20260921` |
| `/root/ipam-native-transfer` | `ipam-native-transfer` | `ipam_vm_native_transfer_20260921` |

Exact Compose diffs and mount inspections are exported. Recovery Compose hash:
`56c999866cf716744512568ee36a6947e6778124e4dd97ed1722caadb7f4e5a9`;
recipient Compose hash:
`779e1a3eaa412c8097d7c0f866ad47f6eadf196044343e615ca545d4070d4ec5`.

Key-only strict-host SSH succeeded; server password authentication was disabled.
The firewall retained SSH-only ingress from the authorized source address.
The app published **127.0.0.1:8000** only; the local SSH tunnel used previously
free **127.0.0.1:18000**. Native Atlas on local8000 and retained acceptance stores
were untouched. Runtime inspection established uid/gid10001, writable `/data`,
read-only root, dropped capabilities, no-new-privileges and `/tmp` tmpfs.
Compiled UI, inventory/policy, eight observation files and installed
`ipam_synthetic_feed` were present; their file hashes were exported.

## Actual bounded observations

The baseline `build.sh` completed once, then `seed.sh`, `start.sh`, `health.sh`
and `acquire.sh vm-baseline-cycle1` succeeded. Rich seed produced4 scopes,
60 prefixes,8 pools and1 initial allocation. Manual cycle1 imported9 batches
and saved run `af830c8f-bdd7-481a-af52-d947aabf91b2`; scheduling remained disabled.
All process/schema/data/static readiness flags were true with HTTP200/schema5.

CUA operated the real compiled Atlas UI through the tunnel; direct API evidence
used that same tunnel and saved raw request/status/headers/body:

- Combined North scope/demo-core/North region/IPv4 filters returned12 prefixes.
  IP search `10.40.2.1` retained `10.40.0.0/16` and `10.40.2.0/28`;
  detail showed stored scope, pool, owner and initial assignment. Cleared filters
  plus IPv6 returned9 prefixes.
- The actual saved-run selector displayed the cycle1 summary:11 anomalous,
  0 unknown,3 affected scopes and2 pressure pools. A UI-saved IPv6 preset removed
  two columns; its revision-bound CSV returned27 rows with the selected six
  columns and same run ID. The UI requested its CSV download; retained CSV bytes
  came from the corresponding API endpoint, not a claimed browser download file.
- Imported-source catalog rendered source identity, scope and evidence limits.
  Reposting the current routing envelope with opt-in reconciliation created
  run `e71132fa-a287-4dd9-92bd-bd7f7e334333`; API and UI replay reused it with
  no new ingestion sequence. The first callback used an already imported cycle
  envelope, so this does not claim a new-upload callback branch beyond prior evidence.
- Requester Mira created exact candidate `10.40.2.3`; Mira's approval attempt
  returned403 with `audit_recorded:true`. Independent Rowan approval persisted
  the allocation and success audit. A deliberate downstream simulation failure
  remained visibly separate as `simulated_failure` while local outcome was allocated.
- Exception acknowledgement succeeded, a correction proposal for
  `10.80.241.0/24` was independently rejected, and disabled six-hour schedule
  settings saved as configuration2 with null next due. Corresponding views were
  accessed; these are representative actions, not a repeat of exhaustive prior flows.

Restart and restored/recipient reads retrieved these same logical identities:

| Record | ID |
|---|---|
| Request | `53e85b9f-6df3-4c40-950d-96012ea51851` |
| Allocation | `93056b23-7f18-4b49-946a-d8d311e46ef9` |
| Approval audit | `74601801-65f1-4a28-91d0-8c2f865b578a` |
| Refusal audit | `d5668ea4-e3d1-4835-b79f-974c316efbd9` |
| Request audit | `cc46e42b-cde2-472d-89e0-b2798a9183ca` |
| Rejected correction | `a201ea71-4ef9-433d-b619-b42e0763e50a` |

## Stopped recovery and timing

After baseline stop, `backup.sh baseline-populated.sqlite3` and
`snapshots.sh export baseline-populated.sqlite3 /root/vm-evidence/baseline-populated.sqlite3`
succeeded. The second volume was richly seeded and changed through the API:
prefix `41aca2b0-ec1d-4f64-8d21-c5af0ab0b003` gained custom field
`recovery_marker=vm-prior-target-20260921`, audit
`62497382-e9eb-47b0-a6ec-51ae5b6849eb`.

After stopping that target and importing the snapshot, actual
`restore.sh baseline-populated.sqlite3` returned wrapper stderr/exit2.
The stopped target's before/after SHA-256 matched. No fabricated core JSON
refusal is used. Confirmed restore reported `database_replaced:true`, non-null
`preserved_database`, schema5 and `migration_required:false`.

`RECOVERY_PROTOCOL.md` was written before timing. Its local demonstration
objective was **under120 seconds**, starting immediately before the confirmed
restore subprocess and ending at the first HTTP200 health response with all four
readiness flags true. Python `time.monotonic()` measured:

| Milestone | Seconds from start |
|---|---:|
| Restore command complete | 1.726 |
| Start command complete | 2.322 |
| Full readiness | **4.427** |
| Later logical-ID comparison, separate duration | **1.557** |

Provisioning, installation, image build/load, transfer/import/hash checks,
prior-target preparation and refusal were excluded. This is not outage-to-business
recovery, a customer SLA, or a general under60-minute recovery guarantee.
Read-only inspection of the preserved database found the exact marker and audit;
the restored working database lacked that prior-target marker and retained the
baseline allocation/audit/run IDs.

## Recipient reproduction and native transfer

`recipient-transfer/` contains `source.tar`, `source-commit.txt`, `image.tar`,
`image-id.txt`, baseline snapshot and `SHA256SUMS`. On the same authorized host,
checksums were verified, source extracted into a fresh directory, `docker image
load --input image.tar` completed, and the reported image ID matched. A third
isolated volume imported/restored the snapshot, started ready, and retained the
same IDs after its own stop/start. No recipient build or image pull was needed.
This is **agent procedural reproduction on one engine**, not independent-host
or human acknowledgement, practice or training.

A separate new native macOS14.5 arm64/Python3.12.10 store used the exact extracted
source, rich seed and an audited domain-function metadata edit. No native server
was started. Its marker `native-macos-to-linux-20260921` and audit
`97d64d82-8651-41d9-9f06-e25c8a0e5127` were captured in a stopped snapshot,
transferred with matching hash, and restored on a fourth isolated VM volume.
The deployed API returned the same marker/audit and all readiness flags true.
This demonstrates that particular snapshot transfer, not ongoing hybrid operation,
network integration, concurrent synchronization or ARM container support.

## Evidence, issues and remaining limits

Private evidence pointers (relative to the root above):

- `01-install.*`, `02-baseline-build.*`, `05-start-after-harness-fix.*`:
  raw installation/build/start commands, output, exit and monotonic durations.
- `08-*` through `29-*`, `ui-*.txt`, `ui-*.png`: API bodies/headers and CUA
  DOM/screenshots. `19-custom-export.body` is the retained customized CSV.
- `31-restarted-*`, `39-restored-*`, `41-recipient-*`, `43-recipient-restarted-*`:
  logical-ID comparisons and separately recorded comparison durations.
- `remote-evidence/`: exact refusal stderr/stdout/exit and before/after hashes,
  recovery protocol/timing, preserved-marker result/snapshot, native transfer
  result, image/container inspections, runtime versions, asset hashes, final
  app log and all four stopped-volume archives under `volumes/`.
- `recipient-transfer/SHA256SUMS`, `remote-evidence/SHA256SUMS`:
  locally rehashed **44 matching files**; `verified-transfer-hashes.json` records
  the worker comparison. Lead independently verified the same exports.
- `ISSUES.md`: observed symptoms, bounded diagnosis and response.

No application deployment defect was established. The first SSH `bash -s`
harness stopped after seed because Compose consumed its remaining stdin; the
private harness was corrected and execution resumed at start without reseed or
rebuild. A frozen routing fixture was correctly refused because its clock did
not match the acquired scenario; the current cycle envelope succeeded. Browser
selector/clear-filter handling needed adjustment, with no source defect established.
Some wrapper messages literally name the default volume even when the source-copy
volume differs; actual configuration/mount evidence governs identity.

Clock discrepancy is preserved, not corrected: local installation start
`2026-09-21T00:36:25.754172+00:00`, provider creation
`2026-09-20T21:29:08Z`, final VM clock `2026-09-20 21:48:22 UTC` during the local
`00:50:56` final export operation. External HTTP headers were cached (`Age:47000`)
and cannot resolve the clock discrepancy. All elapsed recovery claims use monotonic time.

Earlier exhaustive functional evidence is reused. This run did not exercise
reset, bad mounts, hot backup, enabled-schedule recovery, crash/failover/endurance,
public TLS/authentication, live integrations, performance/scale, orchestration,
complete license notices or human training. Native core reset/diagnostic evidence
remains separately scoped in [STATE_OPERATIONS.md](../STATE_OPERATIONS.md).
Initial removed-container application logs were not separately exported; raw
HTTP/command evidence and the final container log are retained.

All VM execution/export finished before local00:53UTC, well before the03:45
handoff/04:00 stop-write/04:30:55 cleanup limits. The baseline service was left
ready only for the lead's final read-only observation; no worker remote work
remained. Lead was explicitly told it could delete the sole Droplet and dedicated
firewall/key/tag immediately. **Lead cleanup subsequently completed:** the privately retained
`lead-cleanup-result.json` records Droplet deletion at local00:52:37UTC and
404 absence results for the Droplet, dedicated firewall, provider SSH key and
tag by00:54:01UTC. The worker read that record; no deletion was performed by
this worker. The SSH tunnel exited after deletion. Evidence and the local
private key were preserved; the lead removed the temporary cleanup heartbeat.

## Proposed lead follow-up

Review this docs-only branch against deployed `eab1d337`, the exported manifests,
actual refusal/preserved-marker proof and timing boundary. Reuse existing accepted
application evidence; do not repeat a broad suite. Record bounded acceptance and
RFP decisions, then merge only after review. Retain the verified deletion/absence of Droplet
602245599 and its dedicated firewall/key/tag in the lead's cleanup record. Human
recipient acceptance and remaining clauses stay explicit. No new implementation
stage or automatic VM extension is proposed.
