# Changelog

## 2024-03-18
- Switched to AutoLoader for Bronze. Batch reads were timing out as the container got bigger.
- Added `_source_file` to Bronze to help trace back bad rows to the source ZIP.
- Fix: `vw_provider_performance` was miscalculating rejection rates for new providers.

## 2024-02-05
- Added watermark-based incremental loading. 
- Quarantine layer for malformed claim IDs.
- SCD Type 2 for member data.

## 2023-12-10
- Initial pipeline (raw-to-warehouse).
- Synapse DDL and stored procs.
- Data generator for testing.
