"""Sample-only Kea DHCPv4 memfile CSV to synthetic dhcp envelope converter.

Sample-only proof of format mapping, not a generic operator importer. Only
the tracked sample ``kea-leases4-sample.csv`` with the pinned SHA-256 below
is accepted; changing the sample needs a reviewed pin update. Conversion
requires an explicit sample flag plus a scope-map declaring
``synthetic_sample: true`` and repeating the same pinned filename and hash.
A renamed real export fails the hash gate and is never labeled synthetic.
A real operator export needs a reviewed non-synthetic contract, authority,
privacy and access gate before ingestion. No live API, connection or full
lease history is claimed. Converter-only in this iteration: no supported
import path exists for the emitted source ID (see integration memo).
"""

import csv
import hashlib
import json
from datetime import datetime, timezone
from ipaddress import ip_address
from pathlib import Path
import os
import tempfile
from uuid import UUID, uuid5

from .errors import AppError

EXPECTED_HEADER = (
    "address",
    "hwaddr",
    "client_id",
    "valid_lifetime",
    "expire",
    "subnet_id",
    "fqdn_fwd",
    "fqdn_rev",
    "hostname",
    "state",
    "user_context",
    "pool_id",
)
MAX_IMPORT_BYTES = 10 * 1024 * 1024
MAX_IMPORT_ROWS = 10_000
INFINITE_LIFETIME = 0xFFFFFFFF
SAMPLE_NAMESPACE = UUID("fed69f72-8aa8-48e5-896e-cc50e06bc004")
TRACKED_SAMPLE_FILENAME = "kea-leases4-sample.csv"
TRACKED_SAMPLE_SHA256 = "70d7f38d6686666cd01c97b4245ea26273c75ffa3df8e4da1e3b233c73325707"


def _iso_ms(epoch_seconds: int) -> str:
    instant = datetime.fromtimestamp(epoch_seconds, tz=timezone.utc)
    return instant.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _parse_clock(value: str, field: str) -> datetime:
    if not isinstance(value, str):
        raise AppError("KEA_SAMPLE_INVALID", f"Scope-map {field} must be a string.", 422)
    try:
        instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AppError("KEA_SAMPLE_INVALID", f"Scope-map {field} is not a valid timestamp.", 422) from exc
    if instant.tzinfo is None:
        raise AppError("KEA_SAMPLE_INVALID", f"Scope-map {field} must include a timezone.", 422)
    return instant.astimezone(timezone.utc)


