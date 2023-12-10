# Databricks notebook source
# Fact rebuild and KPI refresh. 
# Full overwrite on fact_claims for now (~2M rows), will switch to MERGE if volume spikes.

from pyspark.sql import functions as F
from delta.tables import DeltaTable

dbutils.widgets.text("silver_claims_path",    "abfss://silver@datalake.dfs.core.windows.net/claims/")
dbutils.widgets.text("silver_members_path",   "abfss://silver@datalake.dfs.core.windows.net/members/")
dbutils.widgets.text("silver_providers_path", "abfss://silver@datalake.dfs.core.windows.net/providers/")
dbutils.widgets.text("gold_fact_path",        "abfss://gold@datalake.dfs.core.windows.net/fact_claims/")
dbutils.widgets.text("gold_kpi_path",         "abfss://gold@datalake.dfs.core.windows.net/provider_kpi/")

df_claims    = spark.read.format("delta").load(dbutils.widgets.get("silver_claims_path"))
# Broadcasting small dims to skip shuffle
df_members   = F.broadcast(spark.read.format("delta").load(dbutils.widgets.get("silver_members_path")).select("member_id", "member_sk", "insurance_plan_id"))
df_providers = F.broadcast(spark.read.format("delta").load(dbutils.widgets.get("silver_providers_path")).select("provider_id", "provider_sk", "specialization", "state"))

df_fact = (
    df_claims
    .join(df_members,   on="member_id",   how="left")
    .join(df_providers, on="provider_id", how="left")
    .withColumn("processing_days", F.datediff(F.col("discharge_date"), F.col("admission_date")))
    .withColumn("claim_risk_tier",
        F.when(F.col("claim_amount") > 50_000, "Critical")
         .when(F.col("claim_amount") > 10_000, "High")
         .when(F.col("claim_amount") >  5_000, "Medium")
         .otherwise("Low"))
    .withColumn("claim_year",  F.year("claim_date"))
    .withColumn("claim_month", F.month("claim_date"))
    .withColumn("_gold_updated_at", F.current_timestamp())
    .select(
        "claim_id", "member_sk", "provider_sk", "claim_date", "claim_year", "claim_month",
        "admission_date", "discharge_date", "processing_days", "claim_amount",
        "diagnosis_code", "procedure_code", "claim_status", "claim_risk_tier",
        "insurance_plan_id", "_gold_updated_at"
    )
)

df_fact.write.format("delta").mode("overwrite").partitionBy("claim_year", "claim_month").save(dbutils.widgets.get("gold_fact_path"))

# Provider KPI - ops uses this directly in the Power BI "Deep Dive" report. 
df_kpi = (
    df_fact.groupBy("provider_sk", "provider_id", "state", "specialization")
    .agg(
        F.count("claim_id").alias("total_claims"),
        F.round(F.sum("claim_amount"), 2).alias("total_billed"),
        F.round(F.avg("claim_amount"), 2).alias("avg_claim_amount"),
        F.round(F.avg("processing_days"), 1).alias("avg_processing_days"),
        F.sum(F.when(F.col("claim_status") == "REJECTED", 1).otherwise(0)).alias("rejected_claims")
    )
    .withColumn("rejection_rate_pct", F.round(F.col("rejected_claims") / F.col("total_claims") * 100, 2))
    .withColumn("last_refreshed", F.current_timestamp())
)

kpi_path = dbutils.widgets.get("gold_kpi_path")
if DeltaTable.isDeltaTable(spark, kpi_path):
    (
        DeltaTable.forPath(spark, kpi_path).alias("tgt")
        .merge(df_kpi.alias("src"), "tgt.provider_sk = src.provider_sk")
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )
else:
    df_kpi.write.format("delta").mode("overwrite").save(kpi_path)
