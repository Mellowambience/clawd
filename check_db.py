import sqlite3
conn = sqlite3.connect('c:/Users/nator/clawd/art_curator/art_curator.db')
c = conn.cursor()
c.execute("SELECT * FROM art_pieces")
print(c.fetchall())
conn.close()