def convert_kea(input_path: str, scope_map_path: str, output_path: str, synthetic_sample: bool) -> dict:
    if not synthetic_sample:
        raise AppError(
            "KEA_SAMPLE_FLAG_REQUIRED",
            "Refusing to label Kea data synthetic without --synthetic-sample. "
            "A real operator export needs a reviewed non-synthetic contract, authority, privacy and access gate.",
            422,
        )
    try:
        scope_map = json.loads(Path(scope_map_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise AppError("KEA_SAMPLE_INVALID", f"Cannot read scope-map: {exc}.", 422) from exc
    if not isinstance(scope_map, dict) or scope_map.get("synthetic_sample") is not True:
        raise AppError(
            "KEA_SAMPLE_FLAG_REQUIRED",
            "Scope-map must declare synthetic_sample: true for this sample-only converter.",
            422,
        )
    for field in ("demo_clock_at", "export_observed_at", "source_id", "source_run_id", "subnet_scope_map", "coverage"):
        if field not in scope_map:
            raise AppError("KEA_SAMPLE_INVALID", f"Scope-map is missing required field: {field}.", 422)
    demo_clock = _parse_clock(scope_map["demo_clock_at"], "demo_clock_at")
    export_observed = _parse_clock(scope_map["export_observed_at"], "export_observed_at")
    if export_observed > demo_clock:
        raise AppError("KEA_SAMPLE_INVALID", "export_observed_at must be at or before demo_clock_at.", 422)
    demo_epoch = int(demo_clock.timestamp())
    source_id = scope_map["source_id"]
    source_run_id = scope_map["source_run_id"]
    if not isinstance(source_id, str) or not source_id.strip():
        raise AppError("KEA_SAMPLE_INVALID", "Scope-map source_id must be a nonempty string.", 422)
    if not isinstance(source_run_id, str) or not source_run_id.strip():
        raise AppError("KEA_SAMPLE_INVALID", "Scope-map source_run_id must be a nonempty string.", 422)
    subnet_scope_map = scope_map["subnet_scope_map"]
    if not isinstance(subnet_scope_map, dict) or not subnet_scope_map:
        raise AppError("KEA_SAMPLE_INVALID", "Scope-map subnet_scope_map must be a nonempty object.", 422)
    for key, scope_id in subnet_scope_map.items():
        try:
            int(key)
        except ValueError as exc:
            raise AppError("KEA_SAMPLE_INVALID", f"Scope-map subnet key is not an integer: {key!r}.", 422) from exc
        try:
            UUID(str(scope_id))
        except ValueError as exc:
            raise AppError("KEA_SAMPLE_INVALID", f"Scope-map scope_id is not a UUID: {scope_id!r}.", 422) from exc

    raw_input = Path(input_path)
    try:
        body = raw_input.read_bytes()
    except OSError as exc:
        raise AppError("KEA_SAMPLE_INVALID", f"Cannot read input CSV: {exc}.", 422) from exc
    if len(body) > MAX_IMPORT_BYTES:
        raise AppError("KEA_SAMPLE_TOO_LARGE", "Kea sample CSV exceeds the 10 MiB limit.", 413)
    try:
        text = body.decode("utf-8")
    except UnicodeError as exc:
        raise AppError("KEA_SAMPLE_INVALID", f"Cannot read input CSV as UTF-8: {exc}.", 422) from exc
    expected_name = scope_map.get("expected_input_filename")
    if expected_name != TRACKED_SAMPLE_FILENAME or raw_input.name != TRACKED_SAMPLE_FILENAME:
        raise AppError(
            "KEA_SAMPLE_NOT_RECOGNIZED",
            f"This converter accepts only the tracked sample {TRACKED_SAMPLE_FILENAME!r}. "
            "A renamed export is rejected; changing the sample needs a reviewed pin update.",
            422,
        )
    expected_hash = scope_map.get("expected_input_sha256")
    if not isinstance(expected_hash, str) or expected_hash.lower() != TRACKED_SAMPLE_SHA256:
        raise AppError(
            "KEA_SAMPLE_NOT_RECOGNIZED",
            "Scope-map must repeat the tracked expected_input_sha256 pin.",
            422,
        )
    if hashlib.sha256(body).hexdigest() != TRACKED_SAMPLE_SHA256:
        raise AppError(
            "KEA_SAMPLE_NOT_RECOGNIZED",
            "Input SHA-256 does not match the tracked sample pin. "
            "A real operator export needs a reviewed non-synthetic contract and access gate.",
            422,
        )
    try:
        resolved_output = Path(output_path).expanduser().resolve()
        resolved_input = raw_input.expanduser().resolve()
        resolved_map = Path(scope_map_path).expanduser().resolve()
    except OSError as exc:
        raise AppError("KEA_SAMPLE_INVALID", f"Cannot resolve output path: {exc}.", 422) from exc
    if resolved_output in (resolved_input, resolved_map):
        raise AppError("KEA_SAMPLE_INVALID", "--output must not equal --input or --scope-map.", 422)

    lines = text.splitlines()
    if not lines:
        raise AppError("KEA_SAMPLE_INVALID", "Kea sample CSV is empty; header is required.", 422)
    reader = csv.reader(lines)
    try:
        header = next(reader)
    except csv.Error as exc:
        raise AppError("KEA_SAMPLE_INVALID", f"Cannot parse CSV header: {exc}.", 422) from exc
    if tuple(header) != EXPECTED_HEADER:
        raise AppError(
            "KEA_SAMPLE_INVALID",
            f"Kea CSV header must be exactly {','.join(EXPECTED_HEADER)}; got {','.join(header)}.",
            422,
        )
    try:
        rows = list(reader)
    except csv.Error as exc:
        raise AppError("KEA_SAMPLE_INVALID", f"Cannot parse CSV rows: {exc}.", 422) from exc
    if len(rows) > MAX_IMPORT_ROWS:
        raise AppError("KEA_SAMPLE_TOO_LARGE", "Kea sample CSV exceeds the 10,000 row limit.", 413)

    parsed: dict[str, dict] = {}
    input_rows = 0
    for line_number, row in enumerate(rows, start=2):
        if not row or all(cell == "" for cell in row):
            continue
        input_rows += 1
        if len(row) != len(EXPECTED_HEADER):
            raise AppError(
                "KEA_SAMPLE_INVALID",
                f"Row {line_number}: expected {len(EXPECTED_HEADER)} columns, got {len(row)}.",
                422,
            )
        entry = dict(zip(EXPECTED_HEADER, row))
        try:
            address = str(ip_address(entry["address"].strip()))
            if ip_address(address).version != 4:
                raise ValueError("address must be IPv4")
        except ValueError as exc:
            raise AppError("KEA_SAMPLE_INVALID", f"Row {line_number}: invalid address: {exc}.", 422) from exc
        hwaddr = entry["hwaddr"].strip()
        client_id_raw = entry["client_id"].strip()
        if not hwaddr and not client_id_raw:
            raise AppError(
                "KEA_SAMPLE_INVALID",
                f"Row {line_number}: empty client identity (both hwaddr and client_id are blank).",
                422,
            )
        try:
            valid = int(entry["valid_lifetime"].strip())
            expire = int(entry["expire"].strip())
        except ValueError as exc:
            raise AppError("KEA_SAMPLE_INVALID", f"Row {line_number}: epoch/lifetime must be integers.", 422) from exc
        if not 0 <= valid <= 0xFFFFFFFF or expire < 0:
            raise AppError("KEA_SAMPLE_INVALID", f"Row {line_number}: epoch/lifetime out of range.", 422)
        if valid == INFINITE_LIFETIME:
            raise AppError(
                "KEA_SAMPLE_INVALID",
                f"Row {line_number}: infinite valid_lifetime (0xffffffff) cannot be represented as a bounded lease interval.",
                422,
            )
        if expire - valid < 0:
            raise AppError("KEA_SAMPLE_INVALID", f"Row {line_number}: expire minus valid_lifetime underflows.", 422)
        subnet_key = entry["subnet_id"].strip()
        try:
            subnet_id = int(subnet_key)
        except ValueError as exc:
            raise AppError("KEA_SAMPLE_INVALID", f"Row {line_number}: subnet_id must be an integer.", 422) from exc
        if subnet_key not in subnet_scope_map and str(subnet_id) not in subnet_scope_map:
            raise AppError(
                "KEA_SAMPLE_INVALID",
                f"Row {line_number}: subnet_id {subnet_id} has no explicit scope mapping.",
                422,
            )
        for flag in ("fqdn_fwd", "fqdn_rev"):
            if entry[flag].strip() not in ("0", "1"):
                raise AppError("KEA_SAMPLE_INVALID", f"Row {line_number}: {flag} must be 0 or 1.", 422)
        try:
            state = int(entry["state"].strip())
        except ValueError as exc:
            raise AppError("KEA_SAMPLE_INVALID", f"Row {line_number}: state must be an integer.", 422) from exc
        if state not in (0, 1, 2, 3):
            raise AppError("KEA_SAMPLE_INVALID", f"Row {line_number}: state must be 0, 1, 2 or 3.", 422)
        key = address
        parsed[key] = {
            "line_number": line_number,
            "address": address,
            "hwaddr": hwaddr,
            "client_id_raw": client_id_raw,
            "valid": valid,
            "expire": expire,
            "subnet_id": str(subnet_id),
            "state": state,
        }

    unique_keys = len(parsed)
    duplicate_rows_collapsed = input_rows - unique_keys
    skipped_state = 0
    skipped_expired = 0
    observed_at = export_observed.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    records = []
    for address in sorted(parsed, key=lambda item: int(ip_address(item))):
        item = parsed[address]
        if item["state"] != 0:
            skipped_state += 1
            continue
        if item["expire"] <= demo_epoch:
            skipped_expired += 1
            continue
        subnet_key = item["subnet_id"]
        scope_id = str(subnet_scope_map[subnet_key])
        start_epoch = item["expire"] - item["valid"]
        if start_epoch > demo_epoch:
            raise AppError(
                "KEA_SAMPLE_INVALID",
                f"Scoped address {address}: derived lease start is after the demo clock.",
                422,
            )
        lease_start_at = _iso_ms(start_epoch)
        lease_end_at = _iso_ms(item["expire"])
        client_id = item["client_id_raw"] if item["client_id_raw"] else f"hwaddr:{item['hwaddr'].lower()}"
        source_record_id = f"kea-sample-s{subnet_key}-{address}"
        record_id = str(uuid5(SAMPLE_NAMESPACE, f"kea-sample-v1/{source_id}/{source_run_id}/{source_record_id}"))
        records.append(
            {
                "id": record_id,
                "source_record_id": source_record_id,
                "scope_id": scope_id,
                "family": 4,
                "address": address,
                "client_id": client_id,
                "lease_start_at": lease_start_at,
                "lease_end_at": lease_end_at,
                "observed_at": observed_at,
                "original_timestamps": {
                    "lease_start_at": lease_start_at,
                    "lease_end_at": lease_end_at,
                    "observed_at": observed_at,
                },
            }
        )

    coverage = scope_map["coverage"]
    if not isinstance(coverage, list) or not coverage:
        raise AppError("KEA_SAMPLE_INVALID", "Scope-map coverage must be a nonempty array.", 422)
    mapped_scopes = set(subnet_scope_map.values())
    for entry in coverage:
        if not isinstance(entry, dict):
            raise AppError("KEA_SAMPLE_INVALID", "Scope-map coverage rows must be objects.", 422)
        for field in ("scope_id", "kind", "window_start_at", "window_end_at", "declared_complete"):
            if field not in entry:
                raise AppError("KEA_SAMPLE_INVALID", f"Scope-map coverage is missing {field}.", 422)
        try:
            coverage_scope = str(UUID(str(entry["scope_id"])))
        except ValueError as exc:
            raise AppError("KEA_SAMPLE_INVALID", "Scope-map coverage scope_id is not a UUID.", 422) from exc
        if coverage_scope not in mapped_scopes:
            raise AppError("KEA_SAMPLE_INVALID", "Scope-map coverage scope is not in subnet_scope_map.", 422)
        if entry["kind"] != "interval":
            raise AppError("KEA_SAMPLE_INVALID", "Scope-map coverage kind must be interval.", 422)
        if entry["declared_complete"] is not False:
            raise AppError("KEA_SAMPLE_INVALID", "Sample coverage declared_complete must be explicit boolean false.", 422)
        start = _parse_clock(entry["window_start_at"], "coverage.window_start_at")
        end = _parse_clock(entry["window_end_at"], "coverage.window_end_at")
        if not start < end <= export_observed <= demo_clock:
            raise AppError(
                "KEA_SAMPLE_INVALID",
                "Coverage must satisfy start < end <= export_observed_at <= demo_clock_at.",
                422,
            )
    envelope = {
        "schema_version": 1,
        "fixture_contract": "ipam-synthetic-v1",
        "synthetic": True,
        "demo_clock_at": demo_clock.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "source_id": source_id,
        "source_run_id": source_run_id,
        "source_kind": "dhcp",
        "source": {
            "name": "Kea lease export sample (local file)",
            "owner": "Coastal Network Team",
            "authority": "observed",
            "required_for": ["dhcp_history"],
        },
        "coverage": coverage,
        "records": records,
    }

    output = Path(output_path)
    payload = json.dumps(envelope, indent=2, sort_keys=False) + "\n"
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix=output.name + ".", suffix=".tmp", dir=str(output.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
            os.replace(tmp_name, output)
        finally:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
    except OSError as exc:
        raise AppError("KEA_SAMPLE_INVALID", f"Cannot write output envelope: {exc}.", 422) from exc

    return {
        "status": "converted",
        "synthetic_sample": True,
        "input_rows": input_rows,
        "unique_addresses": unique_keys,
        "duplicate_rows_collapsed": duplicate_rows_collapsed,
        "skipped_state": skipped_state,
        "skipped_expired": skipped_expired,
        "emitted_records": len(records),
        "output": str(output),
        "source_id": source_id,
        "source_run_id": source_run_id,
        "demo_clock_at": envelope["demo_clock_at"],
        "observed_at": observed_at,
        "limitations": [
            "Converter-only: no current supported authenticated API/CLI import path exists for this source ID; this conversion is not an import receipt.",
            "Sample-only synthetic conversion; not a live Kea API, connection or full lease history.",
            "Coverage is a bounded snapshot window from the sample scope-map, not history and not inferred from present leases.",
            "Counts above are converter skips; they are not importer receipts.",
        ],
    }
