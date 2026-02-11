# add_admin_column.py
import sqlite3
import os
import sys

# Try usual locations for the DB file
candidates = [
    "ems.db",
    os.path.join("instance", "ems.db"),
    os.path.join(os.path.dirname(__file__), "ems.db"),
]

db_path = None
for p in candidates:
    if p and os.path.exists(p):
        db_path = p
        break

if not db_path:
    print("Could not find ems.db. Looked at:", candidates)
    sys.exit(1)

print("Using database file:", db_path)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check if 'user' table exists
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user';")
if not cur.fetchone():
    print("No table named 'user' found in", db_path)
    conn.close()
    sys.exit(1)

# Get current columns
cur.execute("PRAGMA table_info('user');")
columns = [row[1] for row in cur.fetchall()]
print("Current columns in user table:", columns)

if 'admin_id' in columns:
    print("Column 'admin_id' already exists. Nothing to do.")
else:
    # Add the new column (SQLite supports ADD COLUMN)
    print("Adding column 'admin_id' to user table...")
    cur.execute("ALTER TABLE user ADD COLUMN admin_id INTEGER;")
    conn.commit()
    print("Added column 'admin_id' successfully.")

# Optional: show final columns
cur.execute("PRAGMA table_info('user');")
print("Final columns:", [row[1] for row in cur.fetchall()])

conn.close()
