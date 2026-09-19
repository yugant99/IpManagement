# Stage 1 pickup: build the foundation

This is the generated pickup for the planning-to-build boundary. Planning is complete. The original **Build synthetic inventory demo** chat remains persistent project lead; this stage runs in a separate implementation chat. The user has now started **Build Stage 1 IPAM foundation**; do not create a duplicate worker from this prompt. Consult current status before pickup.

## Recorded state

| Field | Actual state at handoff preparation |
|---|---|
| Repository | `https://github.com/yugant99/IpManagement` |
| Local checkout | `/Users/yuganthareshsoni/Downloads/Ip_inventory` |
| Planning/source baseline | `main` at `ff8b3a3e59081277cd3e56af9d657c4e4c25448b`, already pushed; PR #2 merged |
| Handoff publication | This is a later documentation-only change; inspect the current published `main` and use it if it contains the recorded baseline. Do not reset to the older baseline just to match this table |
| Contract | `demo-v2-questionnaire` |
| Completed | Questionnaire-first priorities, 111-row gap map, architecture decisions, six part briefs, Spencer pickup, development/skill/chat-stage rules |
| Application / runtime | No app module, frontend, locks, schema or working runtime command yet |
| Runtime evidence | None; no application tests, smoke checks, container build or deployment run |
| Git before this handoff change | Clean `main`; no application work or unmerged application dependencies; one local checkout |
| Private material | Ignored local `assessment/` and source attachments remain outside the public repo; do not stage or delete them |
| Part 6 | Spencer, 6–8 hours, no presentation work; `PART6_READY=no` |

This state must be refreshed from Git/status at pickup. A subsequent code change supersedes this snapshot; it is not authority to overwrite later work. The outgoing chat reports the final documentation publishing SHA after push/merge, avoiding a self-referential commit hash in this file.

## Outcome and ownership

Establish an installable backend under `backend/ipam_demo`, React/TypeScript/Vite frontend under `frontend/`, pinned dependency/build metadata, a minimal scoped inventory schema and deterministic seed. Wire the browser's inventory view to the actual local API, with explicit setup-needed/error states. Preserve the runtime/data/static/health contract and document actual implemented entrypoints.

Start with `codex/part-1-foundation` in an isolated worktree from the current integration baseline. Use further feature branches for distinct work; a stage is not permission to combine unrelated features. The persistent lead retains shared contract and integration authority; the Stage 1 worker implements the assigned schema, startup and locks. A UI agent may own assigned `frontend/` files in another worktree after payloads are fixed. Stage 1 owns its minimal packaged seed; the separately assigned Part 2 data lane owns the richer source/scenario pack. Coordinate their seed shape and IDs. Do not switch another agent's checkout or have two lanes regenerate shared locks.

Foundation work contributes to 002/007/010/012/013/026/028/029/030/031 but does not automatically complete these rows. Preserve the full questionnaire denominator and actual evidence states.

## First work sequence

1. Read applicable `AGENTS.md` instructions, actual Git/worktree state, this handoff, `STATUS.md`, `CONTRACTS.md`, `QUESTIONNAIRE_SCOPE_DELTA.md` and Part 1. Consult the stage/priority and skill maps only as needed; do not rerun the 75-question interview.
2. Report Stage 1 activation and owned files to the persistent lead, and establish the actual backend/frontend installation and lockfile conventions in the stage report. The lead updates global status. Keep FastAPI/Uvicorn, React/Vite, SQLite and standard IP address arithmetic; no stack shopping.
3. Establish scoped prefixes/pools and their identity/version/metadata fields, a small deterministic IPv4/IPv6 seed and the common API/error/data-path shapes. Design later lease/source/run records only to the extent the next stage needs their contract; do not implement every rule now.
4. Connect the inventory browser view to stored API data. Startup/readiness must distinguish unseeded data from failure. No hardcoded dashboard totals or fixture expected-answer labels masquerading as rule output.
5. Document actual setup and runtime entrypoints and every missing state command. Core owns eventual seed/reset/backup/restore correctness; `PART6_READY` stays false until all its real prerequisites exist. Spencer may prepare package files/docs in parallel without inventing missing app commands.
6. Checkpoint each coherent change and push after three, earlier at handoff. Arrange focused code review and record only checks actually run under current authorization. Do not claim runtime success from code inspection.

## Exit boundary

