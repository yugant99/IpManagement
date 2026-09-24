# Skills by agent and work part

Use a skill to produce a concrete useful artifact within the feature budget. This is a map, not a checklist requiring every skill on every change. Repository rules and explicit user instructions override optional setup/questionnaire/test pipelines.

## Who uses what

| Agent / part | Primary skill when useful | Optional skill and trigger | Required output; what to skip |
|---|---|---|---|
| Lead / architecture | `grill-me` → `grilling`, with another agent as counterpart | `review` at a coherent integration | Recorded questions/answers and decisions. No user interview; no repeated architecture exercise after choices are settled |
| Part 1 inventory/API | `review` for a shared schema/API change | `investigate` for a concrete blocker | Scope/time identity and API compatibility findings. Routine coding needs no separate skill ceremony |
| Part 2 source/data | `spreadsheets:Spreadsheets` only when an actual workbook/CSV analysis benefits from it | `review` for normalization/provenance logic; `investigate` for a failed import | Positional/source mapping, visible reject counts and reproducible fixtures. No workbook formatting or artifact pipeline for ordinary JSON fixtures |
| Part 3 rules | `review` once a coherent rule group works | `investigate` for a mismatched expected scenario | Critical false-positive/missing-evidence findings and smallest fixes. No test-count target or repeated review of unchanged rules |
| Part 4 UI/capacity | `design-taste-frontend` for the shared dashboard shell and states | `browse` for an authorized changed browser flow; `review` for calculations | Readable tables, clear evidence/unknown states, consistent detail/overview. No decorative animation, landing-page effects or forced dependencies |
| Part 5 workflow | `review` for the transaction and role boundaries | `investigate` for a broken transition | Confirm exact candidate/version handling, atomic allocation/audit and visible failure. No enterprise security program or generic workflow engine |
| **Part 6 Spencer** | `review` as a bounded packaging/contract review; no special deploy skill is required | `browse` only for focused packaged-UI runtime evidence; `investigate` for a startup/persistence failure | Correct entrypoint, locks, volume, state commands and recipient instructions. No VM/deploy skill, source-rule rewrite or app-wide regression pipeline |
| Independent integration reviewer | `review` | `browse` only when a claim needs visible evidence | A short list of actionable defects/limits, mapped to goals and files. Owning lane fixes; do not create competing edits |
| Stage 4 scheduler / evolving-feed owners | `review` for clock, authority, atomic cycle and replay boundaries | `investigate` only for a concrete blocker; `browse` only for a focused runtime check relevant to assigned work | Follow SCHEDULING_CONTRACT.md; source findings and pending evidence. No cron/deploy skill, setup ceremony or repeated architecture interview |
| Source-document analyst, only if needed again | Presentation/document/spreadsheet skill matching the actual file type | None by default | Extract only missing facts with exact locators. Do not reopen the entire assessment during each feature |

## Timeboxes and invocation boundaries

| Skill | Normal budget | Stop condition |
|---|---|---|
| `grilling` | Short agent-to-agent frontier rounds, normally 10–15 minutes | Material decisions are explicit; the completed one-time [75-question pass](GRILL_75.md) is recorded separately. Do not impose 75 questions on every feature |
| `design-taste-frontend` | One 30-minute shared design pass | Reusable layout and states are clear; implement within the feature budget |
| `review` | 15–20 minutes per coherent integration | Actionable findings or explicit limits recorded; no repeated unchanged diff reviews |
| `investigate` | 20–30 minutes | Root cause/narrow fix or evidence-backed blocker; after three failed hypotheses, escalate to the lead |
| `browse` | 10–15 minutes on the affected flow | Steps and observed result captured; do not turn browser setup into a separate project |
| Artifact reading skills | Only the missing source fact/output | Exact evidence captured; no unrelated artifact generation |

Expired time does not mean success. Report the blocker, narrow the task or explain a justified extension. Skill work is included in the feature estimate.

## Installed names and portable lookup

Resolve skills from the current agent's installed catalog. On the lead's environment, `grill-me` forwards to `grilling`; frontend taste uses the `taste-skill` directory; review/investigate/browse use `gstack-review`, `gstack-investigate`, and `gstack-browse`. Artifact skills are supplied by their document/spreadsheet/presentation plugins. Do not hardcode the lead's home directory or plugin version into project tooling.

Spencer's environment may differ. Optional skills are not a setup prerequisite: use the bounded method/output described here if unavailable. If a specifically requested indispensable skill is missing, report that exact blocker rather than quietly substituting it.

## Explicit overrides

- Grilling happens between agents. The user's correction overrides the upstream user-interview/confirmation defaults. Keep actual question/answer evidence; do not fabricate a debate.
- Skip optional onboarding, upgrades, telemetry, analytics sync, persistent-learning writes, routing-file injection and skill shopping. None is part of the product deliverable.
- No skill may change the chosen stack, introduce a service, widen file ownership, send external messages or bypass feature-branch/merge rules.
- Preserve useful root-cause analysis and review, but do not execute automatic test creation or repeated full-suite runs from generic skills. Follow the project lean-verification rules.
- UI skill defaults do not justify Next.js, an animation library, downloaded fonts or another component system. Use restrained operational UI and the selected dependencies.
- Never describe a bounded method pass as completion of an entire upstream workflow with skipped steps.

## Verified upstream sources

- [Grilling](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md).
- [gstack](https://github.com/garrytan/gstack): review, debugging and browser methods; installed versions contain setup/telemetry and broader test instructions that this project's explicit rules constrain.
- [Taste skill](https://github.com/Leonxlnx/taste-skill), including [the older v1 variant](https://github.com/Leonxlnx/taste-skill/blob/main/skills/taste-skill-v1/SKILL.md). The inspected local version differs from current upstream; do not silently upgrade mid-build.

No additional skill installation is needed now. Review a new skill only for a named blocker, with a brief source/license/content check and a clear time saving.
