# Databricks notebook source
# Ingests new claim files from landing zone to Bronze.
# Switched to AutoLoader to handle the growing volume in the raw container.
# Checkpoint stores the state so we don't re-process the same files.

from pyspark.sql.functions import current_timestamp, lit, input_file_name, to_date

dbutils.widgets.text("source_path",     "abfss://raw@datalake.dfs.core.windows.net/claims/")
dbutils.widgets.text("bronze_path",     "abfss://bronze@datalake.dfs.core.windows.net/claims/")
dbutils.widgets.text("checkpoint_path", "abfss://bronze@datalake.dfs.core.windows.net/_checkpoints/claims/")
dbutils.widgets.text("table_name",      "bronze.claims")
dbutils.widgets.text("job_run_id",      "manual")

source_path     = dbutils.widgets.get("source_path")
bronze_path     = dbutils.widgets.get("bronze_path")
checkpoint_path = dbutils.widgets.get("checkpoint_path")
table_name      = dbutils.widgets.get("table_name")
job_run_id      = dbutils.widgets.get("job_run_id")

# mergeSchema is on — source team likes to add columns without notice.
# Better to absorb it than fail at 2am.
df_raw = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "csv")
    .option("cloudFiles.schemaLocation", checkpoint_path + "/schema")
    .option("header", "true")
    .option("inferSchema", "true")
    .option("mergeSchema", "true")
    .load(source_path)
)

df_bronze = (
    df_raw
    .withColumn("_ingestion_ts",  current_timestamp())
    .withColumn("_source_file",   input_file_name())
    .withColumn("_job_run_id",    lit(job_run_id))
    .withColumn("_ingest_date",   to_date(current_timestamp())) # partition key for easier daily compaction
)

# Bronze is immutable. Never overwrite. 
(
    df_bronze.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", checkpoint_path)
    .option("mergeSchema", "true")
    .partitionBy("_ingest_date")
    .trigger(availableNow=True)
    .start(bronze_path)
    .awaitTermination()
)

spark.sql(f"CREATE TABLE IF NOT EXISTS {table_name} USING DELTA LOCATION '{bronze_path}'")

# TODO: wire up the audit logger here
# row_count = spark.read.format("delta").load(bronze_path).count()
