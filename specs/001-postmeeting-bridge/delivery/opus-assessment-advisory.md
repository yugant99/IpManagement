# Bounded Opus5.5 assessment advisory

User-authorized single read-only response through the existing Claude Max connection.
Claude Code2.1.280; exact response model `claude-opus-5-5`, high effort, tools disabled.
Session `d999c245-03ec-4915-8675-6018dfc09185`; source candidate
`833c2c8676b205c97476ab71f4e3b2cff0a2c608`. Scope was the T008 authority-revision,
assessment-digest and sign-off encoding question, not a code or whole-project review.

The successful response took71.333 seconds and one turn. Reported usage:2 uncached
input tokens,5800 cache-creation input,531 cache-read input and7002 output tokens
(including4686 thinking tokens). Provider usage telemetry is not an extra-charge receipt.
No second invocation, Fable call, OpenCode retry or paid-overage activation followed.
Evidence remains at /tmp/ipam-opus-t008-review (prompt.txt, response.jsonl, review.md,
stderr.txt, session-id.txt and progress.md); no private source or credentials were sent.

## Advice and lead disposition

Opus judged the existing schema sufficient if authority_revision uses a strict tagged
canonical composite, the assessment digest excludes mutable sign-off fields, and the
creation receipt anchors that digest. It highlighted loose revision-only comparison,
digest changes caused by signing/order/canonicalization, and split authority/baseline
checks as concrete traps. Explicit extra config columns were optional, not required.

Astra accepts the existing-schema approach under the exact amendment in
[contracts/migration.md](../contracts/migration.md). The lead refines receipt replay:
returning the historical success must not imply current sign-off after governance or
baseline changes; reauthorize first and expose current staleness separately. A mapping
version must be derived from reviewed mapping authority, never accepted as a free client
label. Luna receives this decision within its one-file T008 implementation lease.

This is advisory evidence only. No implementation, test, build, database, runtime,
portability, human or production acceptance is established. Sol remains the independent
source reviewer and Astra retains acceptance. No further Opus task is queued.
