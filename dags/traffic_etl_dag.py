
"""
Airflow DAG for Smart Traffic Analytics ETL Pipeline
---------------------------------------------------
This DAG performs:
1. Data validation (checks if data file exists and is not empty)
2. ETL processing (calls run_etl from traffic_etl.py)
3. Notification (prints/logs success)
If validation fails, ETL and notification are skipped.
"""

import sys
from datetime import datetime, timedelta
import os
from airflow import DAG  # type: ignore
from airflow.operators.python import PythonOperator, BranchPythonOperator  # type: ignore
from airflow.operators.empty import EmptyOperator  # type: ignore

# Ensure src/etl is in the path for both Airflow and static analysis
sys.path.insert(0, '/workspaces/IoT-Based-Smart-Traffic-Analytics-Pipeline/src/etl')

try:
    from traffic_etl import run_etl  # type: ignore
except ImportError:
    run_etl = None

DATA_PATH = '/workspaces/IoT-Based-Smart-Traffic-Analytics-Pipeline/Data/raw/traffic_data_out.jsonl'

def validate_data():
    """Check if data file exists and is not empty."""
    if os.path.exists(DATA_PATH) and os.path.getsize(DATA_PATH) > 0:
        return 'run_traffic_etl'
    else:
        print(f"Validation failed: {DATA_PATH} missing or empty.")
        return 'validation_failed'

def notify_success():
    print("✅ Airflow ETL pipeline completed successfully!")

def notify_failure():
    print(f"❌ Data validation failed. ETL not run.")
        
        


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'traffic_etl_dag',
    default_args=default_args,
    description='ETL pipeline for traffic data',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 11, 30),
    catchup=False,
    tags=['traffic', 'ETL', 'analytics'],
    doc_md=__doc__,
)

start = EmptyOperator(task_id='start', dag=dag)
validate = BranchPythonOperator(
    task_id='validate_data',
    python_callable=validate_data,
    dag=dag,
)
etl_task = PythonOperator(
    task_id='run_traffic_etl',
    python_callable=run_etl,
    dag=dag,
)
notify = PythonOperator(
    task_id='notify_success',
    python_callable=notify_success,
    dag=dag,
)
validation_failed = PythonOperator(
    task_id='validation_failed',
    python_callable=notify_failure,
    dag=dag,
)
end = EmptyOperator(task_id='end', dag=dag)

start >> validate
validate >> etl_task >> notify >> end
validate >> validation_failed >> end
