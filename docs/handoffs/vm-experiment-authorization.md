# Bounded VM experiment authorization

On 2026-09-21 UTC, the user explicitly authorized creating one brief DigitalOcean VM experiment and running deployed E2E checks, while warning against repeated build/test loops. Main Lead 3.0 read the original user message in the **easy wins** task. This grant supersedes earlier no-cloud/no-Docker wording only for this disposable experiment; it does not authorize a standing deployment or new services.

## Owners and baseline

- Lead: Main Lead 3.0, `01a0c0c1-3952-7720-93c8-ff49192b8e13`; acceptance, integration, questionnaire decisions and resource cleanup.
- Sole deployment owner: **VM portability — bounded deployment and E2E**, `01a0c163-9686-7001-81d1-d6abbfad41ec`, visible GPT-6 Astra / medium, isolated `codex/vm-portability` branch. No additional workers are assigned.
- Initial candidate: accepted main `eab1d3376633bf3280ff7bd8834fe46c88353d9a`, including Atlas and all nine easy wins. Deploy this exact source before any repair; distinguish later repair candidates and images.
- Existing provisioned host: one Ubuntu 24.04 amd64 Droplet, 2 vCPU / 4 GB / 80 GB local disk, Toronto. Dedicated resource IDs, strict-host SSH details and raw provisioning records are in the private experiment handoff outside Git. Do not create another host.

## Permitted execution

Install Docker Engine/Compose and required OS tools on this VM, pull/build the image, run the compiled UI/API on loopback, and inspect the real deployed app over a narrow SSH tunnel. SSH ingress stays restricted to the recorded client address; there are no public app ports. Provider credentials stay on the local machine and private-key contents must never enter logs or artifacts.

Use only disposable synthetic data. Record Linux/image/platform/runtime/lock identity, packaged static/fixture/producer assets, uid 10001 data permissions and loopback/read-only-root behavior. Prove the global `ipam_demo_data` volume absent on the dedicated engine before reserving it; changing Compose project names alone does not isolate that volume.

Run one planned bounded UI/API pass: rich seed/acquisition; inventory filters/detail; saved-run summary/custom report export; source catalog; one allocation with independent approval/audit and a refusal; opt-in import reconciliation/replay; and representative access/actions for exceptions, corrections and schedule. Automatic scheduling stays disabled. Reuse prior exhaustive local functional evidence.

Prove persistence by retrieving the same allocation/audit/run identities after restart. Stop before backup and transfer; retain hashes. Restore into a distinct populated disposable target, observing confirmation refusal without replacement, then confirmed restore, the preserved prior-state marker, logical identity equality and readiness. Define a local recovery target and start/end boundaries before measuring with monotonic time; report readiness time separately from data verification, without asserting a customer SLA.

Package hashed source/image/snapshot artifacts for a small procedural recipient reproduction on distinct data on the same authorized host. Agent reproduction does not establish human training, presenter practice or recipient acknowledgement. Any optional native-to-VM snapshot must come from a new disposable native store; retained native Atlas/acceptance stores and the existing localhost:8000 preview remain untouched.

## Stop, cost and cleanup rules

- One baseline build/pass. After a failure, record the symptom and root-cause hypothesis, make the minimal correction, then rerun only affected checks. Rebuild only for changed image inputs or a specific diagnosed reason; reuse valid artifacts/cache.
- Two failures without new evidence, or approximately 20 minutes stuck on a path, require a lead diagnosis rather than another blind retry or infrastructure recreation.
- No local Docker, extra VM, managed database, public app, TLS expansion, live integration, HA/endurance project or speculative refactor.
- The provider's quoted rate is USD 0.03571/hour. Target 2–4 hours, with planned base compute well below USD 1. The user's displayed USD 5 signup credit is a budget, not a verified provider-enforced cap.
- Evidence/checkpoint by 03:45 UTC, stop new work/export by 04:00 UTC, and complete destruction by **2026-09-21 04:30:55 UTC on the local/lead clock** at latest. Clean up earlier on completion or an unrecoverable blocker. The observed roughly three-hour provider/VM clock discrepancy must be retained and investigated, not used to extend the experiment.
- Main Lead 3.0 must export evidence locally, destroy only the authorized Droplet, verify its absence, and remove only its dedicated firewall, provider SSH-key record and tag when no longer needed. Power-off is insufficient. Preserve local private keys and unrelated resources.
- Temporary `ipam-vm-experiment-cleanup-deadline` heartbeat checks the deadline every 15 minutes through that cutoff and is removed after cleanup. It is an additional local safeguard, not a provider billing cap. The pre-existing project oversight monitor remains PAUSED.

Raw evidence, image archives, snapshots, screenshots and infrastructure connection details stay in the private evidence directory identified by the provisioning handoff. Commit only sanitized engineering findings and coherent fixes. Lead reviews any cross-boundary application change and all PR merges.

## Acceptance boundaries

Provisioning itself earns no questionnaire credit. Baseline remains **38 Demonstrated / 17 Partial / 10 Documentary / 46 Missing = 111**. The lead will reread exact clauses for deployment, measured recovery and portability after evidence review. Orchestration, human training/KT, complete license notices, failover, virtual network support, hot backup and encryption are not automatic promotions. `PART6_READY=no` remains in force until the lead adjudicates the actual bounded result. This is not a new engineering stage or an unlimited E2E cycle.
