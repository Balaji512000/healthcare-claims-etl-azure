# Databricks notebook source
# Mount ADLS containers. Run once per cluster/workspace.
# Uses service principal credentials from the 'healthcare-kv-scope' secret scope.

def mount_container(container: str, storage_account: str, scope: str):
    mount_point = f"/mnt/{container}"
    if any(m.mountPoint == mount_point for m in dbutils.fs.mounts()):
        print(f"Skipping {mount_point}, already mounted.")
        return

    configs = {
        "fs.azure.account.auth.type": "OAuth",
        "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
        "fs.azure.account.oauth2.client.id":     dbutils.secrets.get(scope=scope, key="sp-client-id"),
        "fs.azure.account.oauth2.client.secret": dbutils.secrets.get(scope=scope, key="sp-client-secret"),
        "fs.azure.account.oauth2.client.endpoint": f"https://login.microsoftonline.com/{dbutils.secrets.get(scope=scope, key='tenant-id')}/oauth2/token"
    }

    dbutils.fs.mount(
        source=f"abfss://{container}@{storage_account}.dfs.core.windows.net/",
        mount_point=mount_point,
        extra_configs=configs
    )
    print(f"Mounted: {mount_point}")

# Defaults for dev.
STORAGE_ACCOUNT = "stdatalakedev001"
SECRET_SCOPE    = "healthcare-kv-scope"
containers      = ["raw", "bronze", "silver", "gold", "quarantine", "metadata"]

for c in containers:
    mount_container(c, STORAGE_ACCOUNT, SECRET_SCOPE)
