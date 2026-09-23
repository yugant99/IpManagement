# T023 stopped recovery source review

Author: Muse 1.3 high in OpenCode, retained session
`ses_f32c9e72dffeg9BzrsFy7Djgbm`, exact paid route
`opencode-go/muse-spark-1.3-contributor#high`. Independent reviewer: GPT-6 Sol high.
Common T018/T023 base: `5c2181c33ad8c841cc0cd0fb5a09b1cf495cbe33`.
Initial full candidate: `f4e8d9a3dcf167f5d0d73cdfccef780b2caf3304`, PR92.
Final source: **`adb2dc18fe747d4ff97a90f1a21bcdc4382f9fea`**.
Source integration: `a711d1ee84ba3d8959f18471bc2acf930c3ce7a5`.

The complete feature retains stopped locking, whole-SQLite copying, recognized
schema policy, no-clobber publication, preserved prior store and atomic replacement.
Backup adds a private deterministic recovery manifest bound to the closed snapshot's
SHA-256, size and schema, with sanitized observed configuration identity or explicit
unavailable fields. Restore strictly validates a present manifest and input identity
before and after SQLite copying. An absent manifest permits unverified data rescue;
known equal, known changed and unavailable configuration remain distinct. Snapshot
contents do not include application code, UI, configuration files or secrets.

Sol's whole-feature source review confirmed manifest parsing, input-byte hash
checks and configuration classification, and returned two blocking findings to
the retained author. Astra independently identified the same failure paths:

1. Manifest publication was reported only after directory fsync, so a failure
   after linking the final name falsely reported `manifest_published=false`.
   The correction records publication immediately after the successful link.
2. Scratch-manifest unlink failure was logged but allowed clean success.
   The correction raises `STATE_CLEANUP_FAILED` with the exact remaining path
   and accurate publication progress, preserving already published files.

Sol independently closed both corrections at the final source above and found
no new source blocker in nearby backup handling. The CLI help now reflects
recognized schemas 1–6 and current schema 7. Restore success or equal configuration
does not establish readiness: all six protected readiness fields, separate selected
domain business-state comparison and actual human signoff remain distinct gates.

Only `state_ops.py` and `__main__.py` changed. No application tests, builds, imports,
typechecks, lint, SQL/database execution, state commands or runtime checks ran.
Partial filesystem failure and recovery behavior remain unverified until T025.
The later user ownership amendment assigns package/operator preparation to agents. T025/T028 and the Tier B lock are unchanged;
this is source acceptance, not portable/human evidence or permission to merge main.
