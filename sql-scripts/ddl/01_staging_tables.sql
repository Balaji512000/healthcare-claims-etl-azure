-- staging tables for synapse load
-- pattern: ADF copy activity fills these → SP merges into dim/fact → truncate
-- keeping these as HEAP / ROUND_ROBIN — no point indexing a table you truncate every night

CREATE SCHEMA IF NOT EXISTS stg;
GO

CREATE TABLE stg.claims
(
    claim_id            VARCHAR(50),
    member_id           VARCHAR(50),
    provider_id         VARCHAR(50),
    claim_date          DATE,
    admission_date      DATE,
    discharge_date      DATE,
    processing_days     INT,
    claim_amount        DECIMAL(18,2),
    diagnosis_code      VARCHAR(20),
    procedure_code      VARCHAR(20),
    claim_status        VARCHAR(20),
    claim_risk_tier     VARCHAR(20),
    insurance_plan_id   VARCHAR(50),
    _gold_updated_at    DATETIME2
)
WITH (DISTRIBUTION = ROUND_ROBIN, HEAP);
GO

CREATE TABLE stg.members
(
    member_id           VARCHAR(50),
    member_name         VARCHAR(100),
    gender              CHAR(1),
    date_of_birth       DATE,
    insurance_plan_id   VARCHAR(50),
    policy_start_date   DATE,
    policy_end_date     DATE,
    state               VARCHAR(50)
)
WITH (DISTRIBUTION = ROUND_ROBIN, HEAP);
GO

-- provider feed occasionally sends blank npi_number — VARCHAR handles that fine
CREATE TABLE stg.providers
(
    provider_id         VARCHAR(50),
    provider_name       VARCHAR(100),
    npi_number          VARCHAR(20),
    specialization      VARCHAR(100),
    hospital_name       VARCHAR(100),
    city                VARCHAR(50),
    state               VARCHAR(50),
    network_status      VARCHAR(20)
)
WITH (DISTRIBUTION = ROUND_ROBIN, HEAP);
GO
