import sqlite3
import os
import json
import time
from pathlib import Path
from datetime import datetime

DB_PATH = Path("c:/Users/nator/clawd/art_curator/art_curator.db")

class CuratorAgent:
    def __init__(self):
        self.db_path = DB_PATH
        self.output_dir = self.db_path.parent / "curated_output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_conn(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        conn = self.get_conn()
        c = conn.cursor()
        
        # Art Pieces / Content
        c.execute('''CREATE TABLE IF NOT EXISTS art_pieces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            tags TEXT,
            file_path TEXT,
            content TEXT,
            source TEXT DEFAULT 'mist',
            status TEXT DEFAULT 'draft',
            created_at INTEGER
        )''')

        # Scheduled Posts
        c.execute('''CREATE TABLE IF NOT EXISTS scheduled_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            art_piece_id INTEGER,
            platform TEXT NOT NULL,
            caption TEXT,
            scheduled_at INTEGER,
            status TEXT DEFAULT 'scheduled',
            posted_at INTEGER,
            FOREIGN KEY(art_piece_id) REFERENCES art_pieces(id)
        )''')
        
        # Social Config
        c.execute('''CREATE TABLE IF NOT EXISTS social_config (
            platform TEXT PRIMARY KEY,
            credentials TEXT
        )''')

        conn.commit()
        conn.close()

    def add_art_piece(self, title, file_path=None, description="", tags="", content="", source="mist"):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("INSERT INTO art_pieces (title, description, tags, file_path, content, source, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (title, description, tags, file_path, content, source, 'draft', int(time.time())))
        pid = c.lastrowid
        conn.commit()
        conn.close()
        return pid

    def list_art(self, status=None):
        conn = self.get_conn()
        c = conn.cursor()
        if status:
            c.execute("SELECT id, title, description, content, status FROM art_pieces WHERE status=?", (status,))
        else:
            c.execute("SELECT id, title, description, content, status FROM art_pieces")
        rows = c.fetchall()
        conn.close()
        return [{"id": r[0], "title": r[1], "description": r[2], "content": r[3], "status": r[4]} for r in rows]

    def schedule_post(self, art_id, platform, caption, delay_minutes=0):
        # Determine schedule time
        scheduled_at = int(time.time()) + (delay_minutes * 60)
        
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("INSERT INTO scheduled_posts (art_piece_id, platform, caption, scheduled_at, status) VALUES (?, ?, ?, ?, ?)",
                  (art_id, platform, caption, scheduled_at, 'scheduled'))
        # Update original piece status
        c.execute("UPDATE art_pieces SET status='scheduled' WHERE id=?", (art_id,))
        sid = c.lastrowid
        conn.commit()
        conn.close()
        return sid

    def void_art(self, art_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("UPDATE art_pieces SET status='voided' WHERE id=?", (art_id,))
        conn.commit()
        conn.close()
        return True

    def get_queue(self):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''SELECT s.id, a.title, s.platform, s.scheduled_at, s.status 
                     FROM scheduled_posts s 
                     JOIN art_pieces a ON s.art_piece_id = a.id 
                     ORDER BY s.scheduled_at ASC''')
        rows = c.fetchall()
        conn.close()
        return [{"id": r[0], "title": r[1], "platform": r[2], "time": datetime.fromtimestamp(r[3]).strftime('%Y-%m-%d %H:%M:%S'), "status": r[4]} for r in rows]

    async def start_loop(self, gateway):
        import asyncio
        print("Curator Automation Loop Started.")
        while True:
            await asyncio.sleep(60)
            self._check_schedule(gateway)

    def _check_schedule(self, gateway):
        try:
            now = int(time.time())
            conn = self.get_conn()
            c = conn.cursor()
            c.execute("SELECT id, platform, caption, art_piece_id FROM scheduled_posts WHERE status='scheduled' AND scheduled_at <= ?", (now,))
            posts = c.fetchall()
            
            for p in posts:
                pid, plat, cap, aid = p
                # publish
                if self.publish_post(pid, plat, cap, aid):
                    c.execute("UPDATE scheduled_posts SET status='published', posted_at=? WHERE id=?", (now, pid))
                    if gateway:
                         # We can't await here easily if called from sync, but we passed gateway.
                         # Ideally run_loop is async.
                         pass 
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Curator Loop Error: {e}")

    def publish_post(self, pid, platform, caption, art_id):
        # MOCK X PUBLISHER
        print(f"[{platform.upper()}] 𝕏 SIGNAL BROADCASTING...")
        print(f"[{platform.upper()}] CONTENT: {caption}")
        time.sleep(2)
        print(f"[{platform.upper()}] SUCCESS: Post {pid} is live on X.")
        return True

if __name__ == "__main__":
    agent = CuratorAgent()
    print("Curator Initialized.")
    # Test
    # pid = agent.add_art_piece("Test Piece", "C:/test.jpg")
    # agent.schedule_post(pid, "twitter", "Check this out!", 120)
    # print(agent.get_queue())
