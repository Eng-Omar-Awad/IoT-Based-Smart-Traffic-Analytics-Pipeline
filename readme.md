🚦 IoT-Based Smart Traffic Analytics Pipeline

End-to-End Data Engineering Project simulating IoT traffic sensors, building batch + streaming pipelines, and visualizing real-time insights on a dashboard.

📌 Project Overview

Modern cities depend on IoT traffic sensors to monitor roads, detect congestion, and ensure road safety.
In this project, we simulate such a system by:

Generating realistic traffic data (vehicle ID, speed, location, timestamp).

Processing it in batch pipelines for historical insights.

Streaming it in real-time pipelines for alerts.

Visualizing insights on a dashboard for monitoring.

This project demonstrates core data engineering skills:
✅ Data Simulation
✅ ETL (Extract, Transform, Load)
✅ Streaming Analytics
✅ Cloud Integration (Azure, Kafka)
✅ Real-Time Dashboards

🎯 Objectives

Simulate IoT Traffic Data – Python script generates live traffic events.

Batch Data Pipeline (ETL) – Clean, transform & load into SQL/Data Lake.

Streaming Analytics – Real-time alerts for overspeeding, congestion, accidents.

Dashboard & Reporting – Visualize live metrics, summarize findings.

🛠️ Tech Stack
Layer	Tools & Technologies
Data Simulation	Python (random, faker)
Batch Processing	Pandas, SQL, Azure Data Factory (optional)
Streaming	Azure Stream Analytics / Apache Kafka
Storage	CSV, SQLite (local), Azure SQL / Data Lake
Visualization	Power BI / Streamlit / Grafana
Big Data (Optional)	Spark, Hadoop
DevOps (Optional)	Airflow, CI/CD
📂 Project Structure
📦 smart-traffic-analytics
 ┣ 📜 README.md
 ┣ 📜 traffic_simulator.py      # Data generator (IoT traffic)
 ┣ 📜 traffic_data.csv          # Raw sensor logs
 ┣ 📜 traffic_etl.py            # Batch ETL pipeline
 ┣ 📜 processed_data.csv        # Cleaned data output
 ┣ 📜 streaming_pipeline/       # Real-time stream processing setup
 ┣ 📜 dashboard/                # Dashboard code (Power BI / Streamlit)
 ┣ 📜 report/                   # Final PDF Report

🚀 Milestones
Milestone 1: Data Simulation

✅ Python script simulates traffic data:

vehicle_id, speed, location, timestamp.

✅ Data saved into traffic_data.csv.

Sample Log:

V605,133,Downtown,2025-09-03 06:12:38
V744,56,Highway A1,2025-09-03 06:12:43

Milestone 2: Batch ETL Pipeline

✅ Extract raw CSV into Pandas.

✅ Transform:

Flag overspeeding vehicles (>120 km/h).

Compute average speeds per location.

Handle missing/duplicate records.

✅ Load: Store into SQLite / Azure SQL.

Milestone 3: Streaming Analytics

✅ Send real-time events to Azure Event Hub / Kafka.

✅ Process streams with Azure Stream Analytics.

✅ Generate alerts for:

Overspeeding.

Sudden congestion (avg speed drop).

Accidents (vehicles stuck at 0 km/h).

Milestone 4: Dashboard & Reporting

✅ Dashboard in Power BI / Streamlit / Grafana.

✅ Real-time monitoring:

Vehicle speeds per road.

Alerts for violations.

Rush-hour trends.

✅ Final report summarizing:

Architecture.

Insights.

Performance.

📊 System Architecture
       ┌─────────────┐
       │ Data Source │  (Python IoT Generator)
       └──────┬──────┘
              │
              ▼
     ┌───────────────┐
     │   Batch ETL   │ (Pandas, SQL)
     └───────────────┘
              │
              ▼
     ┌───────────────┐
     │   Data Lake   │ (Azure SQL / Storage)
     └───────────────┘
              │
              ▼
     ┌───────────────┐
     │  Streaming    │ (Kafka / Azure Stream Analytics)
     └───────────────┘
              │
              ▼
     ┌───────────────┐
     │  Dashboard    │ (Power BI / Streamlit)
     └───────────────┘

📸 Screenshots (to add later)

✅ Console logs of data simulation.

✅ Sample CSV raw data.

✅ Processed ETL dataset.

✅ Real-time dashboard view.

🏆 Final Deliverables

Python scripts (traffic_simulator.py, traffic_etl.py).

Data files (traffic_data.csv, processed_data.csv).

Streaming pipeline config (Azure/Kafka).

Dashboard (Power BI / Streamlit).

Final Report (PDF) documenting:

Pipeline architecture.

Key insights.

System performance.

👥 Team Roles
Role	Member Responsibility
Data Simulation Lead	Write traffic generator scripts
Batch ETL Engineer	Pandas + SQL pipelines
Streaming Engineer	Azure Stream Analytics / Kafka
Cloud Architect	Azure setup (Event Hub, SQL, Data Lake)
Dashboard Developer	Build Power BI / Streamlit dashboards
Project Manager	Report writing, integration, presentation
🌟 Key Learnings

How IoT data is generated and ingested.

Building ETL pipelines for batch analytics.

Streaming pipelines for real-time event processing.

Cloud-native data engineering with Azure / Kafka.

Building professional dashboards for insights.

📜 License

This project is for educational purposes as part of a Data Engineering course.