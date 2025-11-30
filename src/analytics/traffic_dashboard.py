import streamlit as st
import pandas as pd
import os
import time
import requests
import json
from datetime import datetime
from streamlit_folium import st_folium
import folium
import plotly.express as px

st.set_page_config(page_title="Traffic Analytics Dashboard", layout="wide")
st.title("🚦 IoT-Based Smart Traffic Analytics Dashboard (Airflow-Connected)")
st.caption("Live dashboard with Airflow DAG integration, streaming, and map visualization.")

# Airflow API configuration
AIRFLOW_BASE_URL = "http://localhost:8080/api/v1"
DAG_ID = "traffic_etl_dag"
AIRFLOW_USERNAME = "admin"
AIRFLOW_PASSWORD = "admin"  # Use environment variables in production

# Data file path
data_path = os.path.join(os.path.dirname(__file__), '../../Data/raw/traffic_data_out.jsonl')

# --- Airflow API Helper Functions ---
@st.cache_data(ttl=10)
def get_airflow_dag_status():
    """Fetch the latest DAG run status from Airflow."""
    try:
        url = f"{AIRFLOW_BASE_URL}/dags/{DAG_ID}"
        response = requests.get(url, auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD), timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.warning(f"Could not connect to Airflow API: {e}")
        return None

@st.cache_data(ttl=10)
def get_latest_dag_run():
    """Fetch the latest DAG run details."""
    try:
        url = f"{AIRFLOW_BASE_URL}/dags/{DAG_ID}/dagRuns?limit=1&order_by=-execution_date"
        response = requests.get(url, auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD), timeout=5)
        if response.status_code == 200:
            runs = response.json().get('dag_runs', [])
            return runs[0] if runs else None
        else:
            return None
    except Exception as e:
        st.warning(f"Could not fetch DAG runs: {e}")
        return None

@st.cache_data(ttl=10)
def get_dag_tasks_status():
    """Fetch task status for the latest DAG run."""
    try:
        latest_run = get_latest_dag_run()
        if not latest_run:
            return None
        run_id = latest_run['dag_run_id']
        url = f"{AIRFLOW_BASE_URL}/dags/{DAG_ID}/dagRuns/{run_id}/taskInstances"
        response = requests.get(url, auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD), timeout=5)
        if response.status_code == 200:
            return response.json().get('task_instances', [])
        else:
            return None
    except Exception as e:
        st.warning(f"Could not fetch task status: {e}")
        return None

def trigger_dag_run():
    """Trigger a new DAG run."""
    try:
        url = f"{AIRFLOW_BASE_URL}/dags/{DAG_ID}/dagRuns"
        payload = {"conf": {}}
        response = requests.post(url, json=payload, auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD), timeout=5)
        if response.status_code == 200:
            st.success("DAG run triggered successfully!")
            st.rerun()
        else:
            st.error(f"Failed to trigger DAG: {response.text}")
    except Exception as e:
        st.error(f"Error triggering DAG: {e}")


def load_data():
    if os.path.exists(data_path):
        return pd.read_json(data_path, lines=True)
    return pd.DataFrame()

