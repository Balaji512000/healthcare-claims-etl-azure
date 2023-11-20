-- DW tables — Synapse Dedicated SQL Pool
-- fact_claims: HASH on patient_sk. Most analytical queries are member-centric
--              so hash here cuts cross-node shuffle on the most common joins.
-- dimensions: REPLICATED — all small enough that broadcasting always wins.
--
-- Note: dim_date is pre-populated via SP_Populate_Dim_Date (run once at setup).
-- Don't truncate it — nobody wants to regenerate 25 years of calendar rows.

CREATE SCHEMA IF NOT EXISTS healthcare;
GO
CREATE SCHEMA IF NOT EXISTS metadata;
GO

-- --------------------------------------------------------
-- dim_patient
-- SCD Type 2. New row on plan change or state change.
-- --------------------------------------------------------
CREATE TABLE healthcare.dim_patient
(
    patient_sk          INT             NOT NULL,
    member_id           VARCHAR(50)     NOT NULL,
    member_name         VARCHAR(100),
    gender              CHAR(1),
    date_of_birth       DATE,
    age_band            VARCHAR(20),            -- derived: Under 18 / 18-35 / 36-55 / 55+
    state               VARCHAR(50),
    insurance_plan_id   VARCHAR(50),
    policy_start_date   DATE,
    policy_end_date     DATE,
    is_active           BIT             DEFAULT 1,
    effective_from      DATE,
    effective_to        DATE,
    _dw_inserted_at     DATETIME2       DEFAULT GETDATE()
)
WITH (DISTRIBUTION = REPLICATE, CLUSTERED COLUMNSTORE INDEX);
GO

-- --------------------------------------------------------
-- dim_provider
-- Type 1 mostly — provider attributes rarely change.
-- network_status changes do get tracked via effective dates
-- because they affect adjudication rules.
-- --------------------------------------------------------
CREATE TABLE healthcare.dim_provider
(
    provider_sk         INT             NOT NULL,
    provider_id         VARCHAR(50)     NOT NULL,
    provider_name       VARCHAR(100),
    npi_number          VARCHAR(20),
    specialization      VARCHAR(100),
    hospital_name       VARCHAR(100),
    city                VARCHAR(50),
    state               VARCHAR(50),
    network_status      VARCHAR(20),    -- IN_NETWORK | OUT_OF_NETWORK
    is_active           BIT             DEFAULT 1,
    effective_from      DATE,
    effective_to        DATE,
    _dw_inserted_at     DATETIME2       DEFAULT GETDATE()
)
WITH (DISTRIBUTION = REPLICATE, CLUSTERED COLUMNSTORE INDEX);
GO

-- --------------------------------------------------------
-- dim_insurance_plan
-- Updated quarterly when plan catalog changes.
-- --------------------------------------------------------
CREATE TABLE healthcare.dim_insurance_plan
(
    plan_sk             INT             NOT NULL,
    plan_id             VARCHAR(50)     NOT NULL,
    plan_name           VARCHAR(100),
    plan_type           VARCHAR(50),    -- HMO, PPO, EPO, HDHP
    deductible_amount   DECIMAL(10,2),
    oop_max             DECIMAL(10,2),
    is_active           BIT             DEFAULT 1,
    _dw_inserted_at     DATETIME2       DEFAULT GETDATE()
)
WITH (DISTRIBUTION = REPLICATE, CLUSTERED COLUMNSTORE INDEX);
GO

-- dim_date: pre-seeded 2010–2035, no ETL dependency
CREATE TABLE healthcare.dim_date
(
    date_sk             INT             NOT NULL,   -- YYYYMMDD
    full_date           DATE,
    calendar_year       SMALLINT,
    calendar_month      TINYINT,
    month_name          VARCHAR(10),
    calendar_quarter    TINYINT,
    day_of_month        TINYINT,
    day_of_week         TINYINT,
    day_name            VARCHAR(10),
    is_weekend          BIT,
    is_holiday          BIT,
    fiscal_year         SMALLINT,
    fiscal_quarter      TINYINT
)
WITH (DISTRIBUTION = REPLICATE, CLUSTERED COLUMNSTORE INDEX);
GO

-- --------------------------------------------------------
-- fact_claims
-- Grain: one row per claim submission (latest version).
-- HASH on patient_sk — member history queries dominate.
-- --------------------------------------------------------
CREATE TABLE healthcare.fact_claims
(
    claim_sk            BIGINT          NOT NULL,
    claim_id            VARCHAR(50)     NOT NULL,
    patient_sk          INT             NOT NULL,   -- -1 if member not resolved
    provider_sk         INT             NOT NULL,   -- -1 if provider not resolved
    plan_sk             INT             NOT NULL,
    claim_date_sk       INT             NOT NULL,
    admission_date_sk   INT,
    discharge_date_sk   INT,
    diagnosis_code      VARCHAR(20),
    procedure_code      VARCHAR(20),
    claim_amount        DECIMAL(18,2),
    approved_amount     DECIMAL(18,2),
    patient_liability   DECIMAL(18,2),
    claim_status        VARCHAR(20),
    claim_risk_tier     VARCHAR(20),
    processing_days     INT,
    _dw_inserted_at     DATETIME2       DEFAULT GETDATE(),
    _source_updated_at  DATETIME2
)
WITH (DISTRIBUTION = HASH(patient_sk), CLUSTERED COLUMNSTORE INDEX);
GO

-- audit log — round robin, append only
CREATE TABLE metadata.pipeline_audit_log
(
    audit_id            BIGINT          IDENTITY(1,1),
    job_run_id          VARCHAR(100),
    pipeline_name       VARCHAR(100),
    layer               VARCHAR(20),
    status              VARCHAR(20),    -- STARTED | COMPLETED | FAILED | SKIPPED
    input_rows          BIGINT,
    output_rows         BIGINT,
    quarantine_rows     BIGINT,
    error_message       NVARCHAR(MAX),
    event_timestamp     DATETIME2       DEFAULT GETDATE()
)
WITH (DISTRIBUTION = ROUND_ROBIN, CLUSTERED COLUMNSTORE INDEX);
GO
