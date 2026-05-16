# Operational Monitoring Dashboard

Internal portal for monitoring the Healthcare Claims ETL pipeline. 

## Features
- **Pipeline Overview:** Real-time metrics on ingestion volume and success rates.
- **Data Quality:** Reconciliation checks between source, Delta layers, and Synapse.
- **Quarantine Explorer:** View and retry records that failed validation.
- **Architecture Flow:** Visual representation of the Azure stack.

## Local Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the dashboard:
   ```bash
   streamlit run app.py
   ```

## Production Deployment
This dashboard is designed to run as an Azure App Service or within a containerized environment (AKS/ACI) with managed identity access to the underlying Delta tables (via Databricks SQL Warehouse or Synapse).
