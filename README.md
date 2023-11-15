# Healthcare Claims ETL

Batch pipeline for processing insurance claims on Azure. 

Raw files (CSV) land in ADLS, processed through Bronze/Silver/Gold layers in Databricks, and synced to a Synapse SQL Pool for Power BI.

This repo represents the evolution of our claim processing engine over the last ~4 months, moving from basic batch scripts to an incremental Medallion flow.

## Pipeline Flow

1. **Bronze:** AutoLoader reads from `raw/` and appends to Delta. Immutable ledger.
2. **Silver:** Incremental load using watermarks. Cleans types, handles basic dedup, and quarentines bad rows (null IDs, etc).
3. **Gold:** Rebuilds facts and refreshes provider KPIs. 
4. **Synapse:** ADF Copy activity pushes Gold to the warehouse for DirectQuery reporting.

## Incremental Strategy
We use a `pipeline_control` table in Azure SQL to track the `last_watermark` for the claims feed. Each run only picks up records newer than that timestamp. If a run fails, the watermark isn't bumped, so the next run re-processes the batch.

## Running locally / testing
- `utilities/generate_datasets.py` creates sample CSVs for testing.
- DDL scripts are in `sql-scripts/ddl/`. Run these first if setting up a new Synapse pool.
- Cluster configs and workspace paths are in `configs/`.

## Common Tasks
- **Forcing a full reload:** Reset the watermark to `1970-01-01` in the control table and re-trigger the master pipeline.
- **Checking for errors:** Query the `metadata.pipeline_audit_log` table in Synapse or check the `quarantine/` container in ADLS.

## Known Limitations / Operational Notes
- **SFTP Timing:** We currently rely on a scheduled trigger (01:00 UTC). If the source system is late with the claims drop, the pipeline skips. We're looking into Storage Event triggers for the next sprint.
- **SCD Logic:** Member data is Type 2, but Provider data is currently Type 1. If we need historical provider specialty tracking, we'll need to refactor the provider SP.
- **Data Volume:** The Gold layer is a full rebuild. At ~5M rows this is fine, but we'll need to switch to an incremental MERGE once we scale past that.

## Future TODOs
- [ ] Move quarantine logic to a shared library to reduce notebook boilerplate.
- [ ] Add column-level encryption for PII (SSN/Member Names) in the Silver layer.
- [ ] Implement Great Expectations for deeper data quality gating in Silver.
