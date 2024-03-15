# Azure Setup Notes

Mostly provisioned via the portal, but here are the core resource names and CLI snippets.

### Storage
- Account: `stdatalakedev001` (Standard LRS)
- Containers: `raw`, `bronze`, `silver`, `gold`, `quarantine`, `metadata`

### Compute
- Databricks: `dbw-health-dev-001`
- Cluster: 13.3 LTS, DS3_v2 nodes. 
- Mounts: Run `databricks-notebooks/utilities/mount_adls.py` once the SP is setup in IAM.

### Database
- Synapse: `syn-health-dev-001`
- SQL Pool: `sqlpool-dev` (DW100c is enough for dev).
- Remember to grant the ADF managed identity `Contributor` access to the Synapse workspace.

### Key Vault
- `kv-health-dev-001`
- Secrets needed: `storage-key`, `sp-client-id`, `sp-client-secret`, `tenant-id`.
