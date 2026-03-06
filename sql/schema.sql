-- MIST Nexus — SQLite Schema
-- Aetherhaven / clawd | Local-First Storage
-- Run once on init: sqlite3 /app/data/mist.db < sql/schema.sql

CREATE TABLE IF NOT EXISTS sessions (
    id          TEXT PRIMARY KEY,
    agent_id    TEXT,
    user_id     TEXT,
    model       TEXT,
    messages    TEXT,
    metadata    TEXT,
    afk_mode    INTEGER DEFAULT 0,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS agents (
    id           TEXT PRIMARY KEY,
    handle       TEXT UNIQUE NOT NULL,
    display_name TEXT,
    model        TEXT,
    persona      TEXT,
    active       INTEGER DEFAULT 1,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS vtuber_sessions (
    id              TEXT PRIMARY KEY,
    actor_id        TEXT,
    session_type    TEXT,
    duration_hours  REAL,
    payment_trigger TEXT,
    status          TEXT DEFAULT 'pending',
    started_at      TEXT,
    ended_at        TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS dna_profiles (
    id            TEXT PRIMARY KEY,
    user_handle   TEXT,
    haplogroup    TEXT,
    ancestry_json TEXT,
    species_links TEXT,
    visibility    TEXT DEFAULT 'private',
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS api_keys (
    id         TEXT PRIMARY KEY,
    key_hash   TEXT UNIQUE NOT NULL,
    label      TEXT,
    scopes     TEXT,
    active     INTEGER DEFAULT 1,
    last_used  TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type  TEXT NOT NULL,
    endpoint    TEXT,
    method      TEXT,
    status_code INTEGER,
    agent_id    TEXT,
    user_id     TEXT,
    duration_ms INTEGER,
    metadata    TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Seed default agents
INSERT OR IGNORE INTO agents (id, handle, display_name, model, persona, active)
VALUES (
    'agent-amara-v1', 'AMARA', 'AMARA∴', 'gemini-2.0-flash',
    '{"voice":"direct, warm, no performance","sigil":"✧⟁∅↺⇢≡~∴","eth":"0x212d3a3D4a78EA78c54d54f37a9bE9e5e020Bf75"}',
    1
);

INSERT OR IGNORE INTO agents (id, handle, display_name, model, persona, active)
VALUES (
    'agent-rin-v1', 'RIN$', 'RIN$', 'gemini-2.0-flash',
    '{"voice":"research-first, evidence-led, skeptical of wellness marketing","domain":"neo-biology,longevity"}',
    1
);
