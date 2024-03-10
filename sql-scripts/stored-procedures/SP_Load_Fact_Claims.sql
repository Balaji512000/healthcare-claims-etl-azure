-- fact_claims load via delete-insert. 
-- Using this instead of MERGE because Synapse performance on massive MERGEs is inconsistent.

CREATE OR ALTER PROCEDURE healthcare.SP_Load_Fact_Claims
AS
BEGIN
    SET NOCOUNT ON;

    -- Clear existing rows for the claims we're processing (idempotency)
    DELETE fc FROM healthcare.fact_claims fc INNER JOIN stg.claims src ON fc.claim_id = src.claim_id;

    -- Push resolved rows. Default to -1 if dim lookups fail.
    INSERT INTO healthcare.fact_claims
    (
        claim_id, patient_sk, provider_sk, plan_sk,
        claim_date_sk, admission_date_sk, discharge_date_sk,
        diagnosis_code, procedure_code, claim_amount, 
        claim_status, claim_risk_tier, processing_days, _source_updated_at
    )
    SELECT
        src.claim_id,
        ISNULL(dp.patient_sk,  -1),
        ISNULL(dpr.provider_sk, -1),
        ISNULL(dip.plan_sk,    -1),
        CONVERT(INT, FORMAT(src.claim_date,     'yyyyMMdd')),
        CONVERT(INT, FORMAT(src.admission_date, 'yyyyMMdd')),
        CONVERT(INT, FORMAT(src.discharge_date, 'yyyyMMdd')),
        src.diagnosis_code, src.procedure_code, src.claim_amount,
        src.claim_status, src.claim_risk_tier, src.processing_days, src._gold_updated_at
    FROM stg.claims src
    LEFT JOIN healthcare.dim_patient      dp  ON dp.member_id   = src.member_id   AND dp.is_active  = 1
    LEFT JOIN healthcare.dim_provider     dpr ON dpr.provider_id = src.provider_id AND dpr.is_active = 1
    LEFT JOIN healthcare.dim_insurance_plan dip ON dip.plan_id  = src.insurance_plan_id AND dip.is_active = 1;

    TRUNCATE TABLE stg.claims;
END;
GO
