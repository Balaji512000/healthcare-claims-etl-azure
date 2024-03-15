# Power BI Notes

A few pointers for the BI folks building the dashboards.

### Connection
- **Mode:** DirectQuery.
- **Server:** `syn-health-dev-001.sql.azuresynapse.net` (parameterize this!).
- **Database:** `sqlpool-dev`.

### Main Views
- `healthcare.vw_monthly_claims_summary`: Top-level trends.
- `healthcare.vw_provider_performance`: The main table for the provider deep-dive. 
- `healthcare.vw_patient_claims`: For the member search page.

### Key Metrics to include
- **Rejection Rate:** Use the pre-calculated `rejection_rate_pct` from the provider view. 
- **Turnaround Time:** `avg_turnaround` in the monthly view.
- **Claim Risk:** Use the `claim_risk_tier` column to bucket dollar amounts.

### TODO / Wishlist
- Add a "Time Travel" toggle to compare last month's stats vs this month's (Delta Lake history could help here).
- Map view for claims by provider state.