# --- Airflow Status Panel ---
st.sidebar.header("🔄 Airflow Control & Status")
col1, col2 = st.sidebar.columns([1, 1])
with col1:
    if st.button("🔄 Refresh Status", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with col2:
    if st.button("▶️ Trigger DAG", use_container_width=True):
        trigger_dag_run()

# Display Airflow DAG status
dag_status = get_airflow_dag_status()
latest_run = get_latest_dag_run()
tasks_status = get_dag_tasks_status()

if dag_status:
    st.sidebar.markdown("### DAG Status")
    st.sidebar.metric("DAG ID", dag_status.get('dag_id', 'N/A'))
    st.sidebar.metric("Is Active", dag_status.get('is_active', False))
    
if latest_run:
    st.sidebar.markdown("### Latest Run")
    st.sidebar.metric("Execution Date", latest_run.get('execution_date', 'N/A')[:10])
    run_state = latest_run.get('state', 'UNKNOWN')
    color = '🟢' if run_state == 'success' else '🔴' if run_state == 'failed' else '🟡'
    st.sidebar.metric("State", f"{color} {run_state}")
    
    if tasks_status:
        st.sidebar.markdown("### Task Status")
        for task in tasks_status:
            task_id = task.get('task_id', 'unknown')
            task_state = task.get('state', 'UNKNOWN')
            task_color = '✅' if task_state == 'success' else '❌' if task_state == 'failed' else '⏳'
            st.sidebar.write(f"{task_color} {task_id}: {task_state}")

# --- Main Dashboard ---
st.sidebar.header("Filters")
df = load_data()
# Auto-refresh controls
auto_refresh = st.sidebar.checkbox("Auto-refresh", value=False)
refresh_interval = st.sidebar.slider("Refresh interval (sec)", min_value=2, max_value=60, value=5)
if st.sidebar.button("Refresh now"):
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.sidebar.info("Manual refresh requested — please reload the page if it doesn't update automatically.")

if not df.empty:
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        # Convert pandas Timestamp to native python datetimes for Streamlit widgets
        min_date = df['timestamp'].min().to_pydatetime()
        max_date = df['timestamp'].max().to_pydatetime()
        # If only one timestamp present, use slider fallback handling
        try:
            date_range = st.sidebar.slider("Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date))
            df = df[(df['timestamp'] >= pd.to_datetime(date_range[0])) & (df['timestamp'] <= pd.to_datetime(date_range[1]))]
        except Exception:
            # Fallback: single-value or incompatible types — don't filter
            pass
    if 'vehicle_type' in df.columns:
        vehicle_types = df['vehicle_type'].unique().tolist()
        selected_types = st.sidebar.multiselect("Vehicle Type", vehicle_types, default=vehicle_types)
        df = df[df['vehicle_type'].isin(selected_types)]

    # Overspeed threshold control (sidebar)
    if 'speed' in df.columns:
        overspeed_threshold = st.sidebar.slider("Overspeed threshold (km/h)", min_value=20, max_value=200, value=120)
    else:
        overspeed_threshold = 120

    st.subheader("Raw Traffic Data (Live)")
    st.dataframe(df, width='stretch')

    # Summary statistics
    st.subheader("Summary Statistics")
    st.write(df.describe(include='all'))
    
    # KPI Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", len(df))
    with col2:
        if 'speed' in df.columns:
            st.metric("Avg Speed", f"{df['speed'].mean():.2f} km/h")
    with col3:
        if 'speed' in df.columns:
            st.metric("Max Speed", f"{df['speed'].max():.2f} km/h")
    with col4:
        if 'speed' in df.columns and df['speed'].max() > overspeed_threshold:
            overspeeding = (df['speed'] > overspeed_threshold).sum()
            st.metric("Overspeeding", overspeeding)

    # Vehicle count by type (pie chart)
    if 'vehicle_type' in df.columns:
        st.subheader("Vehicle Count by Type")
        st.plotly_chart({
            "data": [{
                "values": df['vehicle_type'].value_counts().values,
                "labels": df['vehicle_type'].value_counts().index,
                "type": "pie"
            }],
            "layout": {"title": "Vehicle Type Distribution"}
        }, use_container_width=True)

    # --- Enhanced Time Series Controls ---
    st.markdown("---")
    st.subheader("Traffic Over Time — Controls")
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        metric = st.selectbox("Metric", options=[
            'count', 'avg_speed', 'max_speed', 'min_speed', 'overspeeding_count'
        ], index=0)
    with col2:
        resample_freq = st.selectbox("Resample frequency", options=['1min', '5min', '15min', '1H'], index=0)
    with col3:
        rolling_enabled = st.checkbox("Rolling avg")
    rolling_window = None
    if rolling_enabled:
        rolling_window = st.slider("Rolling window (periods)", min_value=2, max_value=60, value=3)

    split_by_location = False
    if 'location' in df.columns:
        split_by_location = st.checkbox("Split by location", value=False)

    # Time series chart (enhanced)
    if 'timestamp' in df.columns:
        st.subheader("Traffic Over Time (Live)")
        try:
            df_ts = df.copy()
            df_ts = df_ts.set_index('timestamp')

            # Build the aggregated series depending on metric
            if metric == 'count':
                if split_by_location and 'location' in df_ts.columns:
                    agg = df_ts.groupby('location').resample(resample_freq).size().unstack(level=0).fillna(0)
                else:
                    agg = df_ts.resample(resample_freq).size().rename('value')
            elif metric in ('avg_speed', 'max_speed', 'min_speed'):
                col = 'speed'
                if split_by_location and 'location' in df_ts.columns:
                    agg = df_ts.groupby('location').resample(resample_freq)[col].agg({'avg_speed':'mean','max_speed':'max','min_speed':'min'})
                    if metric == 'avg_speed':
                        agg = agg['avg_speed'].unstack(level=0).fillna(0)
                    else:
                        agg = agg[metric].unstack(level=0).fillna(0)
                else:
                    if metric == 'avg_speed':
                        agg = df_ts.resample(resample_freq)['speed'].mean().fillna(0).rename('value')
                    elif metric == 'max_speed':
                        agg = df_ts.resample(resample_freq)['speed'].max().fillna(0).rename('value')
                    else:
                        agg = df_ts.resample(resample_freq)['speed'].min().fillna(0).rename('value')
            elif metric == 'overspeeding_count':
                if 'speed' not in df_ts.columns:
                    st.error('No speed column available for overspeeding_count')
                    agg = None
                else:
                    df_ts['overspeeding'] = df_ts['speed'] > overspeed_threshold
                    if split_by_location and 'location' in df_ts.columns:
                        agg = df_ts.groupby('location').resample(resample_freq)['overspeeding'].sum().unstack(level=0).fillna(0)
                    else:
                        agg = df_ts.resample(resample_freq)['overspeeding'].sum().fillna(0).rename('value')
            else:
                agg = None

            if agg is None:
                st.info('No data to plot for selected metric.')
            else:
                # Apply rolling average if requested (works for single series and DataFrame)
                if rolling_enabled and rolling_window and rolling_window > 1:
                    try:
                        agg = agg.rolling(window=rolling_window, min_periods=1).mean()
                    except Exception:
                        pass

                # Prepare for Plotly: if agg is Series -> reset_index; if DataFrame -> melt
                if isinstance(agg, pd.Series):
                    plot_df = agg.rename('value').reset_index()
                    fig = px.line(plot_df, x=plot_df.columns[0], y='value', title=f"{metric} ({resample_freq})")
                else:
                    # DataFrame with multiple columns (locations)
                    plot_df = agg.reset_index()
                    plot_df = plot_df.melt(id_vars=plot_df.columns[0], var_name='location', value_name='value')
                    fig = px.line(plot_df, x=plot_df.columns[0], y='value', color='location', title=f"{metric} ({resample_freq})")

                # --- Trend arrow / delta metric ---
                try:
                    if isinstance(agg, pd.Series):
                        if len(agg) >= 2:
                            last = float(agg.iloc[-1])
                            prev = float(agg.iloc[-2])
                            delta = last - prev
                            pct = (delta / prev * 100) if prev != 0 else 0.0
                            st.metric("Latest", f"{last:.2f}", delta=f"{delta:+.2f} ({pct:+.1f}%)")

                            # Add arrow annotation to Plotly chart showing direction
                            try:
                                last_idx = agg.index[-1]
                                prev_idx = agg.index[-2]
                                last_x = last_idx
                                prev_x = prev_idx
                                last_y = last
                                prev_y = prev
                                arrow_color = 'green' if delta >= 0 else 'red'
                                fig.add_annotation(x=last_x, y=last_y,
                                                   ax=prev_x, ay=prev_y,
                                                   xref='x', yref='y', axref='x', ayref='y',
                                                   showarrow=True, arrowhead=3, arrowcolor=arrow_color,
                                                   arrowsize=2)
                            except Exception:
                                pass

                    else:
                        # For multi-location DataFrame, compute total across locations
                        if agg.shape[0] >= 2:
                            last_total = float(agg.iloc[-1].sum())
                            prev_total = float(agg.iloc[-2].sum())
                            delta = last_total - prev_total
                            pct = (delta / prev_total * 100) if prev_total != 0 else 0.0
                            st.metric("Latest (all locations)", f"{last_total:.2f}", delta=f"{delta:+.2f} ({pct:+.1f}%)")

                            # Per-location mini metrics when splitting
                            try:
                                if split_by_location:
                                    loc_cols = agg.columns.tolist()
                                    # Show metrics in rows of up to 4 columns
                                    for i in range(0, len(loc_cols), 4):
                                        cols = st.columns(min(4, len(loc_cols) - i))
                                        for j, loc in enumerate(loc_cols[i:i+4]):
                                            try:
                                                last_val = float(agg.iloc[-1][loc])
                                                prev_val = float(agg.iloc[-2][loc])
                                                d = last_val - prev_val
                                                p = (d / prev_val * 100) if prev_val != 0 else 0.0
                                                cols[j].metric(loc, f"{last_val:.2f}", delta=f"{d:+.2f} ({p:+.1f}%)")
                                            except Exception:
                                                cols[j].metric(loc, "n/a", delta="n/a")
                            except Exception:
                                pass
                except Exception:
                    # Don't break plotting for minor calculation issues
                    pass

                fig.update_layout(xaxis_title='Time', yaxis_title=metric)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Could not render time series: {e}")
    # Live map (if location data exists)
    # Map textual location names to coordinates for demo purposes
    location_coords = {
        'Airport Road': (37.615, -122.389),
        'City Center': (37.776, -122.417),
        'Downtown': (37.789, -122.401),
        'Highway A1': (37.804, -122.271),
        'Highway A2': (37.687, -122.470),
    }

    if 'location' in df.columns:
        st.subheader("Live Traffic Map")
        st.write(f"Locations in data: {df['location'].unique().tolist()}")  # Debug: show locations
        # Try to map known textual locations to coordinates
        coords_with_loc = []
        for loc in df['location']:
            if isinstance(loc, str) and loc in location_coords:
                lat, lon = location_coords[loc]
                coords_with_loc.append((lat, lon, loc))
        
        if coords_with_loc:
            avg_lat = sum([c[0] for c in coords_with_loc]) / len(coords_with_loc)
            avg_lon = sum([c[1] for c in coords_with_loc]) / len(coords_with_loc)
            m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
            
            # Add markers for each location
            for lat, lon, loc in coords_with_loc:
                folium.CircleMarker(
                    location=[lat, lon], 
                    radius=8, 
                    color='red', 
                    fill=True,
                    fillColor='red',
                    fillOpacity=0.7,
                    popup=loc,
                    tooltip=loc
                ).add_to(m)
            
            st_folium(m, width=None, height=500)
        else:
            st.warning("⚠️ No valid location coordinates found in data. Available locations: " + str(df['location'].unique().tolist() if not df.empty else "No data"))
    else:
        st.info("ℹ️ No 'location' column in data. Map will appear once location data is available.")

    # Download/export
    st.download_button("Download Filtered Data", df.to_csv(index=False), file_name="traffic_data_filtered.csv")

    # Live auto-refresh: sleep then rerun if supported
    if auto_refresh:
        time.sleep(refresh_interval)
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
        else:
            st.sidebar.info("Auto-refresh requested but st.experimental_rerun is not available in this Streamlit version. Use 'Refresh now' button.")
else:
    st.warning(f"No data found at {data_path}. Run the ETL pipeline first or trigger the DAG above.")

st.markdown("---")
st.info("✨ Dashboard connected to Airflow DAG. Use 'Trigger DAG' to run the ETL pipeline.")
