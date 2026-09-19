"""Installed CLI. Setup is explicit and errors are visible with nonzero exits."""

import argparse
import json
import logging
import sqlite3
import sys
from uuid import uuid4

from .errors import AppError, store_error
from .seed import seed_baseline, seed_rich
from .state_ops import backup_database, reset_database, restore_database
from .store import data_directory, migrate_schema


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m ipam_demo", description="Synthetic IPAM inventory demo")
    commands = parser.add_subparsers(dest="command", required=True)
    serve = commands.add_parser("serve", help="Serve one local API/UI process; never seeds automatically")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    seed = commands.add_parser("seed", help="Initialize explicit synthetic inventory; stop the service first")
    seed.add_argument("--scenario", choices=["baseline", "rich"], required=True)
    seed.add_argument("--inventory", help="Rich inventory JSON path; required for rich, forbidden for baseline")
    commands.add_parser("migrate", help="Explicitly migrate recognized v1/v2 stores; stop the service first")
    backup = commands.add_parser("backup", help="Snapshot the complete store to a new file; stop the service first")
    backup.add_argument("--output", required=True)
    restore = commands.add_parser("restore", help="Validate and restore a snapshot, preserving the old store; stop the service first")
    restore.add_argument("--input", required=True)
    restore.add_argument("--confirm", action="store_true")
    reset = commands.add_parser("reset", help="Remove only the recognized application store; stop the service first")
    reset.add_argument("--confirm", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    try:
        if args.command == "seed":
            if args.scenario == "rich":
                if not args.inventory:
                    raise AppError("INVALID_SEED_OPTIONS", "Rich setup requires --inventory PATH.", 422)
                result = seed_rich(data_directory(), args.inventory)
            else:
                if args.inventory is not None:
                    raise AppError("INVALID_SEED_OPTIONS", "Baseline uses its packaged inventory; omit --inventory.", 422)
                result = seed_baseline(data_directory())
            print(json.dumps(result, indent=2))
        elif args.command == "migrate":
            print(json.dumps(migrate_schema(data_directory()), indent=2))
        elif args.command == "backup":
            print(json.dumps(backup_database(data_directory(), args.output), indent=2))
        elif args.command == "restore":
            print(json.dumps(restore_database(data_directory(), args.input, confirm=args.confirm), indent=2))
        elif args.command == "reset":
            print(json.dumps(reset_database(data_directory(), confirm=args.confirm), indent=2))
        else:
            if not 1 <= args.port <= 65535:
                raise AppError("INVALID_PORT", "Port must be between 1 and 65535.", 422)
            import uvicorn
            from .app import create_app
            uvicorn.run(create_app(), host=args.host, port=args.port, workers=1)
        return 0
    except (AppError, sqlite3.Error, OSError) as exc:
        if isinstance(exc, AppError):
            error = exc
        elif isinstance(exc, sqlite3.Error):
            logging.exception("SQLite operation failed")
            error = store_error(exc)
        else:
            error = AppError("FILESYSTEM_ERROR", "Cannot access configured app files. Check paths and permissions.", details={"reason": str(exc)})
        print(json.dumps(error.body(str(uuid4()))), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
