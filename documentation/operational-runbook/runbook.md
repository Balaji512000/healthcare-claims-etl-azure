# ETL Runbook

Notes for the on-call engineer.

### Schedule
Nightly batch starts at 01:00 UTC. Usually finishes by 02:00.

### Failing Batches
1. **Source file missing:** Check the landing zone. If `raw/claims/` is empty, contact the billing ops team. The pipeline skips automatically but we need the files for daily reporting.
2. **Databricks timeout:** Usually a cluster startup issue. Restart the cluster manually if it's stuck in "Pending".
3. **Synapse connectivity:** Check if the pool is paused. Resuming it usually clears the error.

### Re-runs
To re-process a day's data:
1. Delete the bad rows from the Silver table for that date.
2. Set `last_watermark` in `metadata.pipeline_control` to the start of the target day.
3. Trigger `PL_Master_Orchestration`.

### Monitoring
Check the `metadata.pipeline_audit_log` in Synapse for row count discrepancies. If `quarantine_rows` is > 5% of `input_rows`, we likely have a schema change from the source that hasn't been mapped yet.
