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
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
    /* Global Styles */
    .main {
        background-color: #f4f7f9;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Metric Card Styling */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e6ed;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        transition: transform 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.05);
    }
    
    /* Header Styling */
    h1, h2, h3 {
        color: #1a202c;
        font-weight: 700;
    }
    
    /* Status Badges */
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .status-prod { background-color: #e3f2fd; color: #1976d2; }
    .status-region { background-color: #f1f8e9; color: #388e3c; }
    
    /* Table Styling */
    .stTable {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Custom Title Area */
    .title-area {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 30px;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

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
        
    st.markdown('<div style="margin-bottom: 20px;">'
                '<span class="status-badge status-prod">Prod Env</span> '
                '<span class="status-badge status-region">East US</span>'
                '</div>', unsafe_allow_html=True)
    
    menu = st.radio("Navigation", 
                   ["Executive Summary", "Pipeline Monitoring", "Data Quality", "Architecture"],
                   index=0)
    
    st.divider()
    st.caption("v1.4.2-stable | Build: 2024.05.16.R1")

# --- MAIN CONTENT ---
metrics = get_mock_metrics()

if menu == "Executive Summary":
    st.title("Healthcare Claims Pipeline")
    st.markdown("Global operational overview for the Azure Medallion architecture.")
    
    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Claims (30D)", f"{metrics['total_claims']:,}", "↑ 12%")
    with c2:
        st.metric("SLA Success Rate", f"{metrics['success_rate']}%", "0.2%")
    with c3:
        st.metric("In Quarantine", f"{metrics['quarantine_count']}", "-5", delta_color="inverse")
    with c4:
        st.metric("Recon Mismatches", f"{metrics['reconcile_mismatch']}", "2", delta_color="inverse")

    st.divider()
    
    # Trends
    st.subheader("Daily Ingestion Activity")
    trends = get_daily_trends()
    fig = px.area(trends, x="Date", y="Volume", 
                  title="Bronze Layer Ingestion Volume",
                  color_discrete_sequence=['#0078D4'])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.subheader("Operational Alerts")
        st.info("**Feed Delayed:** CIGNA-NORTH batch missing for 06:00 window.")
        st.warning("**Schema Evolution:** New column `telehealth_flag` detected and merged.")
        st.error("**Reconciliation:** Batch 20240516-A has 12 missing records in Gold.")
    
    with col_b:
        st.subheader("Latest Pipeline Executions")
        runs = pd.DataFrame({
            "Run ID": ["ad45", "df89", "cc12", "aa01"],
            "Pipeline": ["Master_ETL", "Master_ETL", "Ref_Sync", "Master_ETL"],
            "Status": ["✅ Success", "✅ Success", "❌ Failed", "✅ Success"],
            "Time": ["10:00", "08:00", "07:30", "06:00"]
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
                            color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_gantt, use_container_width=True)

    st.subheader("Quarantine Review (Silver Layer)")
    q_data = get_quarantine_data()
    st.dataframe(q_data, use_container_width=True)
    
    if st.button("Manual Retry: Replay Quarantine Batch"):
        st.toast("Triggering ADF Pipeline `Retry_Quarantine`...")
        st.success("Request sent. Tracking ID: REPLAY-9923")

elif menu == "Data Quality":
    st.title("Data Integrity & Reconciliation")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Medallion Reconciliation")
        recon = pd.DataFrame({
            "Layer": ["Source Files", "Bronze Delta", "Silver Delta", "Gold Fact", "Synapse SQL"],
            "Count": [12450, 12450, 12398, 12398, 12398],
            "Delta": ["-", "0", "-52", "0", "0"]
        })
        st.table(recon)
    
    with col2:
        st.markdown("#### Provider Validation Nulls")
        nulls = pd.DataFrame({
            "Field": ["claim_id", "member_id", "npi_code", "icd10", "amt"],
            "Null%": [0.0, 1.2, 0.8, 15.4, 0.0]
        })
        fig_nulls = px.bar(nulls, x="Field", y="Null%", title="Missing Values per Field",
                           color_discrete_sequence=['#FF4B4B'])
        st.plotly_chart(fig_nulls, use_container_width=True)

elif menu == "Architecture":
    st.title("Platform Architecture")
    
    if os.path.exists("operational-dashboard/architecture.png"):
        st.image("operational-dashboard/architecture.png", use_container_width=True)
    else:
        st.info("Architecture diagram rendering...")

    st.markdown("""
    ### System Components
    - **ADF:** Master orchestration and control flow.
    - **Databricks:** Spark-based Medallion processing (Bronze/Silver/Gold).
    - **Synapse:** Serving layer for high-concurrency BI.
    - **Delta Lake:** Transactional storage with schema enforcement.
    """)
