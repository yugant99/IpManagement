#!/usr/bin/env python3
"""Focused local evidence for RFP-006, RFP-078 and RFP-033.

The script creates a fresh disposable store, starts the exact checkout's API on
loopback, and writes raw JSON/CSV evidence outside the repository. It does not
modify committed fixtures or any retained acceptance store.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import uuid


def call(base: str, method: str, path: str, payload=None) -> tuple[int, dict[str, str], bytes]:
    body = None if payload is None else json.dumps(payload, separators=(",", ":")).encode()
    request = Request(f"{base}{path}", data=body, method=method,
                      headers={"Accept": "application/json", **({"Content-Type": "application/json"} if body else {})})
    try:
        with urlopen(request, timeout=15) as response:
            return response.status, dict(response.headers.items()), response.read()
    except HTTPError as error:
        return error.code, dict(error.headers.items()), error.read()
    except URLError:
        return 0, {}, b""


def json_call(base: str, method: str, path: str, payload=None) -> tuple[int, dict[str, str], dict]:
    status, headers, body = call(base, method, path, payload)
    return status, headers, json.loads(body)


def write(root: Path, name: str, body: bytes) -> str:
    path = root / "artifacts" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    return str(path)


def header(headers: dict[str, str], name: str) -> str | None:
    return next((value for key, value in headers.items() if key.lower() == name.lower()), None)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--checkout", required=True, type=Path)
    parser.add_argument("--port", required=True, type=int)
    args = parser.parse_args()
    root = args.root.resolve()
    checkout = args.checkout.resolve()
    data = root / "data"
    root.mkdir(parents=True, exist_ok=True)
    data.mkdir(parents=True, exist_ok=True)
    (root / "artifacts").mkdir(exist_ok=True)
    (root / "derived").mkdir(exist_ok=True)
    # Keep the venv launcher path; resolving it can discard the venv on macOS.
    python = Path(sys.executable)
    env = {**os.environ, "IPAM_DATA_DIR": str(data), "IPAM_SYNTHETIC_FEED_DIR": str(checkout / "fixtures/v1"),
           "PYTHONPATH": str(checkout / "backend")}

    seed = subprocess.run(
        [str(python), "-m", "ipam_demo", "seed", "--scenario", "rich", "--inventory", str(checkout / "fixtures/v1/inventory.json")],
        cwd=checkout, env=env, capture_output=True, text=True, check=True,
    )
    write(root, "seed.json", seed.stdout.encode())
    process = subprocess.Popen(
        [str(python), "-m", "ipam_demo", "serve", "--host", "127.0.0.1", "--port", str(args.port)],
        cwd=checkout, env=env, stdout=(root / "artifacts/server.log").open("wb"), stderr=subprocess.STDOUT,
    )
    write(root, "runtime.json", json.dumps({"python": str(python), "checkout": str(checkout), "pid": process.pid,
                                              "port": args.port}, indent=2).encode())
    base = f"http://127.0.0.1:{args.port}"
    try:
        for _ in range(60):
            status, headers, body = call(base, "GET", "/healthz")
            if status == 200:
                write(root, "health.json", body)
                break
            time.sleep(0.1)
        else:
            raise RuntimeError("API did not become ready")

        # RFP-006: save a non-default filter and ordered column subset, reload,
        # export the pinned revision, and compare the CSV to the saved selection.
        status, headers, body = call(base, "POST", "/api/schedule/run", {
            "actor_id": "demo-approver", "reason": "focused report evidence acquisition",
            "idempotency_key": "easy-wins-cycle-1",
        })
        assert status == 201, body.decode()
        write(root, "rfp-006-acquisition.json", body)
        acquisition = json.loads(body)
        run_id = acquisition["run_id"]
        status, headers, body = call(base, "GET", f"/api/runs/{run_id}")
        assert status == 200, body.decode()
        run = json.loads(body)
        write(root, "rfp-006-run.json", body)
        finding = run["findings"][0]
        filters = {"scope_id": finding["subject"]["scope_id"], "evidence_state": finding["evidence_state"]}
        columns = ["subject", "scope_id", "evidence_state", "rule_id"]
        preset_payload = {"actor_id": "demo-approver", "reason": "pin filtered ordered report",
                          "name": "Focused filtered report", "run_id": run_id, "filters": filters, "columns": columns}
        status, headers, body = call(base, "POST", "/api/report-preset", preset_payload)
        assert status == 200, body.decode()
        write(root, "rfp-006-preset-save.json", body)
        status, headers, body = call(base, "GET", "/api/report-preset")
        assert status == 200, body.decode()
        preset = json.loads(body)
        write(root, "rfp-006-preset-get.json", body)
        assert preset["run_id"] == run_id and preset["filters"] == filters and preset["columns"] == columns
        status, export_headers, body = call(base, "GET", f"/api/report-preset/export?revision={preset['revision']}")
        assert status == 200, body.decode()
        write(root, "rfp-006-preset-export.csv", body)
        write(root, "rfp-006-preset-export-headers.json", json.dumps(export_headers, indent=2).encode())
        assert header(export_headers, "X-Preset-Revision") == preset["revision"]
        exported = list(csv.DictReader(body.decode().splitlines()))
        expected = [item for item in run["findings"] if all(
            (item["subject"].get(key) if key == "scope_id" else item.get(key)) == value
            for key, value in filters.items())]
        assert list(csv.reader(body.decode().splitlines()))[0] == columns
        assert len(exported) == len(expected) > 0
        for row, item in zip(exported, expected):
            assert row["subject"] == item["subject"]["cidr"]
            assert row["scope_id"] == item["subject"]["scope_id"]
            assert row["evidence_state"] == item["evidence_state"]
            assert row["rule_id"] == item["rule_id"]

        # RFP-078: deliberately fail a supported write and use its request ID
        # to prove the failure body, audit list and audit CSV are the same row.
        failed_payload = {"actor_id": "demo-approver", "reason": "capture failed report attempt",
                          "name": "Invalid focused report", "run_id": run_id,
                          "filters": {"unsupported_filter": "deliberate-failure"}, "columns": columns}
        status, failure_headers, body = call(base, "POST", "/api/report-preset", failed_payload)
        assert status == 422, body.decode()
        write(root, "rfp-078-failed-attempt.json", body)
        failure = json.loads(body)
        assert failure["error"]["details"]["audit_recorded"] is True
        request_id = failure["error"]["request_id"]
        status, headers, body = call(base, "GET", "/api/audit?limit=200")
        assert status == 200, body.decode()
        audit_page = json.loads(body)
        write(root, "rfp-078-audit-list.json", body)
        matching = [item for item in audit_page["items"] if item["details"].get("http_request_id") == request_id]
        assert len(matching) == 1
        status, audit_headers, body = call(base, "GET", "/api/audit/export")
        assert status == 200, body.decode()
        write(root, "rfp-078-audit-export.csv", body)
        audit_csv = list(csv.DictReader(body.decode().splitlines()))
        assert len(audit_csv) == audit_page["total"]
        audit_item = matching[0]
        assert audit_item["outcome"] == "failed"
        audit_by_id = {row["id"]: row for row in audit_csv}
        assert audit_item["id"] in audit_by_id
        assert audit_by_id[audit_item["id"]]["action"] == audit_item["action"]
        assert audit_by_id[audit_item["id"]]["outcome"] == audit_item["outcome"]
        assert audit_by_id[audit_item["id"]]["request_id"] == (audit_item["request_id"] or "")
        assert json.loads(audit_by_id[audit_item["id"]]["details"]) == audit_item["details"]

        # RFP-033: accepted routing input uses non-canonical IPv6 and offsets;
        # the record endpoint must expose canonical typed values and exact raw input.
        inventory = json.loads((checkout / "fixtures/v1/inventory.json").read_text())
        central = next(item for item in inventory["scopes"] if item["name"] == "Central")
        original = {"valid_from_at": "2026-08-31T16:00:00-08:00",
                    "valid_until_at": "2026-09-01T01:00:00+00:00",
                    "observed_at": "2026-08-31T23:00:00-01:00"}
        record = {"id": str(uuid.uuid4()), "source_record_id": "normalization-ipv6-001",
                  "scope_id": central["id"], "family": 6,
                  "cidr": "2001:0DB8:0080:0000::/64", "router_id": "router-normalization",
                  **original, "original_timestamps": original}
        envelope = {"schema_version": 1, "fixture_contract": "ipam-synthetic-v1", "synthetic": True,
                    "demo_clock_at": acquisition["demo_clock_at"], "source_id": "focused-normalization",
                    "source_run_id": "focused-normalization-001", "source_kind": "routing",
                    "source": {"name": "Focused normalization route", "owner": "local-evidence",
                               "authority": "observed", "required_for": ["routing_view"]},
                    "coverage": [{"scope_id": central["id"], "kind": "interval",
                                   "window_start_at": "2026-08-31T16:00:00-08:00",
                                   "window_end_at": "2026-09-01T01:00:00+00:00", "declared_complete": True}],
                    "records": [record]}
        write(root, "rfp-033-input-envelope.json", json.dumps(envelope, indent=2).encode())
        status, headers, body = call(base, "POST", "/api/imports", envelope)
        assert status == 201, body.decode()
        receipt = json.loads(body)
        write(root, "rfp-033-receipt.json", body)
        batch_id = receipt["id"]
        status, headers, body = call(base, "GET", f"/api/imports/{batch_id}/envelope")
        assert status == 200, body.decode()
        retained_envelope = json.loads(body)
        write(root, "rfp-033-retained-envelope.json", body)
        status, headers, body = call(base, "GET", f"/api/imports/{batch_id}/records")
        assert status == 200, body.decode()
        records = json.loads(body)
        write(root, "rfp-033-records.json", body)
        typed = records["items"][0]["typed"]
        raw = records["items"][0]["raw"]
        assert receipt["accepted_rows"] == 1 and receipt["rejected_rows"] == 0
        assert typed["cidr"] == "2001:db8:80::/64"
        assert typed["valid_from_at"] == "2026-09-01T00:00:00.000Z"
        assert typed["observed_at"] == "2026-09-01T00:00:00.000Z"
        assert raw["cidr"] == record["cidr"] and raw["valid_from_at"] == original["valid_from_at"]
        assert retained_envelope["records"][0]["cidr"] == record["cidr"]

        summary = {"candidate_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=checkout, text=True).strip(),
                   "root": str(root), "port": args.port,
                   "rfp_006": {"run_id": run_id, "preset_revision": preset["revision"], "filters": filters,
                               "columns": columns, "exported_rows": len(exported),
                               "csv_sha256": hashlib.sha256((root / "artifacts/rfp-006-preset-export.csv").read_bytes()).hexdigest()},
                   "rfp_078": {"failed_request_id": request_id, "audit_id": audit_item["id"],
                               "audit_recorded": failure["error"]["details"]["audit_recorded"], "audit_rows": len(audit_csv),
                               "csv_sha256": hashlib.sha256((root / "artifacts/rfp-078-audit-export.csv").read_bytes()).hexdigest()},
                   "rfp_033": {"batch_id": batch_id, "source_id": receipt["source_id"],
                               "source_run_id": receipt["source_run_id"], "source_record_id": record["source_record_id"],
                               "canonical_cidr": typed["cidr"],
                               "canonical_valid_from_at": typed["valid_from_at"],
                               "canonical_observed_at": typed["observed_at"]}}
        write(root, "summary.json", json.dumps(summary, indent=2).encode())
        print(json.dumps(summary, indent=2))
        return 0
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
