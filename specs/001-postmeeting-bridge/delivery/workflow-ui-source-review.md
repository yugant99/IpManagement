# T015 complete workflow UI source review

Author: Muse1.3 high in OpenCode, retained session
ses_f32fa18a3ffeyQNRKi43do4bPA. Independent reviewer: GPT-6 Sol high.
Initial full candidate:06f9a15080fce5b860d5d5cd58c5de1d41f95432, draftPR88,
basea4a57df4921fd60b66a923820d908ce8a7d2e865. Not source-accepted.

Sol's whole-feature review returned this correction batch to the original author:

1. Independent Approver receives requester actor_id=null; the response validator
   incorrectly requires string and fails both successful decisions and recovery.
   Permit redacted foreign requester but retain own actor checks for creation.
2. Failed ticket lookup is unknown, not proof of legacy request. Decision controls
   must wait for a successful same-request-ID lookup; clear prior selection state.
3. Allocation-decision recovery pointer must retain minimal intended approve/reject
   and match that terminal state, not any later own terminal decision.
4. Ticket recovery needs exact target plus action-specific original operation shape;
   release-decision recovery must reconcile both proposal and reservation identity.
5. Display original reservation/proposal/assignment/event fields separately from
   current state instead of only a generic recovered message.
6. New path banner must say ticket simulated and provisioning unsupported/not
   requested; retain stored legacy simulated labels only as historical results.

The reviewed feature otherwise uses actual T012/T014 fields, persists minimal
original-context pointers before writes, retains attempt pointer on every failed
POST and gates new attempts using server availability. Exact author corrections
and independent closure are still pending. Recipient/notice UI is T018.

No application tests, builds, imports, typechecks, lint, DB or browser/runtime
checks ran. No runtime/portable/human acceptance, row promotion or main merge.
T025/T028 and Tier B boundaries remain unchanged.
