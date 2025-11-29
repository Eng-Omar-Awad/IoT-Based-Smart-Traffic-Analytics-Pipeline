"""
view_data.py
-------------
Utility script for inspecting tables inside the traffic SQLite database.
Allows you to view the first N rows of any table.

Usage (CLI):
    python view_data.py
    python view_data.py traffic_data 20
"""

import sqlite3
import os
import sys
import pandas as pd


def view_table(db_path: str, table_name: str, limit: int = 10):
    """View first N rows from a specific SQLite table."""
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"❌ Database not found at: {db_path}")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Check if the table exists
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
        (table_name,)
    )
    exists = cur.fetchone() is not None

    if not exists:
        conn.close()
        raise ValueError(f"❌ Table '{table_name}' does not exist in the database.")

    # Read using pandas for nicer formatting
    df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT {limit}", conn)
    conn.close()

    print(f"\n=== Showing first {limit} records from '{table_name}' ===\n")
    print(df.to_string(index=False))


if __name__ == "__main__":
    # Default values
    DB_PATH = os.path.abspath(os.path.join("data", "traffic.db"))
    TABLE = "traffic_data"
    LIMIT = 10

    # Support CLI parameters → python view_data.py table_name limit
    if len(sys.argv) > 1:
        TABLE = sys.argv[1]
    if len(sys.argv) > 2:
        LIMIT = int(sys.argv[2])

    view_table(DB_PATH, TABLE, LIMIT)
