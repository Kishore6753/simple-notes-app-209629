#!/usr/bin/env python3
"""Initialize SQLite database for the simple notes app (database container).

This script is intended to be safe to run repeatedly (idempotent):
- It ensures existing unrelated tables are left untouched.
- It creates the required `notes` table if it does not exist.
- It inserts minimal seed data only when the `notes` table is newly created.

IMPORTANT:
- We use the confirmed database file path under this container:
  `/home/kavia/workspace/code-generation/simple-notes-app-209629/database/myapp.db`
  (as referenced by db_connection.txt and sqlite.env for the DB visualizer).
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone

# Confirmed DB file location for this workspace/container.
DB_PATH = "/home/kavia/workspace/code-generation/simple-notes-app-209629/database/myapp.db"

print("Starting SQLite setup...")

# Ensure parent directory exists (should already exist, but safe).
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

db_exists = os.path.exists(DB_PATH)
if db_exists:
    print(f"SQLite database already exists at {DB_PATH}")
else:
    print(f"Creating new SQLite database at {DB_PATH}...")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create initial schema (existing/unrelated tables preserved and not modified)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS app_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        value TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""
)

# Insert initial data (idempotent via INSERT OR REPLACE)
cursor.execute(
    "INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)",
    ("project_name", "database"),
)
cursor.execute(
    "INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)",
    ("version", "0.1.0"),
)
cursor.execute(
    "INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)",
    ("author", "John Doe"),
)
cursor.execute(
    "INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)",
    ("description", ""),
)

# --- Notes schema (REQUIRED) ---
# Idempotent creation; seed only if we actually created the table.
cursor.execute(
    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='notes' LIMIT 1"
)
notes_table_exists = cursor.fetchone() is not None

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,   -- ISO 8601 string
        updated_at TEXT NOT NULL    -- ISO 8601 string
    )
"""
)

# Seed data only when table is created for the first time.
if not notes_table_exists:
    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        """
        INSERT INTO notes (title, content, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        """,
        ("Welcome", "This is your first note. Edit or delete it anytime.", now_iso, now_iso),
    )
    print("Seeded initial note into newly created `notes` table.")

conn.commit()

# Stats
cursor.execute(
    "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
)
table_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM app_info")
app_info_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM notes")
notes_count = cursor.fetchone()[0]

conn.close()

# Save connection information to a file within this container directory
connection_string = f"sqlite:///{DB_PATH}"

try:
    with open("db_connection.txt", "w") as f:
        f.write("# SQLite connection methods:\n")
        f.write(f"# Python: sqlite3.connect('{DB_PATH}')\n")
        f.write(f"# Connection string: {connection_string}\n")
        f.write(f"# File path: {DB_PATH}\n")
    print("Connection information saved to db_connection.txt")
except Exception as e:
    print(f"Warning: Could not save connection info: {e}")

# Create environment variables file for Node.js viewer (used by db_visualizer)
try:
    with open("db_visualizer/sqlite.env", "w") as f:
        f.write(f'export SQLITE_DB="{DB_PATH}"\n')
    print("Environment variables saved to db_visualizer/sqlite.env")
except Exception as e:
    print(f"Warning: Could not save environment variables: {e}")

print("\nSQLite setup complete!")
print(f"Database: {os.path.basename(DB_PATH)}")
print(f"Location: {DB_PATH}\n")

print("Database statistics:")
print(f"  Tables: {table_count}")
print(f"  App info records: {app_info_count}")
print(f"  Notes: {notes_count}")

print("\nScript completed successfully.")
