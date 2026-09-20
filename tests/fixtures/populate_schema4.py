"""Populate disposable v4 state using the pinned historical application only."""

import json
from pathlib import Path
import sys
from threading import Lock

from ipam_demo import reports, workflow
from ipam_demo.scheduler import SyntheticScheduler
from ipam_demo.seed import seed_rich
from ipam_demo.store import SCHEMA_VERSION, connect, exclusive_data_access


def main():
    if SCHEMA_VERSION != 4:
        raise RuntimeError("This fixture must run against the genuine schema-4 source archive")
    directory, fixtures = map(Path, sys.argv[1:])
    seed_rich(directory, fixtures / "inventory.json")
    with exclusive_data_access(directory) as database:
        scheduler = SyntheticScheduler(database, Lock())
        # No timer thread or server is started. One real manual acquisition
        # populates evidence, a saved run, exceptions, audit and replay records.
        cycle = scheduler.run_now({"actor_id": "demo-approver", "reason": "State preservation fixture",
                                   "idempotency_key": "state-v4-cycle"})
        with connect(database) as connection, connection:
            connection.execute("BEGIN IMMEDIATE")
            status = workflow.workflow_status(connection)
            request, _ = workflow.create_request(connection, {
                "actor_id": "demo-requester", "idempotency_key": "state-v4-allocation",
                "pool_id": status["pool"]["id"], "candidate": "10.40.2.3",
                "pool_version": status["pool"]["pool_version"],
                "baseline_version": status["baseline_version"],
                "owner": "Synthetic state check", "purpose": "Preservation", "reason": "Prepare fixture",
            })
            workflow.decide_request(connection, request["id"], {
                "actor_id": "demo-approver", "action": "approve", "reason": "Independent fixture decision",
            })
            exception = workflow.list_exceptions(connection)[0]
            transferred = workflow.update_exception(connection, exception["id"], {
                "actor_id": "demo-requester", "version": exception["version"], "action": "handoff",
                "recipient_actor_id": "demo-approver", "reason": "Preserve owner and handoff",
            })
            workflow.update_exception(connection, exception["id"], {
                "actor_id": "demo-approver", "version": transferred["version"],
                "action": "acknowledge", "reason": "Preserve acknowledgement",
            })
            reports.save_preset(connection, {
                "actor_id": "demo-approver", "reason": "Preserve saved report",
                "name": "State fixture", "run_id": cycle["run_id"], "filters": {},
            })
            scheduler.configure(connection, {
                "actor_id": "demo-approver", "reason": "Keep fixture stopped and disabled",
                "enabled": False, "interval_hours": 12, "expected_config_version": 1,
            })
            # Deliberate migration control: a changed legacy prefix with an
            # unchanged pool version must receive the conservative history flag.
            connection.execute("UPDATE prefixes SET version=2 WHERE id=("
                               "SELECT prefix_id FROM pools WHERE management_mode='dhcp' ORDER BY id LIMIT 1)")
        print(json.dumps({"schema_version": SCHEMA_VERSION, "cycle": cycle,
                          "allocation_request_id": request["id"], "exception_id": exception["id"]}))


if __name__ == "__main__":
    main()
