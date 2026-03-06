"""
Database layer — SQLite (local-first, aiosqlite)
Schema: sessions, agents, vtuber_sessions, dna_profiles, api_keys, audit_log
"""

import os
import aiosqlite

SQLITE_PATH = os.getenv("SQLITE_PATH", "/app/data/mist.db")


async def init_db():
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
    async with aiosqlite.connect(SQLITE_PATH) as db:
        with open("sql/schema.sql") as f:
            await db.executescript(f.read())
        await db.commit()


async def get_db():
    async with aiosqlite.connect(SQLITE_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db
