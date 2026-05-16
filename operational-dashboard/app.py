import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Healthcare ETL Ops Console",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PROFESSIONAL UI STYLING (FIXED INJECTION) ---
st.markdown("""
<style>
    /* Prevent CSS Leak */
    .stMarkdown div { font-family: 'Inter', sans-serif; }
    
    /* Main Background */
    .stApp {
        background-color: #F4F7FA !important;
    }
    
    /* Sidebar Overhaul */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebarNav"] {
        background-color: transparent !important;
    }
    
    /* Metric Card Design */
    .metric-container {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .metric-title {
        font-size: 0.75rem;
        color: #64748B;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 1.75rem;
        color: #0F172A;
        font-weight: 700;
        line-height: 1;
    }
    .metric-trend {
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 8px;
    }
    .trend-up { color: #059669; }
    .trend-down { color: #DC2626; }
    
    /* Global Typography */
    h1, h2, h3 {
        color: #0F172A !important;
        font-weight: 700 !important;
    }
    p, span, label {
        color: #475569;
    }
    
    /* Badges */
    .env-badge {
        background-color: #1E293B;
        color: #94A3B8 !important;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        border: 1px solid #334155;
    }
    
    /* Alerts */
    .op-alert {
        padding: 12px;
        border-radius: 6px;
        border-left: 4px solid;
        margin-bottom: 10px;
        font-size: 0.85rem;
    }
    .alert-info { background-color: #F0F9FF; border-color: #0EA5E9; color: #0369A1; }
    .alert-warn { background-color: #FFFBEB; border-color: #D97706; color: #92400E; }
    .alert-err  { background-color: #FEF2F2; border-color: #DC2626; color: #991B1B; }

    /* Hide Branding but keep Toggle Button */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Ensure Sidebar Toggle is accessible */
    button[kind="header"] {
        color: #0F172A !important;
    }
</style>
""", unsafe_allow_html=True)

# --- MOCK DATA ENGINE ---
@st.cache_data
def get_ops_metrics():
    return {
        "throughput": 124580,
        "accuracy": 98.4,
        "quarantine": 456,
        "anomalies": 12,
        "last_sync": "14 mins ago"
    }

@st.cache_data
def get_trend_data():
    dates = pd.date_range(end=datetime.now(), periods=30)
    return pd.DataFrame({
        "Date": dates,
        "Volume": np.random.randint(4500, 5500, size=30)
    })

# --- HELPER: OPERATIONAL METRIC CARD ---
def render_metric(label, value, trend, is_up=True):
    trend_class = "trend-up" if is_up else "trend-down"
    trend_icon = "▲" if is_up else "▼"
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-title">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-trend {trend_class}">{trend_icon} {trend}</div>
        </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR: Azure Ops Look ---
with st.sidebar:
    if os.path.exists("operational-dashboard/logo.png"):
        st.image("operational-dashboard/logo.png")
    
    st.markdown('<div style="margin: 10px 0 25px 0;">'
                '<span class="env-badge">PRODUCTION</span> '
                '<span class="env-badge">EAST-US</span>'
                '</div>', unsafe_allow_html=True)
    
    menu = st.radio("OPERATIONS CONSOLE", 
                   ["Executive Overview", "Pipeline Telemetry", "Data Integrity", "Architecture"],
                   index=0)
    
    st.divider()
    st.markdown("### Resource Monitoring")
    st.caption("Databricks Cluster: `db-claims-prd-01`")
    st.caption("Synapse Pool: `syn-health-sql-01`")
    st.caption("Last Deployment: `2024-05-16.R1`")

# --- MAIN CONTENT ---
metrics = get_ops_metrics()

