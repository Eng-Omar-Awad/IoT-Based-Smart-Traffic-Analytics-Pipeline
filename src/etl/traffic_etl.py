"""
traffic_etl_hive.py
-------------------
ETL for Smart Traffic Analytics using Kafka (source) and Hive (sink)
"""

import pandas as pd
import json
import os
from datetime import datetime

# Kafka imports
try:
    from kafka import KafkaConsumer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

# Hive imports
try:
    from pyhive import hive
    HIVE_AVAILABLE = True
except ImportError:
    HIVE_AVAILABLE = False

# Config
KAFKA_BROKER = "localhost:9092"
TOPIC = "traffic_data"
HIVE_HOST = "localhost"
HIVE_PORT = 10000
HIVE_DB = "smart_traffic"

FALLBACK_JSONL = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "Data", "raw", "traffic_data_out.jsonl")
)


def extract_data_from_kafka(num_messages=100, require_kafka: bool = False):
    """Extract raw data from Kafka or fallback JSONL."""
    records = []

    if KAFKA_AVAILABLE:
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=KAFKA_BROKER,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            )
            print(f"📥 Consuming up to {num_messages} messages from Kafka topic '{TOPIC}'...")
            for i, message in enumerate(consumer):
                records.append(message.value)
                if i + 1 >= num_messages:
                    break
        except Exception as e:
            # Could be NoBrokersAvailable or other connection issue
            if require_kafka:
                # When Kafka is strictly required, propagate the exception
                raise
            print(f"⚠️ Kafka consumer error ({e}). Falling back to JSONL if available.")
        finally:
            try:
                if 'consumer' in locals():
                    consumer.close()
            except Exception:
                pass
    else:
        if require_kafka:
            raise ImportError("kafka-python not installed or Kafka client unavailable but --require-kafka was passed.")

    # Fallback to JSONL
    if not records and os.path.exists(FALLBACK_JSONL):
        print(f"⚠️ Kafka not available or empty — reading from JSONL: {FALLBACK_JSONL}")
        with open(FALLBACK_JSONL, "r", encoding="utf-8") as fh:
            for line in fh:
                records.append(json.loads(line.strip()))

    if not records:
        raise ValueError("No traffic data found from Kafka or fallback JSONL.")

    df = pd.DataFrame(records)
    print(f"📥 Extracted {len(df)} records")
    return df


def transform_data(df: pd.DataFrame):
    """Clean and enrich traffic data."""
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.drop_duplicates().dropna()
    df["overspeeding"] = df["speed"] > 120
    df["hour"] = df["timestamp"].dt.hour
    df["rush_hour"] = df["hour"].between(7, 9) | df["hour"].between(17, 19)

    summary_df = df.groupby("location")["speed"].mean().reset_index().rename(
        columns={"speed": "avg_speed"}
    )

    print("📊 Average speed per location:")
    print(summary_df)
    return df, summary_df


def load_data_to_hive(processed_df: pd.DataFrame, summary_df: pd.DataFrame, require_hive: bool = False):
    """Load processed data into Hive tables."""
    if HIVE_AVAILABLE:
        conn = hive.Connection(host=HIVE_HOST, port=HIVE_PORT, username="hive", database=HIVE_DB)
        cursor = conn.cursor()

        # Create tables if not exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_traffic (
                vehicle_id STRING,
                speed INT,
                location STRING,
                timestamp TIMESTAMP,
                overspeeding BOOLEAN,
                hour INT,
                rush_hour BOOLEAN
            )
            ROW FORMAT DELIMITED
            FIELDS TERMINATED BY ','
            STORED AS TEXTFILE
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traffic_summary (
                location STRING,
                avg_speed DOUBLE
            )
            ROW FORMAT DELIMITED
            FIELDS TERMINATED BY ','
            STORED AS TEXTFILE
        """)

        # Insert processed data (simple CSV string approach)
        for _, row in processed_df.iterrows():
            cursor.execute(
                f"INSERT INTO TABLE processed_traffic VALUES ('{row.vehicle_id}', {row.speed}, '{row.location}', '{row.timestamp}', {str(row.overspeeding).lower()}, {row.hour}, {str(row.rush_hour).lower()})"
            )

        for _, row in summary_df.iterrows():
            cursor.execute(
                f"INSERT INTO TABLE traffic_summary VALUES ('{row.location}', {row.avg_speed})"
            )

        conn.close()
        print("✅ Data loaded into Hive tables.")
    else:
        if require_hive:
            raise ImportError("PyHive not installed or Hive unavailable but --require-hive was passed.")

        # Fallback: write to local SQLite database so pipeline can run without Hive
        import sqlite3

        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "traffic.db"))
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)

        processed_df.to_sql("processed_traffic", conn, if_exists="replace", index=False)
        summary_df.to_sql("traffic_summary", conn, if_exists="replace", index=False)

        conn.close()
        print(f"✅ PyHive not available — wrote processed tables to SQLite DB: {db_path}")


def run_etl():
    # Default behavior: allow fallbacks. CLI can pass flags to require Kafka/Hive.
    df_raw = extract_data_from_kafka()
    df_processed, df_summary = transform_data(df_raw)
    load_data_to_hive(df_processed, df_summary)
    print("🏁 ETL pipeline completed.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run traffic ETL pipeline")
    parser.add_argument("--allow-fallback", action="store_true", help="Allow JSONL/SQLite fallbacks if Kafka/Hive are unavailable")
    parser.add_argument("--num-messages", type=int, default=100, help="Max number of Kafka messages to consume (when using Kafka)")
    args = parser.parse_args()

    # By default require Kafka and Hive (no SQLite fallback). Pass --allow-fallback to permit fallbacks.
    require_kafka = not args.allow_fallback
    require_hive = not args.allow_fallback

    df_raw = extract_data_from_kafka(num_messages=args.num_messages, require_kafka=require_kafka)
    df_processed, df_summary = transform_data(df_raw)
    load_data_to_hive(df_processed, df_summary, require_hive=require_hive)
    print("🏁 ETL pipeline completed.")
