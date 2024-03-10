-- dim_patient SCD Type 2 load.
-- Closes out old versions for members where plan/state changed, then inserts fresh rows.

CREATE OR ALTER PROCEDURE healthcare.SP_Load_Dim_Patient
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @load_ts DATETIME2 = GETDATE();

    -- Expire active rows where source data has changed.
    -- Currently only tracking plan and state changes. End date change also triggers a new row.
    UPDATE tgt
    SET
        tgt.is_active    = 0,
        tgt.effective_to = CAST(@load_ts AS DATE)
    FROM healthcare.dim_patient tgt
    INNER JOIN stg.members src ON tgt.member_id = src.member_id AND tgt.is_active = 1
    WHERE
        tgt.insurance_plan_id <> src.insurance_plan_id
        OR tgt.state          <> src.state
        OR tgt.policy_end_date <> src.policy_end_date;

    -- New active rows (brand new members + the ones we just expired)
    INSERT INTO healthcare.dim_patient
    (
        member_id, member_name, gender, date_of_birth,
        age_band, state, insurance_plan_id,
        policy_start_date, policy_end_date,
        is_active, effective_from, effective_to, _dw_inserted_at
    )
    SELECT
        src.member_id, src.member_name, src.gender, src.date_of_birth,
        -- age_band hack for the actuarial reports
        CASE
            WHEN DATEDIFF(YEAR, src.date_of_birth, GETDATE()) < 18  THEN 'Under 18'
            WHEN DATEDIFF(YEAR, src.date_of_birth, GETDATE()) < 36  THEN '18-35'
            WHEN DATEDIFF(YEAR, src.date_of_birth, GETDATE()) < 56  THEN '36-55'
            ELSE '55+'
        END,
        src.state, src.insurance_plan_id, src.policy_start_date, src.policy_end_date,
        1, CAST(@load_ts AS DATE), NULL, @load_ts
    FROM stg.members src
    LEFT JOIN healthcare.dim_patient tgt ON tgt.member_id = src.member_id AND tgt.is_active = 1
    WHERE tgt.member_id IS NULL;

    TRUNCATE TABLE stg.members;
END;
GO
