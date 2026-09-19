# Development rules

These rules apply to every human and agent working on this repository. The goal is a credible, portable synthetic-data demonstration within a short build window. Optimize for finished user-visible behavior, small understandable code and clear handoffs.

## 1. Scope and authority

- Read `AGENTS.md` and `docs/STATUS.md` first. State the assigned goal IDs and owned files before implementation.
- Distinguish accepted decisions, proposals, implementation and demonstrated results. Never treat a written plan or a green-looking screen as completed behavior.
- Resolve routine coding details using existing conventions. The user has delegated architecture grilling to agents: interviewer and proposer must challenge each other directly, settle bounded choices, and record assumptions. Do not interview the user by default.
- Escalate only a genuine blocker that agents cannot resolve within the user's constraints, or an action outside existing authorization such as new infrastructure spending. Do not send routine tradeoffs back to the user.
- Batch material questions, at most three per round. Do not re-ask answered questions or request facts available in the repository.
- Implement only authorized work. No cloud rental, public exposure, external writes or new ongoing cost follows automatically from a feature request.
- Keep the 111-row external requirement view separate from the smaller demo-goal scorecard. Do not relabel partial or simulated behavior as full requirement satisfaction.

## 2. Three changes, then push

- A **coherent change** is a meaningful finished slice with one purpose: a behavior, correction, contract, or documentation outcome. It is not each edited line or file.
- Make one descriptive commit per coherent change. After the third commit, push the working branch before starting the next slice. Three changes normally means three commits and one push.
- Push earlier before handing work to another agent, pausing, or ending a session. Do not wait to accumulate three if work is about to stop.
- Never create empty commits, split inseparable edits, or add cosmetic churn to inflate counts. More real checkpoints improve recovery; raw commit count is not the delivery metric.
- **Different features use different branches, then merge.** Use `codex/part-N-feature-name`, for example `codex/part-3-ghost-scope` or `codex/part-6-container-startup`. A part is an ownership area, not permission to put unrelated features on one long-lived branch.
- Start each feature from the current integration baseline on `main`. If it depends on an unmerged feature, coordinate the dependency with the lead instead of copying code between branches. Concurrent agents use separate worktrees/checkouts; never switch the branch beneath another active agent.
- The initial documentation bootstrap may establish the default branch directly. After bootstrap, no feature implementation goes directly onto `main`.
- Stage explicit owned paths. Inspect the staged content before pushing. Never include source attachments, credentials, local databases or another agent's unrelated edits.
- WIP checkpoints may be pushed with their limitations clearly stated. A push is not a claim that checks passed or a release is ready.
- Do not force-push shared history, reset another contributor's work, or merge your own lane into the integration branch without the lead's coordination. Preserve coherent commits when integrating rather than automatically squashing them away.
- Open a PR for a ready feature. State goal IDs, behavior, focused validation actually performed, simulations/unverified limits and any contract changes. The lead arranges a bounded independent review, resolves relevant conflicts and merges; do not trigger a full test suite just because a PR exists.
- Use a merge that preserves the feature's coherent commits by default. Do not squash or rewrite a contributor's history solely to tidy the graph. After merge, use a new branch for the next feature.
- A branch may be checkpointed before release readiness. Only merge feature behavior whose required correctness/integration evidence is recorded, or clearly identified documentation-only changes. Do not use commit count as a merge criterion.
- If a push fails, record the error and the local branch/commit. Fix the actual cause; never report it as pushed.

## 3. Small code and one owner per boundary

- Read nearby code and call sites before editing. Reuse existing helpers and patterns.
- Choose the smallest implementation that delivers the acceptance behavior. Prefer direct functions, explicit SQL and a small state machine over new frameworks.
- No generic plugin system, event-sourcing framework, microservice split, agent runtime, second database, or configurable workflow builder unless the agreed goal genuinely requires it.
- The logical data model explains information that must survive; it does not mandate a table, abstraction or service for every noun.
- Do not refactor, rename, reformat or upgrade adjacent code while completing a feature.
- Do not create separate copies of business rules for the API, UI and reports. UI and export totals come from the same saved calculation results.
- Lead owns shared contracts, schema migrations, app startup and integration decisions. Each lane owns declared files. Propose a contract change to the lead before implementing incompatible assumptions.
- Fail visibly: rejected records, stale inputs, partial operations and failed downstream simulations must be shown and recorded.

## 4. Lean verification

