# Core SQLite state operations

**Source implementation; runtime evidence pending.** These commands extend the Stage 2 foundation and consume Stage 3's shared schema-v3/legacy-version contract. They were authored and source-reviewed without running the application, state commands, tests or builds. This document supplies core behavior for Spencer's packaging/runbook; it does not change his owned files or declare `PART6_READY=yes`. See the [schema compatibility handoff](handoffs/part-1-state-schema-compat.md) for exact combined dependencies and the narrow follow-up change.

Contribution: G27 core state correctness / RFP-018. No measured recovery objective, disaster-recovery, cross-host or allocation/audit persistence evidence is claimed.

## Commands and operating boundary

Use the installed Python environment and the same absolute `IPAM_DATA_DIR` used by the service. The directory must already exist on a supported local macOS/Linux filesystem. **Stop the service and other database tools before all three commands, including backup.** Each reuses `exclusive_data_access` and its nonblocking `.ipam_demo.lock`; a running service/seed/migrate/state owner returns `DATA_IN_USE`. A leftover lock file is normal; never delete it to bypass a held lock.

The following are documented interfaces, **not commands executed for this task**:

```sh
python -m ipam_demo backup --output /absolute/existing-directory/new-snapshot.sqlite3
python -m ipam_demo restore --input /absolute/existing-directory/new-snapshot.sqlite3 --confirm
python -m ipam_demo reset --confirm
```

Restore/reset reject a missing confirmation before taking the data lock or creating temporary files. No environment default or interactive answer substitutes for `--confirm`. Existing `serve`, `seed` and `migrate` parser/dispatch behavior remains intact. State operations never call seed, initialization or migration implicitly.

The main file is exactly `IPAM_DATA_DIR/ipam_demo.sqlite3`. Only its exact `-wal`, `-shm`, `-journal` companions, operation-owned scratch files, and explicitly named/new backup files participate. No glob deletion, recursive directory removal, source-fixture changes or unrelated file cleanup occurs. The lock and earlier backups are retained by reset.

## Backup

`backup --output PATH` copies the **entire SQLite main database** using `sqlite3.Connection.backup`, not selected rows or a raw copy of an open database file. It therefore includes inventory, original seed metadata, all Stage 2 import envelopes/receipts/raw and typed records/coverage, saved calculation runs and the findings embedded in their JSON. Schema v3's allocation requests, audit events, exceptions and report preset are included when present. Other tables in the same database are also copied; code/assets, files outside SQLite and attached external databases are outside the snapshot. Actual round-trip preservation remains unverified.

The destination parent must already exist. The destination must be new: existing files, directories, symlinks and raced-in names are refused. Naming the active DB, its sidecars or its lock as output is refused. The source is opened read-only; its identity, supported schema, SQLite integrity and foreign keys must validate.

A private mode-0600 temporary database in the output directory receives the SQLite backup. It is normalized to DELETE journal mode, validated, closed and file-synced before publication. A same-directory hard link publishes the final filename without overwriting an existing destination, then the temporary name is removed and the directory is synced. Filesystems that do not support these local operations fail visibly; there is no unsafe copy/overwrite fallback.

The backup callback bounds consecutive SQLite busy/locked retries to three seconds and the copy phase to 30 seconds. These bounds exclude integrity-check time and are illustrative local-demo limits, not performance or availability guarantees.

Success JSON includes `status: backed_up`, `database`, `output`, `output_published`, `schema_version`, `initialized`, and `scope: entire_sqlite_database`. Snapshot creation does not convert synthetic or unknown evidence into live/complete evidence.

## Restore

`restore --input PATH --confirm` accepts a **standalone SQLite snapshot**, not a directory or a database/WAL bundle. Input must have no `-wal`, `-shm` or `-journal` companion. The source is opened read-only, without `immutable=1`; the command does not bypass SQLite recovery rules.

1. Under the existing app-data lock, validate input file safety, identity and schema/integrity/foreign keys. A same-directory temporary candidate is populated via the SQLite backup API and independently validated as a standalone database. This occurs before any work on the existing database.
2. If a current database exists, it too must be a recognized, supported, valid application database. Preserve its full logical state as a new standalone snapshot named `ipam_demo.before-restore-<UTC timestamp>-<UUID>.sqlite3` inside the data directory. File and directory synchronization precede replacement. This preserved database remains after both success and later failure.
3. Ask SQLite to checkpoint existing WAL and switch the current database to DELETE journal mode. Close the connection before filesystem replacement. Refuse unsafe or remaining nonempty sidecars; never throw away nonempty WAL or recovery journals to force progress. Empty remnants may be removed. A read-only source that requires journal recovery may fail before this step; no automatic recovery of an unrecognized/corrupt store is attempted.
4. Atomically replace the current main file with the already validated candidate. If there was no existing database, publish without clobbering a raced-in name; orphan sidecars prevent this fresh-store path. Remove the temporary name and sync the final directory change before reporting success.

Failed input validation, snapshot creation or final replacement leaves the original logical data available; the existing main file stays in place until the final replacement. SQLite may normalize its journal representation without changing its logical contents. The preserved snapshot is the recovery reference and is never deleted automatically. No destructive pre-delete or move-away of the current main file is used.

