-- Ad-hoc recon scripts for morning checks
-- --------------------------------------------------------

-- Check if Gold counts match Synapse
SELECT 'gold_delta', COUNT(*) FROM OPENROWSET(BULK 'https://datalake.dfs.core.windows.net/gold/fact_claims/', FORMAT = 'DELTA') AS g
UNION ALL
SELECT 'synapse_fact', COUNT(*) FROM healthcare.fact_claims;


-- Are we missing keys? (-1 means we couldn't find the member/provider during the load)
SELECT patient_sk, COUNT(*) FROM healthcare.fact_claims GROUP BY patient_sk HAVING patient_sk = -1;


-- Recent audit log
SELECT TOP 10 * FROM metadata.pipeline_audit_log ORDER BY event_timestamp DESC;


-- Outlier check (> 3 std devs)
WITH s AS (SELECT AVG(claim_amount) AS a, STDEV(claim_amount) AS sd FROM healthcare.fact_claims)
SELECT claim_id, claim_amount FROM healthcare.fact_claims, s WHERE claim_amount > (a + (3 * sd));
