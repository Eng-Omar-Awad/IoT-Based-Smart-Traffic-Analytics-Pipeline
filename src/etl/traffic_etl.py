"""
traffic_etl.py
---------------
Modular & Airflow-ready ETL script for Smart Traffic Analytics.

Steps:
1. Extract  → Read raw traffic data from SQLite
2. Transform → Clean, enrich, create summary metrics
3. Load     → Save processed results back into database
"""

import sqlite3
import pandas as pd
import os


def extract_data(db_path: str, table_name: str):
    """Extract raw data from SQLite database."""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at: {db_path}")

    conn = sqlite3.connect(db_path)

    # Check whether the required table exists in the SQLite DB
    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    exists = cur.fetchone() is not None

    if not exists:
        # Attempt to fall back to CSV located in repository: Data/raw/{table_name}.csv
        csv_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "Data", "raw", f"{table_name}.csv")
        )

        if os.path.exists(csv_path):
            print(f"⚠️ Table '{table_name}' not found in DB; loading from CSV: {csv_path}")
            df_csv = pd.read_csv(csv_path)
            # Create the missing table by writing CSV into the DB
            df_csv.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"🔁 Created table '{table_name}' from CSV and wrote to DB")
        else:
            conn.close()
            raise ValueError(
                f"Table '{table_name}' not found in DB and no CSV fallback at: {csv_path}"
            )

    # Read the table now that it exists (either originally or created from CSV)
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()

    print(f"📥 Extracted {len(df)} rows from '{table_name}'")
    return df


def transform_data(df: pd.DataFrame):
    """Transform raw traffic data: cleaning, enrichment, aggregations."""
    
    # Ensure timestamp is datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    
    # Remove duplicates and nulls
    df = df.drop_duplicates().dropna()

    # Add overspeeding flag (over 120 km/h)
    df["overspeeding"] = df["speed"] > 120

    # Extract hour-of-day
    df["hour"] = df["timestamp"].dt.hour

    # Rush-hour flag (7–9 AM and 5–7 PM)
    df["rush_hour"] = df["hour"].between(7, 9) | df["hour"].between(17, 19)

    # Summary: Avg speed per location
    summary_df = (
        df.groupby("location")["speed"]
        .mean()
        .reset_index()
        .rename(columns={"speed": "avg_speed"})
    )

    print("📊 Average speed per location:")
    print(summary_df)

    return df, summary_df


def load_data(db_path: str, processed_df: pd.DataFrame, summary_df: pd.DataFrame):
    """Load processed data back into SQLite tables."""
    conn = sqlite3.connect(db_path)

    processed_df.to_sql("processed_traffic", conn, if_exists="replace", index=False)
    summary_df.to_sql("traffic_summary", conn, if_exists="replace", index=False)

    conn.close()

    print("✅ Loaded processed data into 'processed_traffic'")
    print("✅ Loaded summary data into 'traffic_summary'")


def run_etl(db_path: str):
    """Run full ETL pipeline."""
    print(f"🚀 Starting ETL using database: {db_path}")

    raw_df = extract_data(db_path, table_name="traffic_data")
    processed_df, summary_df = transform_data(raw_df)
    load_data(db_path, processed_df, summary_df)

    print("🏁 ETL pipeline completed successfully!")
    return True


if __name__ == "__main__":
    # Default local execution
    DB_PATH = "data/traffic.db"
    run_etl(DB_PATH)
