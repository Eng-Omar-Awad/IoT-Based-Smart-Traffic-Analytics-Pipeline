🚦 IoT-Based Smart Traffic Analytics Pipeline

End-to-End Data Engineering Project simulating IoT traffic sensors, building batch + streaming pipelines, and visualizing real-time insights on a dashboard — with direct database integration.

📌 Project Overview

Modern smart cities rely on IoT traffic sensors to monitor vehicles, detect congestion, and improve road safety.
This project simulates such a system by:

Generating realistic traffic data (vehicle ID, speed, location, timestamp).

Ingesting data directly into a database instead of flat files.

Processing it in batch ETL pipelines for historical insights.

Streaming it in real-time pipelines for live alerts.

Visualizing insights on a dashboard for monitoring.

This project demonstrates core data engineering skills:
✅ IoT Data Simulation
✅ Database Ingestion (SQLite → Azure SQL / Data Lake)
✅ Batch ETL with Pandas & SQL
✅ Streaming Analytics with Kafka / Azure Stream Analytics
✅ Real-Time Dashboards

🎯 Objectives

Simulate IoT Traffic Data – Python script generates live traffic events into a database.

Batch Data Pipeline (ETL) – Clean, transform & load processed data into a new table.

Streaming Analytics – Real-time alerts for overspeeding, congestion, and accidents.

Dashboard & Reporting – Visualize metrics and summarize findings.

🛠️ Tech Stack
Layer Tools & Technologies
Data Simulation Python (random, faker)
Database SQLite (local), Azure SQL Database
Batch Processing Pandas, SQL queries
Streaming Azure Stream Analytics / Apache Kafka
Storage SQL Database, Azure Data Lake
Visualization Power BI / Streamlit / Grafana
Big Data (Optional) Spark, Hadoop
Orchestration (Optional) Airflow
📂 Project Structure
📦 smart-traffic-analytics
┣ 📜 README.md
┣ 📜 traffic_simulator.py # Data generator → Database ingestion
┣ 📜 traffic.db # SQLite database (raw traffic data)
┣ 📜 traffic_etl.py # Batch ETL pipeline
┣ 📜 processed_traffic.db # Processed table (after ETL)
┣ 📜 streaming_pipeline/ # Real-time processing setup
┣ 📜 dashboard/ # Dashboard code (Power BI / Streamlit)
┣ 📜 report/ # Final PDF Report

🚀 Milestones
Milestone 1: Data Simulation (Database-First)

✅ Python script simulates traffic data:

vehicle_id, speed, location, timestamp.

✅ Data ingested directly into traffic.db (SQLite).

Sample Record:

V605 | 133 | Downtown | 2025-09-03 06:12:38
V744 | 56 | Highway A1 | 2025-09-03 06:12:43

Milestone 2: Batch ETL Pipeline

✅ Extract: Read raw traffic data from traffic.db.

✅ Transform:

Flag overspeeding vehicles (>120 km/h).

Compute average speeds per location.

Handle duplicates/missing values.

✅ Load: Save processed data into new table (processed_traffic).

Milestone 3: Streaming Analytics

✅ Send real-time events to Azure Event Hub / Kafka.

✅ Process streams with Azure Stream Analytics.

✅ Generate alerts for:

Overspeeding.

Sudden congestion (avg speed drop).

Accidents (vehicles stuck at 0 km/h).

Milestone 4: Dashboard & Reporting

✅ Dashboard (Power BI / Streamlit / Grafana).

✅ Real-time monitoring:

Vehicle speeds per road.

Live alerts.

Rush-hour congestion trends.

✅ Final PDF Report with:

System architecture.

Key insights.

Performance results.

📊 System Architecture
┌─────────────┐
│ Data Source │ (Python IoT Generator → Database)
└──────┬──────┘
│
▼
┌───────────────┐
│ Batch ETL │ (Pandas + SQL)
└───────────────┘
│
▼
┌───────────────┐
│ Processed DB │ (SQLite → Azure SQL / Data Lake)
└───────────────┘
│
▼
┌───────────────┐
│ Streaming │ (Kafka / Azure Stream Analytics)
└───────────────┘
│
▼
┌───────────────┐
│ Dashboard │ (Power BI / Streamlit)
└───────────────┘

📸 Screenshots (to add later)

✅ Console logs of data insertion into DB.

✅ Raw traffic_data table in SQLite.

✅ Processed ETL table with flagged anomalies.

✅ Dashboard with real-time metrics.

🏆 Final Deliverables

Python scripts (traffic_simulator.py, traffic_etl.py).

Databases (traffic.db, processed_traffic.db).

Streaming pipeline config (Azure/Kafka).

Dashboard (Power BI / Streamlit).

Final Report (PDF) documenting:

Pipeline architecture.

Key insights.

System performance.

👥 Team Roles
Role Member Responsibility
Data Simulation Lead Python generator → Database ingestion
Batch ETL Engineer Build ETL logic with Pandas + SQL
Streaming Engineer Kafka / Azure Stream Analytics
Cloud Architect Azure SQL, Event Hub, Data Lake setup
Dashboard Developer Power BI / Streamlit dashboards
Project Manager Integration + final report
🌟 Key Learnings

IoT data ingestion directly into databases.

Batch analytics with Pandas & SQL.

Streaming pipelines for real-time traffic monitoring.

Building dashboards for live insights.

Deploying pipelines to cloud platforms.

📜 License

This project is for educational purposes as part of a Data Engineering course.

## Local Kafka + Hive (developer setup)

If you want to run the pipeline against a local Kafka broker and a HiveServer2 instance (recommended for end-to-end testing), follow these steps.

1. Start Kafka (local broker)

- A ready-to-run Docker Compose for Kafka (Zookeeper + Kafka) is included: `docker-compose.kafka.yml`.
- Start it from the project root:

```powershell
docker compose -f docker-compose.kafka.yml up -d
```

- Kafka broker will be reachable at `localhost:9092`.

2. Start HiveServer2 (options)

- Hive is heavier to run locally. For development you have two practical options: - Use an existing Hive cluster (set `HIVE_HOST`/`HIVE_PORT` in the scripts to point to it). - Run a Hive dev stack in Docker. There are community-maintained Docker Compose projects that spin up Hadoop + Hive + HiveServer2 + metastore (MySQL/Postgres). A reliable example is the `bde2020` Hive images; see: https://github.com/big-data-europe/docker-hive

If you want, I can add an opinionated `docker-compose.hive.yml` (Hadoop + MySQL metastore + HiveServer2) to this repo — it will be heavier but will let you run HiveServer2 locally.

3. Install Python dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

4. Run the ETL and viewer (strict mode — Kafka + Hive required by default)

```powershell
# Run ETL (requires Kafka + Hive unless you pass --allow-fallback)
python .\src\etl\traffic_etl.py

# Inspect processed table using the Hive viewer
python .\src\analytics\view_data.py processed_traffic 10
```

If you prefer fallbacks (JSONL/SQLite) temporarily while bringing up Hive, add `--allow-fallback` to the commands.

If you'd like, I can add a full `docker-compose.hive.yml` and test the end-to-end run locally — say "Yes, add Hive compose" and I'll scaffold it next.
