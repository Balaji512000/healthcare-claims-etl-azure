import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Healthcare ETL Ops Portal",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR INTERNAL OPS LOOK ---
st.markdown("""
    <style>
    .main {
        background-color: #F8F9FA;
    }
    .stMetric {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .status-up { color: #107C10; font-weight: bold; }
    .status-down { color: #D13438; font-weight: bold; }
    .status-warn { color: #FFB900; font-weight: bold; }
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
    data = pd.DataFrame({
        "Claim ID": [f"CLM-{1000+i}" for i in range(10)],
        "Reason": np.random.choice(reasons, 10),
        "Provider ID": [f"PROV-{np.random.randint(500, 999)}" for _ in range(10)],
        "Amount": np.random.uniform(50, 5000, 10).round(2),
        "Ingested At": [datetime.now() - timedelta(hours=i) for i in range(10)]
    })
    return data

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://img.icons8.com/color/96/azure-data-factory.png", width=60)
st.sidebar.title("ETL Ops Portal")
st.sidebar.markdown("`Env: Production` | `Region: East US`")

menu = st.sidebar.selectbox(
    "Navigation",
    ["Executive Summary", "Pipeline Monitoring", "Data Quality & Recon", "Medallion Explorer", "Architecture"]
)

metrics = get_mock_metrics()

# --- 1. EXECUTIVE SUMMARY ---
if menu == "Executive Summary":
    st.title("🏥 Healthcare Claims Pipeline Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Claims (30D)", f"{metrics['total_claims']:,}")
    with col2:
        st.metric("Success Rate", f"{metrics['success_rate']}%", "0.2%")
    with col3:
        st.metric("Quarantined", f"{metrics['quarantine_count']}", "-5", delta_color="inverse")
    with col4:
        st.metric("Recon Mismatches", f"{metrics['reconcile_mismatch']}", "2", delta_color="inverse")

    st.subheader("Daily Ingestion Trend")
    trends = get_daily_trends()
    fig = px.line(trends, x="Date", y="Volume", title="Claim Volume (Bronze Ingestion)")
    fig.add_bar(x=trends["Date"], y=trends["Failed"], name="Failed Records")
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Operational Alerts")
        st.info("⚠️ **Provider feed delayed:** CIGNA-NORTH-01 has not delivered files for the 06:00 window.")
        st.warning("🚨 **Schema Drift:** New column `telehealth_indicator` detected in Bronze. Auto-merged to schema.")
        st.error("🔥 **Reconciliation Alert:** Batch 20240516-A mismatch in Synapse (Source: 4502, Target: 4490)")
    
    with col_b:
        st.subheader("Recent ADF Runs")
        runs = pd.DataFrame({
            "Run ID": ["ad45-12b", "df89-44x", "cc12-99p", "aa01-55k"],
            "Pipeline": ["Master_Claims_ETL", "Master_Claims_ETL", "Reference_Sync", "Master_Claims_ETL"],
            "Status": ["Succeeded", "Succeeded", "Failed", "Succeeded"],
            "Duration": ["22m", "25m", "4m", "21m"]
        })
        st.table(runs)

# --- 2. PIPELINE MONITORING ---
elif menu == "Pipeline Monitoring":
    st.title("⚙️ Pipeline Run Monitoring")
    
    st.markdown("### ADF Execution Timeline")
    # Simulation of ADF runs
    df_runs = pd.DataFrame([
        dict(Task="Bronze Ingest", Start='2024-05-16 01:00', Finish='2024-05-16 01:10', Resource="Databricks"),
        dict(Task="Silver Cleanse", Start='2024-05-16 01:12', Finish='2024-05-16 01:25', Resource="Databricks"),
        dict(Task="Gold Aggs", Start='2024-05-16 01:26', Finish='2024-05-16 01:35', Resource="Databricks"),
        dict(Task="Synapse Sync", Start='2024-05-16 01:36', Finish='2024-05-16 01:45', Resource="ADF Copy"),
    ])
    fig_gantt = px.timeline(df_runs, x_start="Start", x_end="Finish", y="Task", color="Resource")
    st.plotly_chart(fig_gantt, use_container_width=True)

    st.subheader("Failed Claims & Quarantine")
    st.write("Records that failed validation in the Silver layer.")
    q_data = get_quarantine_data()
    st.dataframe(q_data, use_container_width=True)
    
    if st.button("Replay Quarantine Batch"):
        st.toast("Simulation: Triggering ADF Pipeline `Retry_Quarantine_Records`...")
        st.success("Job triggered. Tracking ID: REPLAY-9923")

# --- 3. DATA QUALITY & RECON ---
elif menu == "Data Quality & Recon":
    st.title("📊 Data Quality & Reconciliation")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Source vs Target Reconciliation")
        recon = pd.DataFrame({
            "Layer": ["Source (Files)", "Bronze (Delta)", "Silver (Delta)", "Gold (Fact)", "Synapse (SQL)"],
            "Record Count": [12450, 12450, 12398, 12398, 12398],
            "Status": ["✅", "✅", "⚠️ (52 Quarantined)", "✅", "✅"]
        })
        st.table(recon)
    
    with col2:
        st.markdown("#### Null Validation (Silver)")
        nulls = pd.DataFrame({
            "Column": ["claim_id", "member_id", "provider_id", "claim_date", "diagnosis_code"],
            "Null Rate": [0.0, 0.02, 0.01, 0.0, 0.15]
        })
        fig_nulls = px.bar(nulls, x="Column", y="Null Rate", title="Missing Data %")
        st.plotly_chart(fig_nulls, use_container_width=True)

# --- 4. MEDALLION EXPLORER ---
elif menu == "Medallion Explorer":
    st.title("💎 Medallion Layer Explorer")
    
    tab1, tab2, tab3 = st.tabs(["Raw / Bronze", "Silver (Cleaned)", "Gold (KPIs)"])
    
    with tab1:
        st.markdown("**Bronze:** Schema-on-read AutoLoader landing.")
        st.code("""SELECT * FROM bronze.claims LIMIT 5""", language="sql")
        st.caption("Latest Batch Metadata: `_source_file`: claims_20240516.csv | `_ingest_ts`: 2024-05-16 01:05:22")
    
    with tab2:
        st.markdown("**Silver:** Type casting, null handling, and deduplication.")
        sample_silver = pd.DataFrame({
            "claim_id": ["C1", "C2", "C3"],
            "amount": [1200.50, 450.00, 3200.00],
            "status": ["PAID", "DENIED", "PENDING"],
            "provider_npi": ["1234567890", "0987654321", "1122334455"]
        })
        st.dataframe(sample_silver)
    
    with tab3:
        st.markdown("**Gold:** Business-level aggregations.")
        fig_kpi = px.pie(values=[75, 15, 10], names=["Paid", "Rejected", "Pending"], title="Claims Distribution")
        st.plotly_chart(fig_kpi)

# --- 5. ARCHITECTURE ---
elif menu == "Architecture":
    st.title("🏗️ Platform Architecture")
    
    st.image("https://raw.githubusercontent.com/MicrosoftDocs/azure-docs/master/articles/architecture/solution-ideas/media/modern-data-warehouse.png", caption="Conceptual Azure Data Platform Flow")
    
    st.markdown("""
    ### Tech Stack
    - **Orchestration:** Azure Data Factory (ADF)
    - **Compute:** Azure Databricks (Spark 3.4, Delta Lake)
    - **Storage:** Azure Data Lake Storage (ADLS Gen2)
    - **Warehouse:** Azure Synapse Analytics (Dedicated SQL Pool)
    - **Monitoring:** Streamlit (this portal) & Log Analytics
    
    ### Key Engineering Patterns
    - **Incremental Loading:** Watermark-based logic in `pipeline_control`.
    - **Quarantine:** Automatic routing of bad records to a separate Delta path.
    - **Medallion Design:** Decoupling raw ingestion from business logic.
    - **Schema Evolution:** Using Delta's `mergeSchema` to handle source changes.
    """)

st.sidebar.divider()
st.sidebar.caption("v1.4.2-stable | Build: 2024.05.16.R1")
