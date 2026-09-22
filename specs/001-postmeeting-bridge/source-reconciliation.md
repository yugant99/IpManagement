# Source reconciliation and evidence taxonomy

Status: Spec v0, 2026-09-22. Documentary inspection only. No new application observation.
Baseline: `04eba98cb8673406d1e5d38c5318fb963cc77ff7`.
Branch: `codex/postmeeting-specification`. Source workbooks remain unchanged.

## Source map

| ID | Source and exact locator | Authority and limitations |
|---|---|---|
| S1 | User-supplied post-meeting workbook; Technical Requirements B3:H113, J1:L6 | Requirement intent and meeting answer labels. Not execution evidence. Requirement ID n maps to Excel row n+2. E is answer, F is commentary, G has ten additional notes, H has none. |
| S2 | User-supplied accounting workbook; Summary A6:D11, Requirement Detail A5:G115 | Older artifact-specific evidence ledger. Each ID n maps to detail row n+4. Its summary is internally consistent but differs from current accepted accounting. |
| S3 | docs/QUESTIONNAIRE_ROW_MAP.md at baseline | Controlling accepted row classifications, 111 unique rows. Remaining clauses apply even to Demonstrated. Stale closing prose does not override latest acceptance. |
| S4 | docs/STATUS.md, CURRENT_HANDOFF.md, PROJECT_OVERSIGHT.md and handoffs/main-lead-3.0.md at baseline | Current authority and acceptance. Latest dated addenda control older historical passages. No new execution grant follows. |
| S5 | docs/CONTRACTS.md, IMPLEMENTATION_DECISIONS.md, QUESTIONNAIRE_SCOPE_DELTA.md, AUDIT_RESPONSE_CONTRACT.md, EASY_WINS_CONTRACT.md, SCHEDULING_CONTRACT.md | Existing behavior contracts. Later explicit bounded amendments control older deferrals. |
| S6 | docs/handoffs/vm-portability-lead-review.md, easy-wins-lead-review.md, atlas-ui-repairs-lead-review.md | Lead-recorded observations at exact candidates. Read documentary evidence; did not replay it. |
| S7 | Two user-supplied handwritten images, recovered retained attachment representations | Original temporary files missing; exact-basename-labeled embedded attachments recovered read-only and visually inspected by the bounded source-recovery agent. Some wording remains ambiguous. No original bytes or customer details committed. |
| S8 | Source task user narrative and its prior analysis | User narrative supplies migration, domain/region, ServiceNow, utilization, external-platform and DNS intent. Prior assistant interpretations remain secondary; recovered S7 visual evidence now supports the sanitized findings below. |
| S9 | Official GitHub Spec Kit v1.0.9, source commit 3b895d16bd55a0cdaad16d086ffc6b10eef34614 | Real locally initialized toolkit. See toolkit-record.md. |
| S10 | backend/ipam_demo/app.py and workflow.py at baseline | Read-only source: /api/docs and /api/openapi.json exist in app definition; demo actor permissions are fixed. Source inspection is not a new runtime observation. |

Private-source hashes (identity only, no private source content):
- S1 SHA-256: `9ad454822b342f29bd63533ba353cc676a74f073b290de1bf85554f83a06e02e`.
- S2 SHA-256: `3d5ba6d8e6250c27712e419bd5efb751d77831cdb45e165e8e4340daa7a18adc`.

## Reconciliation

| Source | Demonstrated | Partial | Documentary | Missing | Total |
|---|---:|---:|---:|---:|---:|
| S2 actual rows and summary | 36 | 21 | 8 | 46 | 111 |
| S3 current accepted ledger | 39 | 18 | 10 | 44 | 111 |
| S1 answer cells E3:E113 | 92 | 0 | 12 | 7 | 111 |
| S1 static summary J2:L6 | 39 | 18 | 10 | 44 | 111 |

S1's summary values are literals, not formulas recalculating E3:E113. Neither source
workbook was edited or recalculated. S2's note about delivery does not override its actual
row values or the later lead adjudication.

From S3 to S1: 39 Demonstrated unchanged; 18 Partial → Demonstrated; 32 Missing →
Demonstrated; 3 Documentary → Demonstrated; 7 Documentary unchanged; 5 Missing →
Documentary; 7 Missing unchanged. Therefore 53 newly labeled Demonstrated, 58 total
changed labels, and zero newly established runtime results in this inspection.

All 18 formerly Partial rows retain “Remaining” clauses in S1 column F. S1's answer
label and those clauses conflict. Treat new labels as meeting intent/future targets until
each outcome has qualifying evidence; do not convert them into accepted completion.

