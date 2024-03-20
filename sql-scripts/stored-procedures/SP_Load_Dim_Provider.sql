-- dim_provider Type 1 load.
-- Most provider info just overwrites. network_status is the only thing we actually track via effective dates.

CREATE OR ALTER PROCEDURE healthcare.SP_Load_Dim_Provider
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @load_ts DATETIME2 = GETDATE();

    -- Sync existing
    UPDATE tgt
    SET
        tgt.provider_name   = src.provider_name,
        tgt.npi_number      = src.npi_number,
        tgt.specialization  = src.specialization,
        tgt.hospital_name   = src.hospital_name,
        tgt.city                = src.city,
        tgt.state               = src.state,
        tgt.network_status  = src.network_status,
        tgt.effective_from  = CASE WHEN tgt.network_status <> src.network_status THEN CAST(@load_ts AS DATE) ELSE tgt.effective_from END,
        tgt._dw_inserted_at = @load_ts
    FROM healthcare.dim_provider tgt
    INNER JOIN stg.providers src ON tgt.provider_id = src.provider_id
    WHERE tgt.is_active = 1;

    -- New
    INSERT INTO healthcare.dim_provider
    (
        provider_id, provider_name, npi_number, specialization,
        hospital_name, city, state, network_status,
        is_active, effective_from, effective_to, _dw_inserted_at
    )
    SELECT
        src.provider_id, src.provider_name, src.npi_number, src.specialization,
        src.hospital_name, src.city, src.state, src.network_status,
        1, CAST(@load_ts AS DATE), NULL, @load_ts
    FROM stg.providers src
    LEFT JOIN healthcare.dim_provider tgt ON tgt.provider_id = src.provider_id
    WHERE tgt.provider_id IS NULL;

    TRUNCATE TABLE stg.providers;
END;
GO
