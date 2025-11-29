"""
view_data_duckdb.py
-------------------
Utility script to inspect DuckDB tables for Smart Traffic Analytics.
Usage (CLI):
    python view_data_duckdb.py
    python view_data_duckdb.py processed_traffic 20
"""

import sys
import os
import pandas as pd
import argparse
import json

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False

# DuckDB config

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "traffic.duckdb"))

FALLBACK_JSONL = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Data", "raw", "traffic_data_out.jsonl"))

def view_table(table_name: str, limit: int = 10, require_duckdb: bool = False):
    """Show a small sample from a DuckDB table or fallback JSONL."""
    query = f"SELECT * FROM {table_name} LIMIT {limit}"

    # Try DuckDB

    if DUCKDB_AVAILABLE and os.path.exists(DB_PATH):
        conn = duckdb.connect(DB_PATH)
        try:
            df = conn.execute(query).fetchdf()
            print(f"\n=== Showing first {limit} records from '{table_name}' (DuckDB) ===\n")
            print(df.to_string(index=False))
            return
        except Exception:
            pass
        finally:
            conn.close()

    # If DuckDB is required but unavailable

    if require_duckdb:
        raise ImportError(f"DuckDB not installed or {DB_PATH} unreachable. Install duckdb or use --allow-fallback.")

    # Fallback: JSONL

    if os.path.exists(FALLBACK_JSONL):
        records = []
        with open(FALLBACK_JSONL, "r", encoding="utf-8") as fh:
            for line in fh:
                try:
                    records.append(json.loads(line.strip()))
                except Exception:
                    continue
                if len(records) >= limit:
                    break
        if records:
            df = pd.DataFrame(records)
            print(f"\n=== Showing first {limit} records from '{table_name}' (JSONL fallback) ===\n")
            print(df.head(limit).to_string(index=False))
            return

    # Nothing found
    raise ValueError("Could not find table in DuckDB or JSONL fallback.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="View a table from DuckDB or JSONL fallback")
    parser.add_argument("table", nargs="?", default="processed_traffic", help="Table name to view")
    parser.add_argument("limit", nargs="?", type=int, default=10, help="Number of rows to show")
    parser.add_argument("--allow-fallback", action="store_true", help="Allow JSONL fallback if DuckDB is unavailable")
    args = parser.parse_args()

    require_duckdb = not args.allow_fallback
    try:
        view_table(args.table, args.limit, require_duckdb=require_duckdb)
    except ImportError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)





