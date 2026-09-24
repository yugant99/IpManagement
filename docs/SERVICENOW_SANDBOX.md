# Optional ServiceNow sandbox Incident (RFP-042 bounded target)

An opt-in path on the existing workflow page. An authorized Operator opens an
existing simulated ticket handoff, explicitly sends **one** allowlisted synthetic
Incident to a ServiceNow Personal Developer Instance, and later manually refreshes
the external state after a human changes it in ServiceNow.

This is a **sandbox experiment**. A PDI is for individual learning, not business
use. A round trip qualifies only that sandbox. It is not production, customer,
enterprise-identity or provisioning evidence. The simulated handoff, the local
allocation ledger and provisioning (`not_requested`) keep their own state. The
external Incident never changes them, and closing the Incident resolves nothing
in IPAM.

## Server configuration

Configuration is server-side only. The browser cannot supply a URL, group,
assignee or free text. With `IPAM_SERVICENOW_ENABLED` unset or false, the path is
**disabled**: saved records stay readable and every send, lookup or refresh fails
with `SERVICENOW_DISABLED`. If the path is enabled but incomplete, the workflow
page names the invalid variables (never their values) and mutations fail with
`503 SERVICENOW_CONFIGURATION_INVALID`.

| Variable | Meaning |
| --- | --- |
| `IPAM_SERVICENOW_ENABLED` | `true` to opt in. |
| `IPAM_SERVICENOW_INSTANCE_URL` | Bare `https://<instance>.service-now.com` origin. No path, port, query or credentials. Redirects are refused. |
| `IPAM_SERVICENOW_USERNAME` | Dedicated machine identity with Table API GET/POST on `incident` only. |
| `IPAM_SERVICENOW_PASSWORD_FILE` | Path to a regular, owner-only (`0600`/`0400`) file owned by the service user, holding the password (one trailing newline allowed). The password is never in the environment, argv, URLs, logs, the database, snapshots or responses. |
| `IPAM_SERVICENOW_ASSIGNMENT_GROUP_SYS_ID` | Fixed Network assignment group `sys_id` (32 lowercase hex). |
| `IPAM_SERVICENOW_ASSIGNEE_SYS_ID` | Fixed test assignee `sys_id` (32 lowercase hex). |
| `IPAM_SERVICENOW_ALLOWED_DOMAIN` | The single synthetic IPAM domain allowed to send. Other domains are refused. |
| `IPAM_SERVICENOW_TIMEOUT_SECONDS` | Optional, 1–10, default 8 (below the UI's 12-second request timeout). |

The Compose package does not pass these variables. Use a local process run, for
example `uv run python -m ipam_demo serve`, with the usual `IPAM_DATA_DIR` and
`IPAM_ACCESS_CONFIG`. The database needs schema 8. Stop the service and run
`python -m ipam_demo migrate` on an existing schema 1–7 store. The migration only
adds the `servicenow_incidents` table and preserves existing rows.

## API (selected domain, current access pins)

- `GET /api/handoffs/{id}/servicenow`: Viewer and above. Returns the configuration status, stored record, allowed actions and history.
- `POST /api/handoffs/{id}/servicenow/send` `{actor_id, expected_version, idempotency_key}`: Operator. Use `expected_version` 0 before the first send.
- `POST /api/handoffs/{id}/servicenow/lookup` `{actor_id, expected_version}`: Operator. Runs a manual correlation lookup.
- `POST /api/handoffs/{id}/servicenow/refresh` `{actor_id, expected_version}`: Operator. Runs a manual GET of the saved `sys_id`.

Each mutation commits a prepare step, makes **one** HTTP call outside any SQLite
transaction, then commits the observed outcome. There is no PATCH, DELETE,
automatic retry or scheduler.

## Payload and state rules

- **POST fields:** `short_description`, a fixed synthetic `description` (correlation, domain, source request, action, reviewed versions, and a service reference only if it is a simple token), `correlation_id` (the intent's immutable correlation), `correlation_display=ipam-demo`, `impact=3`, `urgency=3`, and the fixed group and assignee.
- **Unknown before POST:** before POSTing, the record is saved as `unknown / send_in_flight`. A crash, timeout, 5xx, redirect or malformed/unexpected 2xx stays `unknown`. A definitive 4xx is `failed`. Only a validated `201` whose `correlation_id` matches exactly becomes `delivered`, storing `sys_id`, number, group, assignee, state and observation time.
- **No duplicate sends:** the same principal and key replays without a POST. Any unresolved send blocks a new one until a manual lookup records **`absent`**, meaning a complete response with zero exact correlation matches. Lookups are refused for 60 seconds after a send, so a slow commit cannot look absent.
- **Lookup outcomes:** a failed, malformed or truncated lookup is recorded as `last_error_code` and is not treated as absence. One exact match becomes `delivered`. Two or more give `duplicate_review`, listing their numbers for owner review in ServiceNow; lookup again after cleanup. An external `sys_id` already owned locally by another handoff also gives `duplicate_review` (`external_id_conflict`).
- **Refresh:** a successful refresh records group, assignee, state and observation time. A failed refresh, or one whose returned identity no longer matches, keeps the last observation and records the failure.

## Limits and unverified behavior

- Lookup absence is only as complete as the machine identity's read access. ServiceNow ACLs can silently hide rows.
- The correlation field is the standard `correlation_id`. It is not unique in ServiceNow, so duplicates are detected, not prevented, remotely.
- State codes shown as labels assume the out-of-box Incident choices (1 New, 2 In Progress, 3 On Hold, 6 Resolved, 7 Closed, 8 Canceled). Other codes display raw.
- Focused app checks use a fake HTTP transport. A separate operator-run check on the PDI confirmed one synthetic Incident POST (HTTP 201) and an exact `correlation_id` GET readback (HTTP 200). The full app workflow against the live PDI remains unverified.
