-- Core inventory schema. Later changes use explicit shared-schema migrations.
CREATE TABLE app_meta (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    initialized INTEGER NOT NULL DEFAULT 0 CHECK (initialized IN (0, 1)),
    baseline_version INTEGER NOT NULL DEFAULT 0,
    scenario TEXT,
    demo_clock_at TEXT,
    seeded_at TEXT,
    seed_envelope TEXT
);
INSERT INTO app_meta(singleton) VALUES (1);

CREATE TABLE scopes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    namespace TEXT NOT NULL UNIQUE,
    domain TEXT NOT NULL,
    region TEXT NOT NULL,
    managed_cidrs TEXT NOT NULL
);
CREATE TABLE prefixes (
    id TEXT PRIMARY KEY,
    scope_id TEXT NOT NULL REFERENCES scopes(id),
    family INTEGER NOT NULL CHECK (family IN (4, 6)),
    cidr TEXT NOT NULL,
    network_hex TEXT NOT NULL,
    prefix_length INTEGER NOT NULL,
    parent_id TEXT,
    owner TEXT NOT NULL,
    purpose TEXT NOT NULL,
    tags TEXT NOT NULL,
    custom_fields TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    origin TEXT NOT NULL,
    UNIQUE(scope_id, family, cidr),
    UNIQUE(id, scope_id, family),
    FOREIGN KEY(parent_id, scope_id, family) REFERENCES prefixes(id, scope_id, family)
);
CREATE INDEX prefixes_order ON prefixes(scope_id, family, network_hex, prefix_length, id);
CREATE TABLE pools (
    id TEXT PRIMARY KEY,
    scope_id TEXT NOT NULL,
    prefix_id TEXT NOT NULL,
    family INTEGER NOT NULL CHECK (family IN (4, 6)),
    name TEXT NOT NULL,
    management_mode TEXT NOT NULL CHECK (management_mode IN ('dhcp', 'static')),
    allocation_authority TEXT NOT NULL CHECK (allocation_authority IN ('local', 'external')),
    ranges TEXT NOT NULL,
    exclusions TEXT NOT NULL,
    pool_version INTEGER NOT NULL CHECK (pool_version > 0),
    origin TEXT NOT NULL,
    UNIQUE(id, prefix_id, scope_id, family),
    FOREIGN KEY(prefix_id, scope_id, family) REFERENCES prefixes(id, scope_id, family)
);
CREATE TABLE allocations (
    id TEXT PRIMARY KEY,
    scope_id TEXT NOT NULL,
    prefix_id TEXT NOT NULL,
    pool_id TEXT,
    family INTEGER NOT NULL CHECK (family IN (4, 6)),
    address TEXT NOT NULL,
    address_hex TEXT NOT NULL,
    owner TEXT NOT NULL,
    purpose TEXT NOT NULL,
    origin TEXT NOT NULL,
    UNIQUE(scope_id, family, address),
    FOREIGN KEY(prefix_id, scope_id, family) REFERENCES prefixes(id, scope_id, family),
    FOREIGN KEY(pool_id, prefix_id, scope_id, family) REFERENCES pools(id, prefix_id, scope_id, family)
);
