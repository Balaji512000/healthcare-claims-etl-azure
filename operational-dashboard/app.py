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
        /* Base styles */
        .main {
            background-color: #f8fafc !important;
            font-family: 'Inter', sans-serif;
        }
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #e2e8f0;
        }
        
        /* Metric Card Styling */
        .metric-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            transition: all 0.2s ease-in-out;
        }
        .metric-card:hover {
            border-color: #3b82f6;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        .metric-label {
            font-size: 0.75rem;
            color: #64748b;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }
        .metric-value {
            font-size: 1.8rem;
            color: #1e293b;
            font-weight: 700;
            line-height: 1;
        }
        .metric-delta {
            font-size: 0.8rem;
            font-weight: 600;
            margin-top: 8px;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .delta-up { color: #10b981; }
        .delta-down { color: #ef4444; }
        
        /* Headers */
        h1, h2, h3 {
            color: #0f172a !important;
            font-weight: 700;
        }
        
        /* Badges */
        .status-badge {
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
        }
        .status-prod { background-color: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }
        .status-region { background-color: #eff6ff; color: #1d4ed8; border: 1px solid #dbeafe; }
        
        /* Clean up UI */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Table cleanup */
        .stTable {
            background-color: #ffffff;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }
        </style>
    """, unsafe_allow_html=True)

local_css()

def custom_metric(label, value, delta, delta_type="up"):
    delta_class = "delta-up" if delta_type == "up" else "delta-down"
    delta_symbol = "▲" if delta_type == "up" else "▼"
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-delta {delta_class}">
                <span>{delta_symbol}</span> {delta}
            </div>
        </div>
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
    
    st.markdown('<div style="margin: 20px 0; display: flex; gap: 8px;">'
                '<span class="status-badge status-prod">PROD</span>'
                '<span class="status-badge status-region">EAST US</span>'
                '</div>', unsafe_allow_html=True)
    
    menu = st.radio("PLATFORM CONSOLE", 
                   ["Overview", "Pipelines", "Quality", "Architecture"],
                   index=0)
    
    st.divider()
    st.caption("Azure Healthcare Claims ETL | v1.4.2")

# --- MAIN CONTENT ---
metrics = get_mock_metrics()

if menu == "Overview":
    st.title("Operations Command Center")
    st.markdown("Real-time operational telemetry for the Medallion Data Platform.")
    
    # Custom Metric Grid
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        custom_metric("Total Throughput", f"{metrics['total_claims']:,}", "12%", "up")
    with c2:
        custom_metric("Pipeline Accuracy", f"{metrics['success_rate']}%", "0.2%", "up")
    with c3:
        custom_metric("Quarantine Pool", f"{metrics['quarantine_count']}", "5", "down")
    with c4:
        custom_metric("Recon Anomalies", f"{metrics['reconcile_mismatch']}", "2", "up")

    st.markdown('<div style="margin-top: 32px;"></div>', unsafe_allow_html=True)
    
    # Trends
    st.subheader("Ingestion Velocity")
    trends = get_daily_trends()
    fig = px.line(trends, x="Date", y="Volume", color_discrete_sequence=['#3b82f6'])
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0')
    )
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Active Incidents")
        st.info("**Latency:** CIGNA source feed delayed by 45m.")
        st.warning("**Schema:** New CPT codes detected in Silver layer.")
    
    with col_b:
        st.subheader("Execution Status")
        runs = pd.DataFrame({
            "Stage": ["Ingest", "Cleanse", "Agg", "Sync"],
            "Status": ["✅ Active", "✅ Active", "⚠️ Warning", "✅ Active"]
        })
        st.table(runs)

elif menu == "Pipelines":
    st.title("Pipeline Run Monitoring")
    df_runs = pd.DataFrame([
        dict(Task="Bronze", Start='2024-05-16 01:00', Finish='2024-05-16 01:10', Step="Ingest"),
        dict(Task="Silver", Start='2024-05-16 01:12', Finish='2024-05-16 01:25', Step="Clean"),
        dict(Task="Gold", Start='2024-05-16 01:26', Finish='2024-05-16 01:35', Step="Agg"),
        dict(Task="Synapse", Start='2024-05-16 01:36', Finish='2024-05-16 01:45', Step="Serve"),
    ])
    fig_gantt = px.timeline(df_runs, x_start="Start", x_end="Finish", y="Task", color="Step",
                            color_discrete_sequence=px.colors.qualitative.Safe)
    st.plotly_chart(fig_gantt, use_container_width=True)

elif menu == "Quality":
    st.title("Data Integrity")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Balancing Check")
        st.table(pd.DataFrame({
            "Layer": ["Source", "Bronze", "Silver", "Gold"],
            "Records": [12450, 12450, 12398, 12398]
        }))
    with col2:
        st.markdown("#### Fill Rate Analysis")
        nulls = pd.DataFrame({"Field": ["member_id", "provider_id", "cpt"], "Fill%": [99.8, 99.2, 85.6]})
        st.plotly_chart(px.bar(nulls, x="Field", y="Fill%", color_discrete_sequence=['#10b981']), use_container_width=True)

elif menu == "Architecture":
    st.title("Architecture Overview")
    if os.path.exists("operational-dashboard/architecture.png"):
        st.image("operational-dashboard/architecture.png", use_container_width=True)
