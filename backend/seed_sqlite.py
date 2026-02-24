"""One-time script to seed sql_genie.db (SQLite) with sample data."""
import sqlite3
from pathlib import Path

DB = Path(__file__).parent / "sql_genie.db"
SQL = Path(__file__).parent.parent / "sample_data_sqlite.sql"

conn = sqlite3.connect(str(DB))
conn.executescript(SQL.read_text())
conn.close()

# Verify
conn = sqlite3.connect(str(DB))
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
customers = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
conn.close()

print(f"Tables:    {[t[0] for t in tables]}")
print(f"Customers: {customers}")
print(f"Orders:    {orders}")
print("Seeding complete.")
