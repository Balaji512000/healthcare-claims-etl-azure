# Data Dictionary (Core Tables)

Brief reference for the Synapse tables.

### healthcare.fact_claims
One row per claim. Contains the resolved keys and the final adjudicated status.
- `claim_id`: natural key.
- `patient_sk`: join to `dim_patient`.
- `provider_sk`: join to `dim_provider`.
- `claim_amount`: amount billed.
- `claim_status`: APPROVED / REJECTED / PENDING.

### healthcare.dim_patient
SCD Type 2 member info.
- `is_active`: 1 for the current version.
- `effective_from/to`: tracking policy changes.
- `age_band`: bucketed for reporting.

### healthcare.dim_provider
Master list of doctors/hospitals.
- `network_status`: IN_NETWORK vs OUT_OF_NETWORK (matters for cost analysis).

### metadata.pipeline_audit_log
Tracks every run.
- `input_rows`: how many we found in Bronze.
- `output_rows`: how many made it to Gold.
- `quarantine_rows`: how many were rejected for bad data.
