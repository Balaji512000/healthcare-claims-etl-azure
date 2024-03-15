-- Presentation views for Power BI
-- --------------------------------------------------------

-- Monthly summary for the main executive dashboard
CREATE OR ALTER VIEW healthcare.vw_monthly_claims_summary AS
SELECT
    d.calendar_year,
    d.calendar_month,
    d.month_name,
    fc.claim_status,
    COUNT(fc.claim_id)      AS total_claims,
    SUM(fc.claim_amount)    AS billed_amt,
    AVG(fc.processing_days) AS avg_turnaround
FROM healthcare.fact_claims fc
JOIN healthcare.dim_date d ON d.date_sk = fc.claim_date_sk
GROUP BY
    d.calendar_year, d.calendar_month, d.month_name, fc.claim_status;
GO


-- Deep dive into provider performance (rejection rates are a key KPI)
CREATE OR ALTER VIEW healthcare.vw_provider_performance AS
SELECT
    dpr.provider_id,
    dpr.provider_name,
    dpr.specialization,
    dpr.state,
    COUNT(fc.claim_id) AS total_claims,
    SUM(fc.claim_amount) AS total_billed,
    SUM(CASE WHEN fc.claim_status = 'REJECTED' THEN 1 ELSE 0 END) AS rejections,
    ROUND(
        100.0 * SUM(CASE WHEN fc.claim_status = 'REJECTED' THEN 1 ELSE 0 END) / NULLIF(COUNT(fc.claim_id), 0), 
        2
    ) AS rejection_rate_pct
FROM healthcare.fact_claims fc
JOIN healthcare.dim_provider dpr ON dpr.provider_sk = fc.provider_sk AND dpr.is_active = 1
GROUP BY
    dpr.provider_id, dpr.provider_name, dpr.specialization, dpr.state;
GO


-- Detailed claim history for member search/lookup
CREATE OR ALTER VIEW healthcare.vw_patient_claims AS
SELECT
    dp.member_id,
    dp.member_name,
    dp.age_band,
    ip.plan_name,
    fc.claim_id,
    fc.claim_date_sk,
    fc.claim_amount,
    fc.claim_status,
    fc.claim_risk_tier
FROM healthcare.fact_claims fc
JOIN healthcare.dim_patient dp        ON dp.patient_sk = fc.patient_sk AND dp.is_active = 1
JOIN healthcare.dim_insurance_plan ip ON ip.plan_sk    = fc.plan_sk;
GO
