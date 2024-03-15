# Pipeline Execution Flow

High-level summary of how the nightly batch runs.

1. **Trigger:** 01:00 UTC schedule on `PL_Master_Orchestration`.
2. **Bronze Ingest:** 
   - `PL_Ingest_Raw_To_Bronze` looks for files in `raw/claims`.
   - If found, fires the Databricks AutoLoader job.
   - Appends everything to `bronze.claims`.
3. **Silver Process:**
   - Reads incrementally using the watermark.
   - Cleans types, normalizes status, and quarentines bad IDs.
   - MERGE into `silver.claims`.
4. **Gold Agg:**
   - Full rebuild of `fact_claims` from Silver.
   - Incremental MERGE into `provider_kpi`.
5. **Warehouse Sync:**
   - Copy activity pulls Gold Delta to Synapse `stg` tables.
   - Stored procs handle the final move into `healthcare` schema.
6. **Watermark Update:**
   - Only happens if the full sequence completes. This ensures we don't miss records if a mid-stage fails.

### Troubleshooting
If the watermark is stuck, you can manually override it in the `metadata.pipeline_control` table in the SQL DB.
