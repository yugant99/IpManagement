# Easy-wins evidence handoff

Status: **READY FOR PROJECT-LEAD REVIEW — focused existing-path evidence**

Owner lane: `codex/easy-wins-evidence`  
Lead: Main Lead 3.0, task `01a0c0c1-3952-7720-93c8-ff49192b8e13`  
Candidate baseline: `852010a311065a9cc0258fc4e3f5c1c1a889329a`  
Evidence date: 2026-09-20  
Scope: RFP-006, RFP-078, RFP-033 only

## Result

The three focused checks completed against a fresh disposable native store and
the real loopback API. No application/frontend/schema/lock/fixture or global
status files were changed. No Docker, VM/cloud, deployment, TLS, hot-snapshot
or broad E2E work was performed.

### RFP-006 — saved filtered report and pinned CSV

Works now on the baseline. One acquisition produced run
`249eb21b-4e0e-4ddc-bc87-73119b2a1b80`. A real preset was saved and reloaded
with filters:

```json
{"scope_id":"2c4a5913-e80c-53e9-9ba1-fd6c87ec6f4c","evidence_state":"healthy"}
```

The ordered, non-default column subset was
`subject,scope_id,evidence_state,rule_id`. The returned pinned revision was
`1ee51bd935bbdd36958274393ff4cdb73aa031629aa8e0ad6f340d9845e1efd2`; export
returned the same revision header, the same selected columns and 26 rows. The
script compared every exported row to the selected run/filter calculation.

### RFP-078 — audit CSV and generated failure

Works now for the bounded API audit path. A deliberately invalid report-preset
write returned `INVALID_INPUT` with `audit_recorded=true`. HTTP request ID:
`bd0096fc-678c-4b68-8124-ae1e6c9f7b4d`; persisted failed audit ID:
`f0dd07c2-36e5-45e8-bd0e-3802a776b660`. The full audit list/export contained
14 rows; the script selected the matching failure by the recorded
`details.http_request_id` and compared ID, action, outcome, request ID and
structured details between the list and CSV. This is not a claim of complete
system configuration audit or compliance reporting.

### RFP-033 — canonical typed values plus retained raw input

Works now for one supported synthetic routing envelope. Batch
`a6eb653d-08e5-4b2b-9b5e-23323f853d73`, source ID `focused-normalization`,
source run `focused-normalization-001`, and source record
`normalization-ipv6-001` were accepted. Input CIDR
`2001:0DB8:0080:0000::/64` became typed
`2001:db8:80::/64`. Offset timestamps such as
`2026-08-31T16:00:00-08:00` and `2026-08-31T23:00:00-01:00` became
`2026-09-01T00:00:00.000Z`; the raw row and original timestamp envelope retain
the exact submitted forms. The import is synthetic and does not promote or
alter intended inventory.

## Reproduction and evidence root

The committed minimal runner is
[`scripts/evidence/easy_wins_existing.py`](../../scripts/evidence/easy_wins_existing.py).
The actual run used a new Python 3.12 environment with locked dependencies,
then:

```sh
cd /Users/yuganthareshsoni/.codex/worktrees/04a6/Ip_inventory
uv venv /Users/yuganthareshsoni/Ip_inventory-easy-wins-20260920-NdavJp/venv --python 3.12
VIRTUAL_ENV=/Users/yuganthareshsoni/Ip_inventory-easy-wins-20260920-NdavJp/venv uv sync --active --frozen --no-dev
/Users/yuganthareshsoni/Ip_inventory-easy-wins-20260920-NdavJp/venv/bin/python \
  scripts/evidence/easy_wins_existing.py \
  --root /Users/yuganthareshsoni/Ip_inventory-easy-wins-20260920-run-GLGJ22 \
  --checkout /Users/yuganthareshsoni/.codex/worktrees/04a6/Ip_inventory \
  --port 18942
```

Disposable evidence root:
`/Users/yuganthareshsoni/Ip_inventory-easy-wins-20260920-run-GLGJ22`

Key artifact hashes:

- RFP-006 CSV: `02eeba7b245652dab8ad84ec0861116c85ce17635eedbeb69338f8fb1fe1562c`
- RFP-078 CSV: `bcc7e086a940948ae6630610edfde49288dc62cab88cf35d1779fc6f9113646f`

The root contains `summary.json`, raw API artifacts, derived input envelope,
and service log. The service was stopped by the runner's `finally` cleanup;
port `18942` is no longer owned by this check. The SQLite store and raw bulky
artifacts remain outside Git for lead inspection and can be removed after the
lead no longer needs them.

## Remaining gates / next owner

The project lead should review the exact artifacts, decide whether to update
the three row-map entries, and coordinate any merge. The evidence does not
close the broader limitations recorded in the row map and does not alter the
controlling 32/22/10/47 accounting. No PR was opened or pushed from this lane
yet; the next action is lead review of this commit and the disposable root.
