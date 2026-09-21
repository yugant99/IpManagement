# Approved Atlas UI follow-up

**Bounded repair authorization, 2026-09-21 UTC:** the user requested only three follow-up changes through the easy-wins task: make Capacity filters visibly affect matching report results with accurate pool-calculation scope; make the saved run's total evaluations prominent and distinguish filtered results; and mark opened exceptions, scroll their detail into view and focus the detail heading. Main Lead 3.0 assigned the existing visible Atlas task `01a0c13d-a8ff-7900-8bdc-400aa29ee5d3`, GPT-5.6 Luna / medium, a new isolated branch from `392e9b594169b49d49b57e1edc9eecbe4598d405`. Preserve the native port-8000 service and demo data; necessary checks are narrowly local and read-only against that store. No VM retest, Docker work, reprovisioning, broader E2E cycle, new feature or coverage upgrade is authorized. The completed VM experiment remains tied to its exact earlier source and is already torn down. Lead review and merge remain required. Earlier Atlas authorization below describes its original scope.

On 2026-09-20 the user selected Atlas from the completed design study and explicitly authorized implementation through a visible GPT-5.6 Luna worker, focused tests, a frontend build, local browser checks, lead integration and a user try flow. The authorization was relayed by the **easy wins** task, `01a0c0e1-aaa0-7152-bfa9-a93c0baa3b43`, and its original user message was read by Main Lead 3.0. This supersedes earlier instructions deferring UI polish within this narrow scope; it does not create another engineering stage.

## Ownership and baseline

- Lead: Main Lead 3.0, `01a0c0c1-3952-7720-93c8-ff49192b8e13`; global status, review, acceptance and merge.
- Worker: **Atlas UI — implementation and local validation**, `01a0c13d-a8ff-7900-8bdc-400aa29ee5d3`, GPT-5.6 Luna / medium, isolated `codex/atlas-ui` worktree.
- Accepted baseline: main `cd915fcfa79dbb5bd394c64c0edf1015fd406e1b`. All nine agreed easy wins are accepted; see [their lead review](easy-wins-lead-review.md).
- Worker owns `frontend/src/**`, its Atlas handoff/evidence and a narrowly justified UI regression harness if needed. Backend, schemas, fixtures, dependency locks and global accounting remain outside that lane.

## Visual and behavior contract

Use `design-experiment/ipam-design-study.html#atlas` and `design-experiment/DESIGN_BRIEF.md` at design-study commit `2094cda41f99c5bbd7da910be29855ff47736864`. Atlas is the `direction-a` section using the base light paper/white navigation, ink/green accents and operational record layout. The navy rail of Console is a separate unselected direction. The design-study branch is a visual reference, not a dependency to merge wholesale.

Retain the React/TypeScript/Vite/plain CSS stack and real API values. Group existing navigation into a persistent rail; make scope and evidence context clear; retain readable inventory/detail layouts and literal evidence states. Saved-run identity and eligibility remain separate from current exceptions and approvals. Translate mockup controls only where an existing real function supports them. Do not copy invented metrics, imply a live authenticated session or add placeholder actions.

Preserve all existing filters, exports, import/reconciliation semantics, retries, roles and actions. Styling does not earn questionnaire credit: accounting remains **38 Demonstrated / 17 Partial / 10 Documentary / 46 Missing = 111**.

## Authorized acceptance

Use a Node version within the declared supported range. Run the frontend type/build check and meaningful focused checks for changed interaction behavior. Inspect the affected real views on fresh disposable synthetic local data: inventory filtering/detail, source catalog and opt-in import reconciliation, saved-run reports/export, requests/exceptions, corrections and schedule. Review desktop and narrow layouts plus keyboard/focus access. Reuse earlier accepted backend evidence; do not repeat broad historical E2E cycles.

Inspect runtime ownership before starting or stopping a service. Preserve original acceptance/demo stores and private artifacts. Record exact candidate, commands, results, limits and any retained preview ownership. Lead review must close relevant findings before merge. The user handoff must give a safe local start command or owned preview URL and a short click-through using actual UI labels.

Docker execution, image pulls, VM/cloud provisioning, deployment and spending remain outside this request. Portable startup/persistence and recipient proof remain unverified, `PART6_READY=no`. The existing oversight monitor stays PAUSED with its original expiry.
