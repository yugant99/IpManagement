# T014 ticket API source review

Author: native GPT-6 Luna high /root/t014_ticket_api. Independent reviewer: GPT-6
Sol high. Lead: Astra/Main Lead5. Final source1b00a66ee1fc9fe9340ad27ec2b3a41b29156ac8
(PR86), reviewed corea5ce063f2e350fe854c9e10a0d35cd439dd042e2. Integrated source
ede6cb6511c71011e6295fd46bf9d7c400a7db39 in draftPR84, not main.

Full review covered scoped list/detail/mutations, current authorization/config,
three separately committed attempt phases, no phase continuation on reserve replay,
unknown/readback requirement after partial failure, sanitized strict nested DTOs,
exact-key receipt recovery and allocation-create recovery. Findings were returned
to the original author: canonical allocation key must match both stored column and
normalized payload under own principal/scope; reassignment requires exact operation
identity rather than an arbitrary own assignment. The first closed at0e5d1046; the
second triggered retained Opus T013 anchor/helper correction and T014 shared helper
adoption. Sol independently closed all known source findings at the exact final SHA.

ApiError drops late-phase recovery details in the current client. T015 uses durable
original-context pointers and exact-key GET authority, retains pointer on any failed
attempt POST, and never automatically replays/resumes an attempt or replaces its key.
Sol reviewed this UI wire as compatible. Runtime behavior is still unverified.

No tests, imports, builds, typechecks, database or application checks ran. T025 is
prerequisite-gated with disposable synthetic data only. No portable/human evidence,
row promotion, infrastructure or deployment; Tier B stays locked and T028 remains
the next main merge.