if menu == "Executive Overview":
    st.title("Platform Command Center")
    st.markdown("Global operational telemetry for Healthcare Claims Medallion architecture.")
    
    # Operational Metrics Grid
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric("30D Throughput", f"{metrics['throughput']:,}", "12.4% vs LY")
    with c2:
        render_metric("Pipeline Accuracy", f"{metrics['accuracy']}%", "0.2% improvement")
    with c3:
        render_metric("Quarantine Backlog", f"{metrics['quarantine']}", "5 resolved", False)
    with c4:
        render_metric("Recon Anomalies", f"{metrics['anomalies']}", "2 new alerts", False)

    st.markdown('<div style="margin-top: 30px;"></div>', unsafe_allow_html=True)
    
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        st.subheader("Ingestion Velocity")
        trends = get_trend_data()
        fig = px.area(trends, x="Date", y="Volume", color_discrete_sequence=['#155E75'])
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=False, color="#64748B"),
            yaxis=dict(showgrid=True, gridcolor='#F1F5F9', color="#64748B")
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_side:
        st.subheader("Active Operational Alerts")
        st.markdown('<div class="op-alert alert-info"><b>Latency:</b> CIGNA feed delayed by 45m. Expected 12:00.</div>', unsafe_allow_html=True)
        st.markdown('<div class="op-alert alert-warn"><b>Schema:</b> Drift detected in Bronze/Provider feed. Auto-merging.</div>', unsafe_allow_html=True)
        st.markdown('<div class="op-alert alert-err"><b>Recon:</b> Mismatch in Batch-2024A (12 orphaned records).</div>', unsafe_allow_html=True)
        
        st.subheader("Process Sync")
        st.table(pd.DataFrame({
            "Stage": ["Ingest", "Cleanse", "Agg", "Sync"],
            "Status": ["OK", "OK", "WARN", "OK"]
        }))

elif menu == "Pipeline Telemetry":
    st.title("Pipeline Run Monitoring")
    st.markdown("Databricks Job Execution Details")
    
    df_runs = pd.DataFrame([
        dict(Task="Bronze Ingest", Start='2024-05-16 01:00', Finish='2024-05-16 01:10', Layer="Bronze"),
        dict(Task="Silver Cleanse", Start='2024-05-16 01:12', Finish='2024-05-16 01:25', Layer="Silver"),
        dict(Task="Gold Aggs", Start='2024-05-16 01:26', Finish='2024-05-16 01:35', Layer="Gold"),
        dict(Task="Synapse Sync", Start='2024-05-16 01:36', Finish='2024-05-16 01:45', Layer="Synapse"),
    ])
    fig_gantt = px.timeline(df_runs, x_start="Start", x_end="Finish", y="Task", color="Layer",
                            color_discrete_sequence=['#0EA5E9', '#0F766E', '#0369A1', '#0F172A'])
    st.plotly_chart(fig_gantt, use_container_width=True)

    st.subheader("Quarantine Pool Explorer")
    st.markdown("Records currently isolated in `abfss://quarantine@datalake/claims/`")
    st.table(pd.DataFrame({
        "Claim_ID": ["CLM-8821", "CLM-8822", "CLM-8825"],
        "Reason": ["Invalid_NPI", "Negative_Amt", "Future_Date"],
        "Detected_At": ["01:15", "01:15", "01:15"]
    }))
    
    if st.button("Trigger Manual Batch Recovery"):
        st.toast("Triggering Recovery Pipeline...")
        st.success("ADF Request Sent: REC-2024-01")

elif menu == "Data Integrity":
    st.title("Data Integrity & Reconciliation")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Operational Reconciliation")
        st.table(pd.DataFrame({
            "Stage": ["Raw Files", "Bronze Delta", "Silver Delta", "Gold Fact"],
            "Count": [12450, 12450, 12398, 12398],
            "Delta": ["-", "0", "-52", "0"]
        }))
    with col2:
        st.markdown("#### Quality Metrics")
        nulls = pd.DataFrame({"Field": ["Member", "Provider", "CPT", "Diag"], "Fill%": [99.8, 99.2, 85.6, 98.4]})
        st.plotly_chart(px.bar(nulls, x="Field", y="Fill%", color_discrete_sequence=['#059669']), use_container_width=True)

elif menu == "Architecture":
    st.title("Platform Architecture")
    if os.path.exists("operational-dashboard/architecture.png"):
        st.image("operational-dashboard/architecture.png")
    
    st.markdown("""
    ---
    ### Operational Stack
    - **Control:** Azure Data Factory (V2)
    - **Compute:** Azure Databricks (Shared Cluster)
    - **Storage:** Delta Lake on ADLS Gen2
    - **Serving:** Azure Synapse Analytics (DW100c)
    """)
