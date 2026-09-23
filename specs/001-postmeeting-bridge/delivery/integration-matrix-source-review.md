# T020 integration matrix source review

Author: Muse 1.3 high in OpenCode, session `ses_f32b85484ffe3rzKZMmJ8uKzG3`.
Independent reviewer: GPT-6 Sol high. Base:
`b8f294fc19b635dcf3c784125fd804d8a1a2616b`; PR94.
Initial candidate: `4c55eb7101263654fc6803978dce7e670933de70`.
Final source: **`1123146ce60ac3636d9a38af8be90467c1df90bf`**.

The whole-document review covered questionnaire membership, current API contracts,
authority, history, simulation and vendor unknowns. The retained author corrected:

- Four explicitly T020-gated rows omitted from the first inventory. The final
  48 included IDs contain all 36 required IDs (19 Integration + 28 T020-gated,
  overlapping by 11), plus 12 explained cross-category IDs. The remaining 63
  retain explicit dispositions. Existing questionnaire evidence classes are unchanged.
- Unknown ticket delivery can resolve through an exact persisted effect found,
  as well as through definitive absence with the appropriate failure fence.
- Schedule GET status, always-refused configuration POST and manual run POST
  now match source. Historical controls are not described as current authority.
- Current reservation/extension/unused release, deferred allocated reclaim,
  unsupported provisioning and distinct allocation/ticket status fields are separated.
- Historical finding/exception notifications are distinct from reservation expiry
  notices; reservation receipt does not clear an exception or free a hold.
- Detailed ticket readback and reservation release bodies now use exact accepted
  field names instead of rejected `key` or `digest` aliases.
- Current preparation ownership follows the explicit user reassignment to agents;
  Spencer references are historical, and human acknowledgement remains unobserved.

Sol independently closed the complete correction at the final SHA and found no
remaining source blocker. T021 and T022 may use this reviewed matrix. No tests,
builds, imports, database or application runtime checks ran. This document does not
establish vendor integration, portable/human evidence, questionnaire promotion or
main readiness. T025/T028 and Tier B gates remain unchanged.