Stage 1 ends at a pushed foundation checkpoint with actual interfaces/files and explicit implemented-versus-unverified state. Do not quietly expand into the complete rule engine. If validation is not authorized or evidence is missing, the handoff says **code ready; runtime evidence pending** and lists the remaining gate. Merge readiness is separate; name any unmerged prerequisite with exact branch/SHA for the persistent lead and next worker.

Write the Stage 1 completion report and draft `docs/handoffs/stage-02-first-path.md` from actual state. Display **READY FOR PROJECT-LEAD REVIEW — Stage 1** with SHA/PR, evidence, gaps and the draft prompt. The persistent lead reviews and coordinates merge/acceptance, then updates `CURRENT_HANDOFF.md` and `STATUS.md` and displays **START A NEW IMPLEMENTATION CHAT — Stage 2: first complete path**. That prompt targets import → stored observations → one computed finding → evidence detail; do not invent the future checkpoint now.

## Scope and permissions to carry forward

The latest user accepted starting the build and requested staged fresh-chat handoffs. Implement this assigned local foundation without reopening planning. The existing instruction still requires explicit request before adding/running application tests, smoke tests or verification commands; record what remains unverified. No container/VM operation, cloud rental, public deployment, customer-system integration, external communication or commercial promise follows from this handoff. Read current user instructions first if they change these limits.

No production identity, HA, carrier-scale claim, second database, event bus, live connector fleet or generic workflow framework. Synthetic inputs and simulated external actions stay labeled. Keep the existing pressure/oversized source thresholds for later stages. Preserve Spencer's Part 6 ownership and the overall hour-14 freeze.

## Paste-ready prompt

```text
Start Stage 1: IPAM foundation in https://github.com/yugant99/IpManagement.
Local checkout: /Users/yuganthareshsoni/Downloads/Ip_inventory.

You are a Stage 1 implementation worker. The existing Build synthetic inventory demo chat remains persistent project lead and owns global status, acceptance and main integration. Check docs/STATUS.md for an existing Stage 1 worker before starting; the task Build Stage 1 IPAM foundation has already been registered, so this prompt must not create competing ownership.

Planning is complete. Implement the foundation now; do not restart the architecture interview. Read applicable AGENTS.md instructions, docs/CURRENT_HANDOFF.md, docs/handoffs/stage-01-foundation.md, docs/STATUS.md and the relevant contracts/Part 1 brief before editing. The recorded pushed planning baseline is ff8b3a3e59081277cd3e56af9d657c4e4c25448b on main, contract demo-v2-questionnaire. Inspect current Git and remote state, preserve later/dirty work, and use the current agreed main baseline containing that commit rather than resetting backward. This prompt may be stale if another stage has already started; follow the current handoff and reconcile ownership first.

Use codex/part-1-foundation in its isolated worker worktree and build the installable FastAPI backend, React/Vite frontend, pinned dependencies, scoped SQLite inventory/schema, small deterministic seed and API-backed inventory view. Implement explicit unseeded/readiness/error states and document actual runtime/data/static paths and missing commands. Coordinate schema/locks centrally; parallelize only independent owned files/worktrees. Part 2 generates the richer synthetic observations/scenarios separately; share your seed shape and IDs without duplicating its files. Spencer owns Part 6 packaging, not app logic, and can prepare alongside us. PART6_READY stays false until its real prerequisites exist.

Use the 111 questionnaire rows as the scorecard; 65/67 planned rows include partial/document evidence and are not completion claims. Follow the bounded skill map, separate feature branches, one coherent change per commit and push after three or before handoff. Avoid speculative abstractions and scope expansion. Preserve current limits: do not add/run application tests, smoke tests or verification commands without an explicit request; no container/VM/cloud/public-deployment action is authorized by this prompt. State unverified behavior plainly.

Stop at the Stage 1 pushed checkpoint. Report READY FOR PROJECT-LEAD REVIEW — Stage 1 with exact pushed branch/SHA/PR, implemented behavior, actual evidence, unverified limits and dependencies. Draft the Stage 2 handoff and paste-ready prompt. Send the report to the persistent project lead; do not independently merge to main, accept the stage or replace global CURRENT_HANDOFF.md/STATUS.md. The lead publishes the accepted next-stage prompt. Keep this worker chat for assigned foundation fixes; do not start Stage 2 here unless I ask.
```
