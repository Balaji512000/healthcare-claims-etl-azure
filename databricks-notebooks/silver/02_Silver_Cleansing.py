# Databricks notebook source
# Cleans incremental Bronze records and MERGEs into Silver.
# FIXME: move quarantine threshold to config per #ETL-204

from pyspark.sql import functions as F
from pyspark.sql.window import Window
from delta.tables import DeltaTable

dbutils.widgets.text("bronze_path",     "abfss://bronze@datalake.dfs.core.windows.net/claims/")
dbutils.widgets.text("silver_path",     "abfss://silver@datalake.dfs.core.windows.net/claims/")
dbutils.widgets.text("quarantine_path", "abfss://quarantine@datalake.dfs.core.windows.net/claims/")
dbutils.widgets.text("watermark_ts",    "1970-01-01 00:00:00")
dbutils.widgets.text("job_run_id",      "manual")

bronze_path     = dbutils.widgets.get("bronze_path")
silver_path     = dbutils.widgets.get("silver_path")
quarantine_path = dbutils.widgets.get("quarantine_path")
watermark_ts    = dbutils.widgets.get("watermark_ts")
job_run_id      = dbutils.widgets.get("job_run_id")

df_bronze = (
    spark.read.format("delta").load(bronze_path)
    .filter(F.col("_ingestion_ts") > F.lit(watermark_ts).cast("timestamp"))
)

if df_bronze.count() == 0:
    dbutils.notebook.exit("NO_NEW_DATA")

# Cast types and normalize. 
# billing partners occasionally send mixed date formats (MM/DD/YYYY vs ISO) — to_date handles most cases.
df_typed = (
    df_bronze
    .withColumn("claim_amount",   F.col("claim_amount").cast("double"))
    .withColumn("claim_date",     F.to_date(F.col("claim_date")))
    .withColumn("admission_date", F.to_date(F.col("admission_date")))
    .withColumn("discharge_date", F.to_date(F.col("discharge_date")))
    .withColumn("claim_status",   F.upper(F.trim(F.col("claim_status"))))
    .withColumn("diagnosis_code", F.upper(F.trim(F.col("diagnosis_code"))))
    .withColumn("procedure_code", F.upper(F.trim(F.col("procedure_code"))))
)

# Routing bad rows to quarantine. 
# Future-dated claims are usually a source timezone issue but we flag them for review.
valid_mask = (
    F.col("claim_id").isNotNull()
    & (F.col("claim_amount") >= 0)
    & F.col("claim_date").isNotNull()
    & (F.col("claim_date") <= F.current_date())
)

df_bad = (
    df_typed.filter(~valid_mask)
    .withColumn("_reject_reason", 
        F.when(F.col("claim_id").isNull(),            "null_claim_id")
         .when(F.col("claim_amount") < 0,             "negative_amount")
         .when(F.col("claim_date") > F.current_date(), "future_claim_date")
         .otherwise("unknown"))
    .withColumn("_quarantine_ts", F.current_timestamp())
    .withColumn("_job_run_id", F.lit(job_run_id))
)

if df_bad.count() > 0:
    df_bad.write.format("delta").mode("append").save(quarantine_path)

# Dedup within the batch. SFTP job upstream occasionally resends full files on failure.
window = Window.partitionBy("claim_id").orderBy(F.desc("_ingestion_ts"))
df_clean = (
    df_typed.filter(valid_mask)
    .withColumn("_rn", F.row_number().over(window))
    .filter(F.col("_rn") == 1)
    .drop("_rn")
    .withColumn("_silver_updated_at", F.current_timestamp())
)

if DeltaTable.isDeltaTable(spark, silver_path):
    (
        DeltaTable.forPath(spark, silver_path).alias("tgt")
        .merge(df_clean.alias("src"), "tgt.claim_id = src.claim_id")
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )
else:
    df_clean.write.format("delta").mode("overwrite").partitionBy("claim_status").save(silver_path)

# FIXME: Z-order runs on every run, should probably gate this for small batches
spark.sql(f"OPTIMIZE delta.`{silver_path}` ZORDER BY (member_id, provider_id)")