S2 differs from S3 on 005, 006, 020, 023, 026, 035, 043, 077, 092, 104 and 106.
In particular, S2 labels training, knowledge transfer and dependency disclosure
Demonstrated; S3 classifies them Documentary, Missing and Documentary respectively.
This is not a simple chronological +3 improvement. Preserve both ledgers.

The earlier analysis's “45 clear plus eight ambiguous” is a planning assessment of the
53 promoted rows, not 45 executable tickets, accepted features or a three-day forecast.
Some unchanged rows contain important new intent; 041, 045, 047, 052, 055, 099 and 111
remain Missing in S1. Include their dependencies and exclusions without promoting them.

## Evidence taxonomy

Store separate dimensions; never overload one status column:
1. Implementation: absent, proposed, source-implemented, partially implemented.
2. Observation: unobserved, observed with limitation, observed for declared acceptance.
3. Delivery evidence: documentary, simulated, local synthetic, live sandbox, customer,
   production. These describe context; none implies another.
4. Decision: open, answered, conflict, locked, deferred.
5. Legacy adjudication: Demonstrated, Partial, Documentary, Missing exactly as S3.

An evidence record needs requirement ID, clause/outcome, exact candidate, input identity,
scope/time, environment, action, actual result, failure cases, artifact pointer, reviewer
and remaining limits. A proposal needs intended gate, not a fabricated evidence result.
A known function can be implemented but unobserved. An observed mock interaction can
remain Missing for a live-integration clause. Documentary evidence counts only where
substantive documents answer the requirement; it does not prove operational adoption.

## Requirement taxonomy

- Product behavior: imports, inventory, lifecycle, decisions, notices, views.
- Integration contracts: authority, identity, payloads, correlation and external outcomes.
- Operational behavior: recovery, health, retention and operator ownership.
- Qualification: security, scale, concurrency, resilience and migration evidence.
- Organizational evidence: methodology, training, support, commercial and reference proof.

`coverage.csv` contains all 111 sanitized generic topics, all three row classifications,
exact worksheet locators, candidate capability ID and evidence/task gates. It contains no
raw private questionnaire wording. No tasks have been approved or decomposed yet.

## Material conflicts

- “Demonstrated” meeting labels versus retained gaps and accepted evidence: keep both.
- Active-active intent versus current single-process/single-writer design: a new architecture
  decision and qualifying evidence would be required; not a packaging tweak.
- TLS note versus at-rest and in-transit requirement: one does not establish the other.
- Existing domain labels versus enforced authorization/tenant isolation: different behavior.
- Staged inventory versus a migration page implying cutover: compare/validate cannot silently promote.
- Reservation request versus existing pending request semantics: explicit new state needed.
- Provider-service operation versus API management of an existing service: unresolved boundary.
- Smaller endpoint reference versus a larger active-address deployment requirement: neither
  metric equivalence nor qualifying reference is established.
- Existing docs contain stale PART6_READY=no and old counts below controlling addenda:
  preserve history; propose corrections to lead later, do not rewrite global records here.

## Recovered handwritten source findings
Original temporary paths were unavailable. A bounded read-only search found retained
embedded PNG representations in the source task, each paired with its exact original
basename. Both 1368×1824 images were visually inspected without writing source copies.
Byte identity with the deleted original files cannot be confirmed.

Retained image identities:
- S7a SHA-256: `8a7568bf4274f4eb286a146e0c80123b6d6692abfceb80aff1635e972f1f0646`.
- S7b SHA-256: `a572dcf6f75908f99347b2b7e5ac74f6ca35582e9be81e9494f7caa8966c6d47`.

Sanitized derived intent: migration import/validation; subscriber/IP handling linked to
ticketing; lifecycle duration/default-policy questions; reservation/static-mode note;
domain/region and DHCP-block drilldown; utilization/formula disclosure; API documentation;
access-network targets; approval-driven DHCP orchestration; distinct alerts/alarms.
The license-expiry note clearly proposes an alarm while preserving running service rather
than shutdown. DNS automation is explicitly not recommended.

Unresolved wording: migration intermediate action; exact IP reassignment action; lifecycle
duration/escalation; reservation “static mode”; prefix proposal/removal; LDAP “outside
domain”; named-platform interface boundary. The event reference appears to be RFP-056,
but the number is uncertain. No implementation conclusion depends on that transcription.
The precise fragments do not change the eight previously identified ambiguous RFP rows;
they add workflow decisions to the same interview register.
