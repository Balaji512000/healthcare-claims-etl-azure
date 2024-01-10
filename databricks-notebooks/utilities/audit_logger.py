# Databricks notebook source
# Basic event logging to the metadata table. 
# Used by ADF to stamp start/end times and row counts for the ops dashboard.

from pyspark.sql.functions import current_timestamp, lit

def log_event(job_run_id, pipeline_name, layer, status, input_rows=0, output_rows=0, quarantine_rows=0, error_message=None):
    audit_df = spark.createDataFrame([(
        job_run_id,
        pipeline_name,
        layer,
        status,
        input_rows,
        output_rows,
        quarantine_rows,
        error_message
    )], ["job_run_id", "pipeline_name", "layer", "status", "input_rows", "output_rows", "quarantine_rows", "error_message"])

    audit_df = audit_df.withColumn("event_timestamp", current_timestamp())

    # Appending to the central metadata table. 
    # TODO: this needs an index in Synapse once we reach >10k runs.
    (
        audit_df.write
        .format("delta")
        .mode("append")
        .save("abfss://metadata@datalake.dfs.core.windows.net/pipeline_audit_log/")
    )
