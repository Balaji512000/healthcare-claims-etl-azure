import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Azure Healthcare ETL Ops",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THEME & CUSTOM CSS ---
def local_css():
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
        .main {
            background-color: #ffffff !important;
            font-family: 'Inter', sans-serif;
        }
        [data-testid="stSidebar"] {
            background-color: #fcfcfc !important;
            border-right: 1px solid #eeeeee;
        }
        div[data-testid="metric-container"] {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        div[data-testid="metric-container"]:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
            border-color: #cbd5e1;
            background-color: #ffffff;
        }
        div[data-testid="stMetricValue"] {
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            color: #0f172a !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            color: #64748b !important;
            text-transform: uppercase;
            letter-spacing: 0.025em;
            margin-bottom: 8px;
        }
        h1, h2, h3 {
            color: #0f172a !important;
            font-weight: 700;
        }
        .status-badge {
            padding: 6px 14px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .status-prod { background-color: #dcfce7; color: #166534; }
        .status-region { background-color: #e0f2fe; color: #075985; }
        .stTable {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #f1f5f9;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

local_css()

# --- MOCK DATA ENGINE ---
@st.cache_data
def get_mock_metrics():
    return {
        "total_claims": 124580,
        "success_rate": 98.4,
        "failed_claims": 1942,
        "quarantine_count": 456,
        "reconcile_mismatch": 12,
        "avg_duration_mins": 24.5,
        "last_run": datetime.now() - timedelta(hours=2)
    }

@st.cache_data
def get_daily_trends():
    dates = pd.date_range(end=datetime.now(), periods=30)
    data = pd.DataFrame({
        "Date": dates,
        "Volume": np.random.randint(4000, 6000, size=30),
        "Failed": np.random.randint(20, 100, size=30)
    })
    return data

@st.cache_data
def get_quarantine_data():
    reasons = ["null_claim_id", "negative_amount", "future_claim_date", "malformed_npi", "invalid_plan_id"]
    return pd.DataFrame({
        "Claim ID": [f"CLM-{1000+i}" for i in range(15)],
        "Reason": np.random.choice(reasons, 15),
        "Provider ID": [f"PROV-{np.random.randint(500, 999)}" for _ in range(15)],
        "Amount": np.random.uniform(50, 5000, 15).round(2),
        "Ingested At": [datetime.now() - timedelta(hours=i) for i in range(15)]
    })

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("operational-dashboard/logo.png"):
        st.image("operational-dashboard/logo.png", use_container_width=True)
    else:
        st.title("🏥 ETL Ops")
        
    st.markdown('<div style="margin-bottom: 24px; display: flex; gap: 8px;">'
                '<span class="status-badge status-prod">Prod</span>'
                '<span class="status-badge status-region">East US</span>'
                '</div>', unsafe_allow_html=True)
    
    menu = st.radio("Management Console", 
                   ["Executive Summary", "Pipeline Monitoring", "Data Quality", "Architecture"],
                   index=0)
    
    st.divider()
    st.caption("v1.4.2-stable | Azure Healthcare")

# --- MAIN CONTENT ---
metrics = get_mock_metrics()

if menu == "Executive Summary":
    st.title("Operations Command Center")
    st.markdown("Real-time telemetry for Healthcare Claims Medallion pipelines.")
    
    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
    
    # KPIs with Icons
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Throughput", f"{metrics['total_claims']:,}", "↑ 12%")
    with c2:
        st.metric("Pipeline Accuracy", f"{metrics['success_rate']}%", "0.2%")
    with c3:
        st.metric("Quarantine Pool", f"{metrics['quarantine_count']}", "-5", delta_color="inverse")
    with c4:
        st.metric("Recon Anomalies", f"{metrics['reconcile_mismatch']}", "2", delta_color="inverse")

    st.markdown('<div style="margin-top: 40px;"></div>', unsafe_allow_html=True)
    
    # Trends
    st.subheader("Ingestion Velocity (Bronze)")
    trends = get_daily_trends()
    fig = px.area(trends, x="Date", y="Volume", 
                  color_discrete_sequence=['#3b82f6'])
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
    )
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.subheader("Operational Alerts")
        st.info("**Data Latency:** CIGNA source feed delayed by 45 mins.")
        st.warning("**Schema Evolution:** Auto-detecting new CPT codes in Silver.")
        st.error("**Reconciliation:** 12 records orphaned in Synapse landing.")
    
    with col_b:
        st.subheader("Sync Status")
        runs = pd.DataFrame({
            "Job": ["Ingest_Raw", "Cleanse_Silver", "Agg_Gold", "Sync_Synapse"],
            "Status": ["✅ Active", "✅ Active", "⚠️ Delayed", "✅ Active"],
            "Last Run": ["10:05", "10:15", "10:30", "11:00"]
        })
        st.table(runs)

elif menu == "Pipeline Monitoring":
    st.title("Pipeline Run Monitoring")
    
    st.markdown("### ADF Execution Sequence")
    df_runs = pd.DataFrame([
        dict(Task="Bronze Ingest", Start='2024-05-16 01:00', Finish='2024-05-16 01:10', Step="Ingest"),
        dict(Task="Silver Cleanse", Start='2024-05-16 01:12', Finish='2024-05-16 01:25', Step="Cleansing"),
        dict(Task="Gold Aggs", Start='2024-05-16 01:26', Finish='2024-05-16 01:35', Step="Aggregations"),
        dict(Task="Synapse Sync", Start='2024-05-16 01:36', Finish='2024-05-16 01:45', Step="Serving"),
    ])
    fig_gantt = px.timeline(df_runs, x_start="Start", x_end="Finish", y="Task", color="Step",
                            color_discrete_sequence=px.colors.qualitative.Bold)
    st.plotly_chart(fig_gantt, use_container_width=True)

    st.subheader("Quarantine Ledger")
    q_data = get_quarantine_data()
    st.dataframe(q_data, use_container_width=True)
    
    if st.button("Trigger Manual Recovery"):
        st.toast("Starting Recovery Pipeline...")
        st.success("ADF Instance: REC-8821 triggered.")

elif menu == "Data Quality":
    st.title("Data Integrity")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Record Balancing")
        recon = pd.DataFrame({
            "Stage": ["Raw", "Bronze", "Silver", "Gold", "SQL"],
            "Records": [12450, 12450, 12398, 12398, 12398],
            "Status": ["OK", "OK", "-52", "OK", "OK"]
        })
        st.table(recon)
    
    with col2:
        st.markdown("#### Field Completeness")
        nulls = pd.DataFrame({
            "Field": ["member_id", "provider_id", "cpt_code", "diagnosis"],
            "Fill%": [99.8, 99.2, 85.6, 98.4]
        })
        fig_nulls = px.bar(nulls, x="Field", y="Fill%", color_discrete_sequence=['#10b981'])
        st.plotly_chart(fig_nulls, use_container_width=True)

elif menu == "Architecture":
    st.title("System Architecture")
    
    if os.path.exists("operational-dashboard/architecture.png"):
        st.image("operational-dashboard/architecture.png", use_container_width=True)
    
    st.markdown("""
    ---
    ### Technical Stack
    - **Control Plane:** Azure Data Factory
    - **Compute Engine:** Databricks / Spark SQL
    - **Storage Fabric:** Delta Lake on ADLS Gen2
    - **Analytical Engine:** Azure Synapse SQL Pool
    """)
