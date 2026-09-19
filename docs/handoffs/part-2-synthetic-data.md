# Parallel pickup: synthetic data

The user requested a separate implementation chat for this lane while Stage 1 continues. The original **Build synthetic inventory demo** chat remains project lead. The initial data subagent stopped before writing files; do not run it alongside the new owner.

## Exact pickup state

- Repo: `https://github.com/yugant99/IpManagement`.
- Prepared local worktree: `/Users/yuganthareshsoni/Downloads/Ip_inventory-synthetic-data`.
- Existing branch: `codex/part-2-synthetic-data`; at preparation, clean at `d157f2c1d63f4797f50b0db166afafd02c6eff97`, with no data commits or published feature branch yet. Refresh Git before editing and retain later work.
- Read this updated handoff on current `main`; incorporate the published oversight documentation into the feature branch before implementation. Do not recreate its worktree or switch the canonical lead checkout.
- Own `fixtures/` (including README), `docs/SYNTHETIC_DATA.md`, and this handoff. No backend, frontend, lock, schema, global-status or packaging edits.
- Stage 1 owns its minimal packaged baseline and loader. The richer pack is a standalone artifact for later import/rule integration, not an already connected feature.

## Required inputs

Read `AGENTS.md`, `DEVELOPMENT_RULES.md`, `docs/PROJECT_OVERSIGHT.md`, `docs/parts/02-sources.md`, `docs/parts/03-reconciliation.md`, relevant `IMPLEMENTATION_DECISIONS.md` sections and `CONTRACTS.md`. Use the existing decisions; do not restart grilling or install skills for ordinary JSON work.

Stage 1 concrete shape is in its worker's `docs/FOUNDATION_API.md`. During parallel work, read `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-1/docs/FOUNDATION_API.md` and the seed lane's `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-1-seed/backend/ipam_demo/data/baseline.json`. Once published, record exact branch/SHA dependency instead of relying on local paths. Preserve those baseline rows/UUIDs when extending the inventory.

The minimal seed uses source `synthetic-baseline`, run `baseline-v1`, and fixed clock **2026-09-01T00:00:00.000Z**. It contains North and Lab scopes, six prefixes, two North pools and intended allocation `10.40.2.2`. Use a distinct source/run for richer content so changed envelopes cannot masquerade as an identical batch replay.

## Deliverable

- A small deterministic Python standard-library generator and the actual generated versioned JSON files; no dependency installation or service required. Running it to create the requested data is authorized artifact generation, not an application acceptance check.
- Extend the seed shape to four fictional scopes (North, Coastal, Central, Lab), about 60 prefixes, eight pools, 2,000 DHCP lease intervals and 200 routing observations over 30 days. Prefer meaningful evidence to padding record counts; document actual counts and any deviation.
- Include healthy data, all six Pool Watch conditions, actual assignment conflict, legitimate cross-scope reuse, sequential renewals, missing metadata, and incomplete/stale/invalid-source scenarios. Use independent managed perimeters, explicit scope and UTC half-open validity intervals, deterministic IDs and provenance.
- Keep invalid/partial variants in separate opt-in batches so they do not invalidate every healthy scenario. Preserve raw rejected values and document reasons expected from the eventual importer.
- Include enough occupancy history for the agreed hourly p95 and daily trend calculations. Use the existing 80% / 60-day pressure and 50% oversized definitions; missing evidence stays unknown. Inactivity is a candidate, never proof that reclaim is safe.
- Keep a separate expected-outcome manifest for later comparison. Expected labels must never be inputs to detection or hardcoded dashboard answers.
- Document a concrete source envelope, field meanings, source/scope/run IDs, clock/window, regeneration command, scenario-to-file map, and importer/seed integration instructions. Distinguish existing seed shape from the proposed Stage 2 observation schema. Do not pretend the importer/rules already consume these files.

## Completion and permissions

Implement and generate the artifacts; do not add/run tests, smoke checks, application builds or a new validation pipeline. No VM/container/database/cloud/customer access is needed. Keep all data fictional and public-repository safe.

Commit each coherent change, push after three or earlier for handoff, and open a focused PR. Report **READY FOR PROJECT-LEAD REVIEW — Synthetic data** with exact pushed SHA/PR, files/counts, schema dependencies, limits and next integration step. No independent main merge or global status changes. The lead reviews the dataset contract and coordinates the next owner.
