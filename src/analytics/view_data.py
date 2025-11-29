"""
view_data_hive.py
-----------------
Utility script to inspect Hive tables for Smart Traffic Analytics.
Usage (CLI):
    python view_data_hive.py
    python view_data_hive.py processed_traffic 20
"""

import sys
import os
import sqlite3
import pandas as pd
import argparse
import json

try:
    from pyhive import hive
    HIVE_AVAILABLE = True
except ImportError:
    HIVE_AVAILABLE = False

# Hive config
HIVE_HOST = "localhost"
HIVE_PORT = 10000
HIVE_DB = "smart_traffic"

def view_table(table_name: str, limit: int = 10, require_hive: bool = False):
    """Show a small sample from a table.

    Tries Hive first. If PyHive/Hive is unavailable and `require_hive` is False,
    falls back to local SQLite (`data/traffic.db`), CSV in `Data/raw/`, or JSONL
    fallback `Data/raw/traffic_data_out.jsonl`.
    """
    query = f"SELECT * FROM {table_name} LIMIT {limit}"

    # Try Hive
    if HIVE_AVAILABLE:
        conn = hive.Connection(host=HIVE_HOST, port=HIVE_PORT, username="hive", database=HIVE_DB)
        df = pd.read_sql(query, conn)
        conn.close()
        print(f"\n=== Showing first {limit} records from '{table_name}' (Hive) ===\n")
        print(df.to_string(index=False))
        return

    # If Hive is required, raise
    if require_hive:
        raise ImportError(
            "PyHive not installed or Hive unreachable.\n"
            "Install PyHive and its peer dependencies: `python -m pip install pyhive thrift`\n"
            "Or run this script with `--allow-fallback` to use local SQLite/CSV/JSONL fallbacks."
        )

    # Fallback 1: local SQLite DB
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "traffic.db"))
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        try:
            df = pd.read_sql(query, conn)
            print(f"\n=== Showing first {limit} records from '{table_name}' (SQLite fallback: {db_path}) ===\n")
            print(df.to_string(index=False))
            return
        except Exception:
            # table may not exist in sqlite; continue to next fallback
            pass
        finally:
            conn.close()

    # Fallback 2: CSV in Data/raw/{table_name}.csv
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Data", "raw", f"{table_name}.csv"))
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print(f"\n=== Showing first {limit} records from '{table_name}' (CSV fallback: {csv_path}) ===\n")
        print(df.head(limit).to_string(index=False))
        return

    # Fallback 3: generic JSONL produced by simulator
    jsonl_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Data", "raw", "traffic_data_out.jsonl"))
    if os.path.exists(jsonl_path):
        records = []
        with open(jsonl_path, "r", encoding="utf-8") as fh:
            for line in fh:
                try:
                    records.append(json.loads(line.strip()))
                except Exception:
                    continue
                if len(records) >= limit:
                    break
        if records:
            df = pd.DataFrame(records)
            print(f"\n=== Showing first {limit} records from '{table_name}' (JSONL fallback: {jsonl_path}) ===\n")
            print(df.head(limit).to_string(index=False))
            return

    # Nothing found
    raise ValueError("Could not find table in Hive, SQLite, CSV, or JSONL fallbacks.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="View a table from Hive (default) or local fallbacks")
    parser.add_argument("table", nargs="?", default="processed_traffic", help="Table name to view")
    parser.add_argument("limit", nargs="?", type=int, default=10, help="Number of rows to show")
    parser.add_argument("--allow-fallback", action="store_true", help="Allow SQLite/CSV/JSONL fallbacks if Hive is unavailable")
    args = parser.parse_args()

    # Default behavior: require Hive (no SQLite fallback). Pass --allow-fallback to permit fallbacks.
    require_hive = not args.allow_fallback
    try:
        view_table(args.table, args.limit, require_hive=require_hive)
    except ImportError as e:
        # Print a concise, actionable message and exit with non-zero status
        print(f"ERROR: {e}")
        sys.exit(1)
