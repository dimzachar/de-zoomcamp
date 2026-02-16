with source as (
    select * from {{ source('raw', 'fhv_tripdata') }}
),

renamed as (
    select
        -- identifiers
        cast(dispatching_base_num AS STRING) AS dispatching_base_num,

        -- timestamps
        cast(pickup_datetime AS TIMESTAMP) AS pickup_datetime,
        cast(dropOff_datetime AS TIMESTAMP) AS dropoff_datetime,

        -- location IDs
        cast(PUlocationID AS INTEGER) AS pickup_location_id,
        cast(DOlocationID AS INTEGER) AS dropoff_location_id,

        -- trip info
        cast(SR_Flag AS STRING) AS sr_flag,
        cast(Affiliated_base_number AS STRING) AS affiliated_base_number
    from source
    -- Filter out records with null dispatching_base_num (data quality requirement)
    where dispatching_base_num is not null
)

select * from renamed