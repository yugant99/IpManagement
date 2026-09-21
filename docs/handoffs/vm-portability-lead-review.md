# Portable demonstration acceptance

Main Lead 3.0 accepts the bounded Linux amd64 deployment, persistence, recovery and transfer checkpoint on 2026-09-21 UTC. The application, all nine easy wins and Atlas remain accepted. The declared portable target now has actual runtime evidence; `PART6_READY=yes` within this scope. The demo is ready for a recipient walkthrough. Human acknowledgement/training, complete dependency notices and customer/production outcomes remain separate gaps. No Part 7, new feature cycle or repeated broad E2E run is assigned.

## Exact candidate and review

The deployed source was **`eab1d3376633bf3280ff7bd8834fe46c88353d9a`**. The deployment owner performed one baseline image build and zero rebuilds; no application, dependency or packaging repair was required. The [worker handoff](vm-portability.md) records exact source/image/snapshot hashes, runtime versions, commands, logical identities and limitations. Publication changes affect only that handoff and [the operator runbook](../RUNNING.md). Reviewed [PR #63](https://github.com/yugant99/IpManagement/pull/63), head `d8933cca28b3f1f334c1495a6652763e006ca0c9`, merged normally at `dd228a8f038eed6d7ec142307d2cfd18396819d1`; contributor history and branch were retained.

The lead reviewed the actual exported commands/results, recovery protocol, refusal stderr/exit, preserved-target marker and audit, logical-ID comparisons and native transfer. Independent tunneled browser observations showed the compiled Atlas inventory with 60 prefixes, and an independent health read showed all readiness flags true. After recovery/transfer, the final original-volume preview again rendered 60 prefixes. The lead independently rehashed all **39 remote-evidence files and five recipient-transfer files** successfully before destroying the host.

The runbook review corrected stale Compose-version wording, made global named-volume isolation explicit, and removed the conflicting suggestion that an ignored Compose override file would change wrapper mounts. These are documentation corrections, not new runtime behavior. No broad application checks were repeated for publication.

## Accepted observations and limits

- Ubuntu 24.04 amd64, Docker Engine 29.8.1 and Compose plugin 5.5.1 built the exact source and served compiled UI/API. Runtime uid 10001 could write the isolated data volume; the root filesystem was read-only and the app port stayed on loopback. Rich seed, manual acquisition and representative UI/API paths were observed with scheduling disabled.
- Real request, independent approval, refusal audit and allocation identities survived restart and populated restore. Simulated downstream failure remained visible and separate from the successful local allocation. Saved-run summary, customized IPv6 CSV, filters, source catalog, import reconciliation/replay and representative exception/correction/schedule paths were exercised.
- Stopped backup/export succeeded. The real restore wrapper without confirmation returned **exit 2** and left the populated target hash unchanged. Confirmed restore preserved the target's exact distinct metadata marker and audit in its prior-state database, while restoring the original allocation/audit/run identities.
- A protocol written before execution set a **120-second** prepared-host objective. Confirmed restore to all-flags HTTP 200 readiness took **4.427 seconds**; restore alone took 1.726 seconds. Later logical-ID comparison took 1.557 seconds separately. Provisioning, image preparation, snapshot transfer/import and business validation were excluded: this is not a complete outage-recovery SLA.
- The exported image/source/snapshot reproduced the same state and restart identities in a third volume on the same engine. A fresh disposable macOS arm64/Python 3.12 snapshot also restored on Linux amd64 with the same audited marker. These establish agent procedural reproduction and this cross-environment data transfer, not a human recipient session, a second independent container engine, ARM image execution or sustained hybrid operation.

Core native reset/diagnostic evidence remains accepted in its earlier scope. This VM run did not add reset, bad-mount, hot-backup, enabled-schedule recovery, crash/failover/endurance, live integration, production identity/TLS or scale coverage. Historical Stage 5 remains 14 passes/two partial cases, with its separate addenda. Initial removed-container logs were not separately retained; raw HTTP/command evidence and the final app log were retained.

## Questionnaire decision

The lead privately reread the original clauses, not just generic topic labels:

| Row | Current class | Basis and remaining limit |
|---|---|---|
| RFP-090 | Demonstrated, previously Partial | Actual declared-target IPAM package startup, workflow persistence, recovery and operator reproduction; bounded synthetic deployment, not production rollout or customer acceptance |
| RFP-020 | Partial, previously Missing | Measured prepared-host recovery; full outage-to-business recovery including excluded prerequisites remains unproved |
| RFP-023 | Partial, previously Missing | Actual Mac-to-cloud-Linux snapshot/identity transfer; sustained hybrid operation and integration remain unproved |
| RFP-091/092/104/106 | Unchanged | Fixed workflow is not a broader orchestration platform; human training/KT and complete transitive/container notices were not supplied by this experiment |

Current accounting is **39 Demonstrated / 18 Partial / 10 Documentary / 44 Missing = 111**. The earlier 38/17/10/46 and 32/22/10/47 snapshots remain historical. No fully-satisfied percentage follows. Separate customer Phase 1/2 outcomes are unchanged.

## Evidence retention and cleanup

Private artifacts remain under `/Users/yuganthareshsoni/Downloads/Ip_inventory-vm-evidence/20260921T0030Z`: `remote-evidence/`, `recipient-transfer/`, HTTP/UI evidence, `lead-export-verification.json` and `lead-cleanup-result.json`. They include source/image archives, all four stopped-volume archives, baseline/prior-target/native snapshots and screenshots. No private database, credentials, customer source document or infrastructure connection detail was committed.

After the worker confirmed all remote work/export complete and the lead verified hashes, the sole Droplet was destroyed at **00:52:37 UTC on the local/lead clock**. Dedicated firewall, provider SSH-key record and tag were deleted; all four resource absence checks returned 404 by **00:54:01 UTC**. The local private key and native Atlas service on port 8000 were preserved. The obsolete VM tunnel/tab closed. The temporary cleanup heartbeat was removed; original project oversight remains PAUSED with its existing expiry.

The local preflight-to-cleanup interval was about 23 minutes; the lead-owned interval was recorded with monotonic time. Provider/VM wall clocks differed from the local clock by roughly three hours. Cached external HTTP headers did not resolve the cause. Raw timestamps are retained, clocks were not changed, and measured recovery uses monotonic time. The quoted compute rate was USD 0.03571/hour; the actual provider charge/credit balance was not verified. No ongoing experiment host remains.

Next: use the retained native Atlas demo and operator/evidence bundle for human presenter practice and recipient acknowledgement. Those are the remaining handoff outcomes; completed implementation does not need another automatic application cycle.