Success JSON includes `status: restored`, `database`, `input`, `database_replaced`, `preserved_database` (null only when no previous DB existed), `schema_version`, `initialized` and `migration_required`. A post-publication scratch-cleanup or directory-sync failure is an error that explicitly records whether the new database was installed and where the original was retained; it is not reported as a clean success. Retrying destructive operations blindly is unnecessary—inspect those fields first.

## Reset

`reset --confirm` removes the recognized application database; it **does not reseed**. Existing app identity, supported schema, integrity and foreign keys must validate before removal. Missing, corrupt, unsupported, linked or otherwise unrecognized databases are refused rather than treated as a successful reset.

SQLite first checkpoints and leaves WAL mode as above. Exact removable empty sidecars are removed before the main file; the main file is removed last, then the directory is synced. A sidecar failure leaves the main database in place and returns the removal progress. A later directory-sync failure reports `database_removed: true` and does not claim clean success. Nonempty recovery files are preserved and reported. Other files in the data directory, preserved pre-restore databases, backup files and the lock file remain untouched.

Success JSON includes `status: reset`, `database`, `database_removed`, `removed_paths`, `previous_schema_version` and `next_step`. SQLite itself may retire sidecars while normalizing its journal; `removed_paths` lists explicit filesystem removals by this command. After reset, explicitly seed or restore before expecting initialized readiness. Starting the service alone creates only the existing unseeded schema behavior.

## Schema and file safety

Application identity and required tables come from shared `require_schema`. State validation uses the store owner's `MIGRATABLE_SCHEMA_VERSIONS` (currently v1 and v2) and `SCHEMA_VERSION` (currently v3). A declared legacy version is checked with `require_schema(version=that_version)`; current and all other inputs go through the current-version check, so unknown versions are refused. There is no separate historical-version list or table policy in state operations.

This applies to backup sources, restore inputs/candidates, existing databases preserved before restore, and reset targets. A restored v1/v2 database keeps its original version and returns `migration_required: true`; stop the service and use the existing explicit `python -m ipam_demo migrate` before normal current-runtime use. Current-v3 restore returns `migration_required: false`. State operations never advance a schema themselves, and normal startup remains restricted to the current schema. An uninitialized but structurally valid database stays uninitialized after backup/restore.

Validation includes `PRAGMA integrity_check` and `PRAGMA foreign_key_check`, beyond identity/version checks. These establish SQLite structural consistency when actually executed; they do not recalculate saved findings or revalidate every domain-level JSON assertion. Future schemas must keep shared helpers authoritative and coordinate any concrete compatibility change with the state-command owner.

Main/input/sidecar/lock files must be regular files with a single hard link; final symlinks are refused. External path parents are resolved, so a symlink cannot conceal the final file being overwritten. Destination publication is no-clobber. File identity/content stamps detect some changes outside the app lock; the operating contract still requires exclusive access and does not defend against a hostile process racing file replacements in a writable data directory.

## Errors, retained artifacts and remaining evidence

Errors follow the existing CLI envelope and nonzero exit behavior. `error.details` records `operation` and known progress: `output_published` for backup; `database_replaced` and `preserved_database` for restore; `database_removed` and `removed_paths` for reset. Filesystem/SQLite exceptions do not become successful no-ops. `STATE_CLEANUP_FAILED` lists exact retained scratch paths; candidate validation/normalization failures and unsafe input paths remain explicit.

Typical refusal codes are `CONFIRMATION_REQUIRED`, `DATA_IN_USE`, `STATE_FILE_MISSING`, `UNSAFE_STATE_FILE`, `OUTPUT_EXISTS`, `UNSAFE_INPUT`, `UNSAFE_OUTPUT`, `UNRECOGNIZED_DATABASE`, `UNSUPPORTED_SCHEMA`, `DATABASE_INTEGRITY_FAILED`, `SNAPSHOT_NOT_STANDALONE`, `STATE_RECOVERY_REQUIRED`, `STATE_CHANGED`, `STORE_BUSY`, and `STATE_OPERATION_TIMEOUT`. Inspect the error message and progress fields before retrying. Never remove sidecars or the lock as a workaround for a reported busy/recovery condition.

An interruption can leave an operation-owned temporary file or a completed preserved snapshot. No startup cleanup scans or deletes those artifacts. This is a one-process local state interface, not a crash/power-loss recovery framework; crash consistency, directory/file-sync behavior and platform portability are unverified.

Pending evidence includes complete v2/v3 snapshot round-trip and saved-ID/content preservation (including populated v3 workflow/audit/exception/preset tables); invalid/foreign/unsupported/corrupt input refusal; original preservation on copy/replace/permission failures; active-service refusal; WAL/rollback-journal behavior; reset scope; replay of backup/restore/reset failures; v1/v2 restore then explicit migration; replacement of an existing v2 target with a v3 snapshot while retaining its original; and untouched unrelated files. No tests were added, and no state command, application install, migration, build, smoke/browser check or infrastructure operation was executed here. Schema table availability alone does not establish populated Part 5 allocation/audit persistence evidence.

Implementation references: [Python's backup API](https://docs.python.org/3.12/library/sqlite3.html#sqlite3.Connection.backup), [SQLite backup design](https://www.sqlite.org/backup.html), [SQLite URI semantics](https://www.sqlite.org/uri.html), and [SQLite temporary/journal files](https://www.sqlite.org/tempfiles.html). These inform source design; they are not runtime evidence for this implementation.
