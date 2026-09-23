# T018 complete notice and occupancy UI source review

Author: Muse 1.3 high in OpenCode, retained session
`ses_f32c9e849ffe2Nu5nShr2wEUgI`, exact paid route
`opencode-go/muse-spark-1.3-contributor#high`. Independent reviewer: GPT-6 Sol high.
Common T018/T023 base: `5c2181c33ad8c841cc0cd0fb5a09b1cf495cbe33`.
Initial full candidate: `aff6e2cdeb161f6f17bbe5da6217183286293892`, PR93.
Final source: **`6173efa8e1d09e89cb35e44ffc99aa589bcaea63`**.

The feature adds scoped notice list/detail, explicit evaluation, configured-recipient
acknowledgement and historical exact-version receipt recovery. Current binding,
immutable history, legacy/unassigned/unavailable states and resolution remain
distinct. Minimal original-context pointers precede acknowledgement; the existing
workflow write lock, in-memory retry payload and context cancellation are retained.
Workflow and Capacity Reports show the same current static IPv4 metric identity,
units, components, server time and provenance separately from saved DHCP evidence.

Sol reviewed the full implementation and shared core/API/UI invariants. The
retained author corrected three findings, independently closed at the final SHA:

1. An acknowledged notification incorrectly claimed an own receipt for another
   principal, while resolved notices hid retained delivery history. Own receipt
   now requires the current actor; resolution and receipt remain separate facts.
2. List pagination/filtering discarded a recovered notice selection and its current
   detail. Selection now survives and loads current detail independently through
   the scoped API; original recovery evidence never substitutes for current state.
3. An uncertain acknowledgement retained an attempt that disabled direct GET
   recovery. Exact-version readback is now available without another POST or reload;
   failed/denied/mismatched readback retains the pointer, payload and write lock.
   Only the matching own original receipt clears both pointer and attempt.

Sol found no new blocker in the corrected selection, rendering, operation lock,
context guards or abort behavior. Only the three leased frontend files changed.
The configured recipient is not proven business owner, in-app receipt is not
external delivery, and acknowledgement never frees a reservation or resolves its
underlying condition.

No application tests, builds, typechecks, lint, imports, database or browser/runtime
checks ran. Rendering, concurrency, reload recovery and actual API behavior remain
unverified until T025 on the complete prerequisite candidate. No questionnaire
promotion, portable/human acceptance or main merge follows from source closure.