- Respect the user's instruction not to add or run application tests without explicit authorization. Documentation-only work does not need an application test run.
- Once checks are authorized, choose the smallest checks that can falsify the claimed behavior. Use an existing focused test first. Do not run the full suite after every feature, commit or push.
- Add regression coverage only when it protects meaningful logic or a real failure: address/time identity, lease transitions, missing-source handling, allocation atomicity, authorization or persistence. Do not test trivial wrappers or mirror implementation line by line.
- Prefer a small scenario matrix with healthy, anomalous and insufficient-evidence cases over hundreds of cosmetic assertions.
- Initial target: zero to three focused checks per small slice; a short build/type check when relevant; one agreed integrated demo pass at a milestone. These are defaults, not permission to skip a necessary safety or correctness check.
- Timebox routine verification. If a planned check becomes slow or repeats unchanged work, report why and narrow it. Do not keep running a growing suite for reassurance.
- Never rerun a passing check without a new relevant edit, failure or unresolved concern. Never call an interrupted or unrun check passed.
- If a material issue remains unverified, say so. A timebox does not convert uncertainty into success. Fix a critical issue or reduce the claim/scope.

## 5. Skills without overhead

- Pick a skill because it improves the current output. Use at most one primary skill per slice unless a second has a distinct required purpose.
- Read the relevant instructions before applying the skill. User instructions and this task's authorized scope take precedence over optional skill defaults.
- Default skill-selection budget: five minutes. New skill research/installation is off the critical path unless it solves a named blocker with a clear net saving.
- Do not import a skill's automatic telemetry, setup wizard, full review pipeline, broad security interview, infrastructure changes, or full-suite test loop into the project by default.
- Use the useful artifact: a small decision tree, UI review findings, root-cause explanation or targeted review. Stop when that artifact is complete.
- Ask security questions only for concrete scope: public deployment, permissions, secrets, or a real state-changing action. Do not design enterprise SSO, HA, compliance or threat programs for this local synthetic demonstration.
- Do not remove essential correctness controls in the name of speed. Unknown evidence stays unknown; the API enforces claimed permissions; allocations cannot silently collide.
- The user explicitly overrides the grilling skill's user-interview and user-confirmation defaults for this project. Run short agent-to-agent frontier rounds; record the actual exchange and resulting decisions, never a fabricated debate. The current deeper 75-question architecture pass is a one-time planning exercise responding to the requested depth, not a mandatory feature ritual. Later rounds reopen only material unresolved choices.
- Other skill confirmation requirements must be checked against existing user authorization. Do not create additional approval gates by interpretation.

## 6. Evidence and synthetic data

- Mark synthetic inputs, replay, calculations and simulated external actions accurately. Local database changes can be real while provisioning outside the app is simulated.
- Match addresses using explicit network scope and time. Legitimate private-address reuse across isolated namespaces is not a conflict by itself.
- Preserve enough source references, observation time and freshness/completeness to explain every finding. No telemetry does not prove no usage.
- Detection logic must not read fixture expected-answer labels to choose its output.
- Inactivity creates a review candidate under the agreed rule, not an automatic safe-to-reclaim claim. Approval does not mean external execution succeeded.
- All values shown in a detail view must reconcile with the dashboard/report using the same run and definitions.
- Public repository content must remain generic and synthetic. Keep source attachments, private assessment extracts and credentials out of commits.

## 7. Documentation and handoffs

- Each part has one short task page: outcome, owner, inputs, owned files, output contract, dependencies, acceptance and exclusions. Update it only when those facts change.
- A receiving agent must be able to start from the repository without access to the prior chat. Record exact branch/commit, read order, current behavior, next action and blockers.
- Do not claim a placeholder endpoint or planned command exists. Mark proposed interfaces explicitly until implemented and recorded.
- Update `docs/STATUS.md` at integration checkpoints, not for every edited line. Each lane keeps its own handoff notes to avoid collisions.
- When blocked for about 15 minutes, report the exact missing contract/error to the lead and continue independent work. Do not invent a second architecture or send the user a stream of implementation questions.
- Progress format: **works now; simulated; unverified; blocker; next visible result**.

## 8. Finish the slice

For every completed slice, report goal IDs, changed behavior, commit/branch, pushed status, validation actually performed, known limitations and next owner. Freeze features early enough to preserve integration and recipient handoff time. Prefer fewer complete paths to many disconnected screens.
