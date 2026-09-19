# Stage 5 local execution authorization

On 2026-09-19, the user told persistent lead task `01a0b845-6c8d-7021-a5c9-15e673db07c9`: **“lets go man tun the tests man”**. This answers the lead's pending request to run the prepared local Stage 5 acceptance checks. It supersedes the earlier no-execution instruction for this bounded run; no further per-scenario permission question is needed.

Continue existing task **Execute Stage 5 acceptance handoff**, `01a0baff-2143-7073-ad3d-4963a9cc0ca5`, in `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5`, branch `codex/stage-5-local-acceptance`, PR #27. Accepted preparation is `7e37dde6ba18a08717b0ce56c4438522fc5f7008`; application pickup is `117d05295473cf25d362adb320e6fef26ecdd74c`, accepted code `54f8f8168108733d40d842263218f16b33df5868`.

## Granted local scope

Execute the prepared 16 scenarios in six groups, using the smallest useful checks:

- Inspect local runtime availability, install pinned dependencies if needed into isolated environments, and build the compiled UI once. Preserve dependency locks and source fixtures.
- Create fresh disposable stores and acceptance artifacts; seed the rich inventory; start one-worker localhost services; exercise browser/API acquisition, replay, calculation, inventory, allocation, audit, and team handoff paths.
- Collect supporting evidence, including input hashes, database reads, independent calculations, requests/results, screenshots and semantic before/after comparisons. Derive clearly labeled synthetic negative-control inputs only in separate disposable stores/copies.
- Use a bounded disposable harness for controlled timer/concurrency/overdue-startup, one transaction fault, and response-loss/retry observations. Record the actual mechanism; do not alter host time or add production hooks.
- Stop owned services for backup/restore, restart disposable copies, and create recognized legacy copies for explicit migration checks. Preserve the disabled-timer snapshot procedure. These operations apply only to new acceptance data.

The proposed artifact root is `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-artifacts/`; choose a fresh run directory and record the actual paths. Isolated ignored frontend dependencies/build output may live in the Stage 5 checkout. Original fixtures are read-only inputs. Retain evidence and snapshots; stop only acceptance-owned processes at completion. No broad cleanup.

## Boundaries and reporting

No cloud, VM, Docker/container execution, deployment, public exposure, spending, external messages, existing user database mutation or unrelated process changes. Spencer retains Part 6 packaging. Reset and deeper exhaustive failure/scale matrices remain outside this prepared run. PR #9 remains NO MERGE.

Route application defects to the existing Stage 3, Stage 4, core or data owner with exact candidate/input/error evidence. The same local permission covers a necessary focused reproducer and affected rerun on fresh disposable data; it does not authorize a growing full suite. Lead review precedes integration of application corrections. Preserve feature ownership and branch history.

Record each scenario as observed pass, observed fail, partial or not run. Permission is not evidence. The 111-row denominator and clause limits remain unchanged, and no runtime or portable acceptance is granted by this document. Application main merges remain a separate lead decision after actual evidence review.
