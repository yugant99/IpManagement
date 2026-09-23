# C-T: internal-ticket-simulator/v1

Q047–Q070; FR-004/009/011. One durable local simulator, no ServiceNow endpoint or credentials.

## Proposed interface and payload
- Request submission atomically records one intent with stable correlation.
- GET /api/handoffs and /{id}: scoped local decision, ticket delivery/receipt, readback state.
- POST /api/handoffs/{id}/attempt: operator, expected intent/version, stable key and one
  allowlisted synthetic scenario (success, definitive failure, committed-response-lost,
  no-effect-response-lost). Production/vendor effects are unavailable.
- POST /api/handoffs/{id}/readback: operator, correlation and matching digest; recorded lookup.
- POST /api/handoffs/{id}/acknowledge: explicitly simulated recipient acknowledgement.
- POST /api/handoffs/{id}/reassign: operator, expected intent version, stable key and
  reason; select the unique team from the current reviewed configuration, never a
  caller-supplied destination. Permitted only while routing_blocked or pending with
  zero attempts. Reassignment to a valid route returns the same intent to pending.
Payload allowlist: domain/action, opaque service reference when required, source request ID,
correlation, relevant revision, reason code and authorized evidence reference. No raw source
envelope, profile, token, private worksheet or attachment upload.
Fixed domain/action team map must have exactly one match; preserve route revision. A route
change is a reviewed configuration revision and explicit reassignment, never silent retry.
Keep an append-only route assignment version with configuration/route revision, team,
assigning principal, reason and UTC. Initial routing may be blocked with no team.
The immutable business payload digest excludes route/team and assignment metadata;
reassignment changes neither logical identity, business payload nor correlation. Every
attempt pins the selected assignment version and allowlisted synthetic scenario in its
own request digest and retained record. After any attempt exists, route reassignment is
unsupported in Tier A and requires visible owner resolution, not a replacement intent.
Recheck current authority/configuration before retry/readback; a route revision change
does not grant permission to change the attempted team. Valid readback/history remain
available under their C-A rights even when new attempts are blocked.

## State and crash boundary
One logical intent per domain/request/action; same identity changed payload is409. Persist
intent in local request transaction. Simulator effect commit is durable and distinct from
recording the observed response. This allows a restart between effect and acknowledgement.
Readback returning found/matching attaches its actual synthetic ID; successful definitive
absence permits another attempt; readback error remains unknown. A timeout never fabricates ID.
Three total attempts including first; five-second per-attempt observation budget, manual only.
An uncertain attempt reserves its ordinal before effect; crash cannot reset budget.
Exhausted budget requires owner review, not a new logical ID. No queue or automatic backlog drain.
Disable blocks new attempts, leaves readback/history available and preserves committed effects.
A previously failed route cannot silently change payload/team on retry.

## Independence
Local allocation approval can commit despite routing/delivery failure. Show each state
separately. Tier A provisioning is unsupported/not requested. Simulated acknowledgement
does not approve IPAM changes or resolve findings. External approval is never trusted.
Existing downstream_status remains historical compatibility data for old requests; new
hand-off records are authoritative for new simulated ticket outcomes, not hidden overrides.
Old records without a handoff say not tracked, not retroactively simulated ticket delivered.
UI shows “Simulated ticketing handoff — ServiceNow mapping pending.”

Future live implementation needs official product/version/interface, instance table/mapping,
auth scopes, real idempotency/lookup/readback/rate/error contract and authorization. None is
filled with guesses. Related CMDB/OSS/BSS remain matrix gaps. Optional DHCP simulation uses
its own separately settled fixture/readback contract, not this ticket's authority.
