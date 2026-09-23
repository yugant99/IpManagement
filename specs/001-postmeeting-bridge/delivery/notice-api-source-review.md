# T017 notice API source review

Complete author: Opus5.5 high in Claude Code, session695fa2f2-0540-45b1-9bd4-0a708a6e8137.
Exact sourcef7e3c986d165f1f88a5d02d07a44a12d26f1461a, PR87. Independent GPT-6 Sol
high reviewed the whole app/models feature against pinnedbasea4a57df and closed it
without blocking source findings. Integrated source11e6728317d9c2da5296975f3f2f1bbce516e785.

Source review covered selected-domain/parent scoping before projection and audit,
strict payload forwarding and actor checks, server UTC, atomic leaf/DTO rollback,
route precedence, exact nested response types, current static occupancy units/time/
provenance and unchanged saved DHCP metrics. Entitled Operators receive generic404
for foreign/absent resources; forbidden mutation roles receive403 before target lookup.

This is the pinned Operator-only notice API. The subsequent user-selected recipient
policy is separately specified in notice-recipient-wire.md and is not met by this
SHA. No tests/builds/imports/typechecks/DB/runtime or portable/human evidence ran.
T025 prerequisites remain unmet, T028 is next main merge and Tier B remains locked.
