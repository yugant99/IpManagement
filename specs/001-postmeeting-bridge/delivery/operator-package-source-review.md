# T024 operator/package source review

Author: Muse Spark 1.3 Contributor high in OpenCode, exact
`opencode-go/muse-spark-1.3-contributor#high`, retained session
`ses_f30868e2affe2hAM4rI4a7dKuR`. Astra/Main Lead 6.0 task
`01a0cf70-c4e0-7ed2-b50b-834609e6d909` coordinates; independent reviewer
is GPT-6 Sol high, worker `/root/sol_t024_review`.

Base: `4ee3a583d3ee36bef4197f6babae52c8eea48d3a`.
First full candidate: `8b6b78fe7dd7dfaa93516208cd6b0391961749be`.
Final author source: **`7e50122ac6c7bc837bd89db6b9029035065b1b57`**.
Reviewed lead recovery-runbook delta: `8f97b8b4bf8bbf6dc0e8302ff33576ca6f963b22`.
Reviewed lead quickstart delta: `eb65c8fa39b11bb622c1dcc498715fb661fbc48e`.
PR100 merged the runbook into the author branch at `2926e69fca7b8d0e2299e8445210415855d70ea5`.
PR99 integrated complete source into the lead bridge at
**`68e0b4ed466c66ce73926ddfec8a79ad94d7d1c8`**. These are bridge-only merges.

## Source findings and closure

Sol reviewed the full nine-path feature and shared core/API/configuration/recovery
contracts. Astra supplied additional source findings. Spark retained and corrected
the implementation; Sol independently closed all P1/P2 findings at final author SHA:

- Replace prefix-based URL admission with parsed exact numeric loopback authority;
  reject userinfo, controls, injectable syntax and unexpected path/query/fragment.
- Keep token contents out of shell variables/argv/logs and disable inherited tracing.
  Open protected files without following symlinks or blocking on FIFOs; descriptor
  checks enforce regular file, current-user ownership, owner-only mode and bounded
  exact token representation. Correct heredoc control flow without execution.
- Reject domain header/config injection before requests, validate pins, and normalize
  the permitted API root slash.
- Accept acquisition only with coherent 201/false/false or 200/true/true status,
  unique exact replay header and boolean body evidence. Inconsistent or transport
  outcomes remain unknown; preserve original key/reason and never auto-retry.
- Remove generic reseed advice. Distinguish Docker liveness from all-six-field
  protected readiness and separate business-state comparison.
- Distinguish absent, invalid/mismatched, and valid-but-unavailable recovery manifests.
  Require explicit data volume and separately provisioned read-only configuration.

The original nine-path lease was preserved; start/backup changes are text only.
The lead separately owned primary RUNNING recovery/transfer sections outside Spark's
narrow auth/readiness/config lease, plus the stale quickstart command correction.
Sol source-reviewed both deltas independently. Historical STATE_OPERATIONS.md schema5
wording and restore.sh literal-volume comment remain identified documentary drift
outside this slice; current operator-handoff/RUNNING/recovery wire govern T025.

## Evidence boundary and next gate

No tests, builds, syntax checks, imports, SQL/database operations, servers or runtime
checks ran before source closure. T018/T019/T020/T021/T022/T023 prerequisite receipts
and ancestry were independently refreshed by Sol; T024 now completes source prerequisites.
Source acceptance does not prove any operator/runtime/recovery behavior.

Luna's separate T025 worktree freezes exact assembly `68e0b4ed466c66ce73926ddfec8a79ad94d7d1c8`.
Existing T025 authorization permits only the complete required disposable synthetic
local evidence scope after this gate; retain every criterion and blocker. No actual
recipient Linux target or human acknowledgement exists. Main stays unchanged;
T028 still requires passing exact-candidate evidence, final Sol T027 and recorded
T026/business dispositions. No questionnaire promotion, deployment or Tier B release.

## T024 correction from independent T025 observations

Independent Luna observed wrapper bootstrap JSON parsing fail despite HTTP200: curl config single-dash `-silent`/`-show-error` were short-option clusters, inadvertently including response headers in the body. Original Spark author corrected all three config writers in acquire/health at **`f8d381adb3a604251b5486ecfa10148bb1491f81`**. Visible independent GPT-6 Sol task `01a0cf9a-ce88-7f90-8556-1fa4b131bf26` confirmed the exact three-line delta and preserved token custody, curl CLI flags, proxy/redirect restrictions, response separation, replay and readiness invariants. No author/reviewer runtime check ran.

PR102 integrated at **`0c20a7ba82c9802d20223d164efdc830e9ab1eac`**. Visible separate Luna task `01a0cf9b-6bef-7fd3-b0f5-9cd303053c8f` owns affected runtime rerun and complete T025 evidence on that frozen candidate. Source correction is not a passing runtime gate. Earlier failed candidate records remain retained; main, portable/human, questionnaire and TierB boundaries are unchanged.
