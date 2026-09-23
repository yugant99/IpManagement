# FR006 configured recipient source review

Explicit user disposition: one reviewed Operator recipient per domain/scope,
immutable notice-version binding, explicit in-app acknowledgement as receipt.
Configured recipient is not proof of business-owner identity. No external delivery
or historical receipt is inferred. Frozen wire: contracts/notice-recipient-wire.md.

T016A complete foundation author: Muse1.3 high, exact route
opencode-go/muse-spark-1.3-contributor#high, session
ses_f32eda1cbffeAumu1uotbBxqdf, draft PR89. Base
b24e50728c9dcd071a4f69534e9110c6d3e58348. Independent reviewer: GPT-6 Sol high.
Initial de7bdd25a5a970ae08266c17f3f917833da67dd6 returned for invalid standalone
SQLite RAISE, insufficient binding constraints and naive time override handling.
Correction38d7bc98a3e68e2e3af95c4199e1c18f1ef4bd3f closed invalid SQL construct
and UTC handling; Sol found nullable CHECK bypass and inconsistent legacy current
acknowledged state with an older acknowledgement version.

Candidate8cd51d583a75cb991bccf215590ba1b2f7efca24 adds explicit non-null/integer
constraints and the missing legacy state/version guard. Independent delta closure
closed with no remaining source blocker. Source integration suitability only;
no migration/DB/runtime acceptance is claimed.
The migration retains only actual known current and distinct older acknowledgement
versions as legacy_unbound; all original source history stays unchanged.

T016B remains the retained Luna lifecycle author lease; T017A remains the retained
Opus API author lease. They follow reviewed prerequisites on separate worktrees.
Source acceptance is distinct from T025 runtime evidence, portable evidence and
human signoff. No application tests/build/import/typecheck/lint/SQL/DB/runtime
checks ran. Tier B is locked and the next main merge remains T028.

## T016B full lifecycle source closure

Retained GPT-6 Luna high T016 author implemented lifecycle.py at
678cb8c118fc1baf0afeca0cbf775b2fe844e0eb (PR90), base
b52c0f9bf2290b66a1f7d9ae554b39a3d85a29b7. Existing workflow resolution already
preserves child history atomically, so no unnecessary workflow edit was made.
Lead returned enriched post-ack projection and resolved/current-ack semantics
before candidate publication. Independent GPT-6 Sol high found no blocking source
issue across complete binding/evaluate/ack/readback/redaction/history invariants.

A new due episode or explicit alarm/route/eligibility/legacy renewal creates one
immutable child version. Unrelated config revisions do not renew the same eligible
recipient. Exact-version GET authorizes the current canonical notice and retains
old own receipt redaction; missing legacy history is never fabricated. Ack checks
bound and current eligible Operator before replay, exact version/state/reason,
and writes child receipt, parent summary and audit in the caller transaction.
Resolution keeps history with acknowledgement_current=false. T017A required
configuration keywords and strict nested DTO wiring are still pending; this leaf
checkpoint is not a complete assembled API or runtime acceptance.

## T017A API and combined source closure

Retained Opus5.5 high author implemented app.py/models.py at
cae954c67b72ec7456244c7cb68a2db2ccd6a224 (PR91), base
efb85125d02f713af8d7cebaa10e16a8b1a671ee. Independent GPT-6 Sol high reviewed
this complete API and included schema/lifecycle invariants; no blocking finding.
All five notice leaf calls forward freshly reviewed configuration. The exact-version
GET scopes the canonical notice and validates returned version and parent identity.
Strict discriminated current/history DTOs retain redaction, legacy-versus-recipient
receipt and resolved/current distinctions. Evaluate exposes renewed_count; ack
validates the own exact requested receipt before committing or reporting replay.
Existing write orchestration reauthenticates and pins configuration inside its
transaction; no new external delivery or mutation-on-read path was added.

Pydantic RootModel/multiple-inheritance and actual route behavior remain unexecuted,
as do migration and concurrency. Source integration is suitable for T018/T023;
T025 remains necessary and prerequisite-gated. No application checks ran.
