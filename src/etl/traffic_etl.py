"""
traffic_etl.py
---------------
Batch ETL pipeline for Smart Traffic Analytics.
Reads raw IoT traffic data from database, applies transformations,
and loads results into a processed table for analysis.

"""

import sqlite3
import pandas as pd


# Step 1: Connect to Database

DB_PATH = r"C:\Users\AL_Qadisiyah\Documents\traffic.db" 
conn = sqlite3.connect(DB_PATH)

print("✅ Connected to database:", DB_PATH)


# Step 2: Extract - Load Raw Data

query = "SELECT * FROM traffic_data"
df = pd.read_sql_query(query, conn)

print(f"📥 Extracted {len(df)} rows from traffic_data")


# Step 3: Transform


# Ensure timestamp is datetime
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# Drop duplicates and handle missing values
df = df.drop_duplicates().dropna()

# Add overspeeding flag
df["overspeeding"] = df["speed"] > 120

# Extract hour for rush-hour analysis
df["hour"] = df["timestamp"].dt.hour

# Optional: rush-hour flag (7-9 AM, 5-7 PM)
df["rush_hour"] = df["hour"].between(7, 9) | df["hour"].between(17, 19)

# Compute average speed per location (summary table)
avg_speed = (
    df.groupby("location")["speed"]
    .mean()
    .reset_index()
    .rename(columns={"speed": "avg_speed"})
)

print("📊 Average speeds per location:")
print(avg_speed)


# Step 4: Load - Save Processed Data

df.to_sql("processed_traffic", conn, if_exists="replace", index=False)

print("✅ Processed data saved to 'processed_traffic' table")

# Save summary averages into a separate table
avg_speed.to_sql("traffic_summary", conn, if_exists="replace", index=False)

print("✅ Summary stats saved to 'traffic_summary' table")


# Done

conn.close()
print("🏁 ETL job completed successfully!")
