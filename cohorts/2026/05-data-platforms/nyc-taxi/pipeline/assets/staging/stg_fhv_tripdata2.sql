/* @bruin
name: staging.stg_fhv_tripdata2
type: duckdb.sql

depends:
  - ingestion.trips2

materialization:
  type: table
@bruin */

-- Staging for FHV (for-hire vehicle) data from trips2
SELECT
    -- identifiers
    CAST(dispatching_base_num AS VARCHAR) AS dispatching_base_num,

    -- timestamps
    CAST(pickup_datetime AS TIMESTAMP) AS pickup_datetime,
    CAST(drop_off_datetime AS TIMESTAMP) AS dropoff_datetime,

    -- location IDs
    CAST(p_ulocation_id AS INTEGER) AS pickup_location_id,
    CAST(d_olocation_id AS INTEGER) AS dropoff_location_id,

    -- trip info
    CAST(sr_flag AS VARCHAR) AS sr_flag,
    CAST(affiliated_base_number AS VARCHAR) AS affiliated_base_number

FROM ingestion.trips2
WHERE taxi_type = 'fhv'
    AND dispatching_base_num IS NOT NULL;
