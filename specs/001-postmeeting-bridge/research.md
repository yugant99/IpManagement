# Research and design decisions

Source inspection only; no application/test/benchmark execution. Independent contract_scout
supplied code seam and qualification research; source-recovery agent inspected retained
images and later supplied independent delivery answers. Actual review is in agent-grilling.md.

| Decision | Rationale / inspected source | Alternative rejected |
|---|---|---|
| Existing application/locks retained | pyproject.toml, uv.lock, frontend/package.json; source-seams.md | Stack upgrade or service extraction unrelated to required behavior |
| Server-derived token principal | app.py exposes all major reads; workflow.py fixed actors are not trusted identity | Actor dropdown masquerading as authorization; broad enterprise IdP integration |
| Whole-envelope deny with authorized derived projection | imports.py retains mixed immutable data; reports.py/runs include saved mixed-scope content | In-place raw redaction or UI-only filtering |
| Candidate assessment only | imports.py staging does not alter baseline; reports.compare_runs is different | Hidden cutover/promotion or duplicate parser |
| Narrow reservation table plus existing write transaction | workflow._eligibility/decide_request and app.write_operation use the existing allocation boundary | General hold framework, independent nontransactional availability query |
| Allocated release/reuse Tier B | schema allocations uniqueness plus allocation_requests FK require preserved history and reader updates | Delete allocation row or silently relax unique constraint |
| Durable internal ticket simulator | Current simulated downstream status has no ticket/correlation journal | Pretend ServiceNow endpoint or parallel provisioning simulator |
| Fixed exception/aging semantics | workflow.sync_exceptions requires comparable healthy evidence; ack is separate | Manual ticket closure clearing anomaly, new generic alarm engine |
| Current static holds separate from saved runs | calculations/rules preserve historical evidence snapshots | Retroactively changing stored utilization after reservation |
| Future scale/HA/encryption protocol | One worker and exclusive local store; no relevant new runtime evidence | Claiming scale from CIDR size or HA from packaging |
| Operator manifest includes config/code/UI | state_ops backups preserve SQLite, not installation assets or credentials | Snapshot presented as complete deployment recovery |
| No license implementation | Handwriting supplies future continuity intent, not commercial rules | Inventing grace periods or restricting new operations |

## Resolved source uncertainty
Two deleted temporary images were recovered as retained attachments and visually inspected;
original-byte identity remains unverified. Exact ambiguous phrases are resolved as design
scope rather than fabricated transcription. Product/instance credentials, human owners,
recipient acknowledgement and vendor mappings are not discoverable from provided sources.
They are external gates for excluded/live claims; they are not unresolved decisions in Tier A.

## Alternatives and decisions that matter
- Migration sign-off attests an immutable assessment only. A separate local request must
  establish its own subject/version/authority; no comparison-to-write shortcut.
- Fixed reviewed configuration holds token digests, roles/domains, source mapping, routing,
  policy and mode revisions. No admin UI or role designer.
- Enforce authorization before serialize/count/export. Unknown legacy scope is denied or
  quarantined, not assigned to a default domain.
- Loopback HTTP is acceptable only for this local synthetic boundary. Do not expose bearer
  tokens over an unqualified remote HTTP route. No TLS implementation is promised now.
- Q081–Q088 numeric targets are future qualification assumptions. Original source clause
  populations/recovery requirements control eventual RFP assessment.

## Toolkit provenance
Real Spec Kit v1.0.9 setup-plan ran after actual Q100 confirmation. Its logical feature
identifier is 001-postmeeting-bridge; Git branch remains codex/postmeeting-specification.
The local ignored .specify/feature.json pointer selects this feature. No extension hooks
are installed. See toolkit-record.md for pinned upstream commit and installation command.

## Independent source-review amendments
Global scheduler advances a singleton clock/cursor and imports the whole feed; global run
creation and exception sync cannot be authorized by filtering responses. Preserve those jobs
under a fixed coordinator credential with explicit complete synthetic scope/source grants.
Ordinary imports are intended candidates only, no callback/delegation. Cancel-own-pending
is deferred; abandoning migration review changes no persisted state. Import replay preserves
normalized JSON identity, not raw bytes. Spencer retains Dockerfile/Compose ownership.
Optional DHCP has its own conditional core persistence gate, independent of allocated release.
