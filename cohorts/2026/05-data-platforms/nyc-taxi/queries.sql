-- Count rows in ingestion.trips
bruin query --connection duckdb-default --query "SELECT COUNT(*) FROM ingestion.trips"

-- Count rows in ingestion.payment_lookup
bruin query --connection duckdb-default --query "SELECT COUNT(*) FROM ingestion.payment_lookup"

-- Count rows in staging.trips
bruin query --connection duckdb-default --query "SELECT COUNT(*) FROM staging.trips"

-- Count rows in reports.trips_report
bruin query --connection duckdb-default --query "SELECT COUNT(*) FROM reports.trips_report"

-- Sample data from ingestion.trips
bruin query --connection duckdb-default --query "SELECT * FROM ingestion.trips LIMIT 10"

-- Check payment types
bruin query --connection duckdb-default --query "SELECT * FROM ingestion.payment_lookup"

-- Check staging data with payment names
bruin query --connection duckdb-default --query "SELECT * FROM staging.trips LIMIT 10"

-- View the final report
bruin query --connection duckdb-default --query "SELECT * FROM reports.trips_report"

-- Check date range in ingestion
bruin query --connection duckdb-default --query "SELECT MIN(pickup_datetime), MAX(pickup_datetime) FROM ingestion.trips"

-- Check taxi types distribution
bruin query --connection duckdb-default --query "SELECT taxi_type, COUNT(*) FROM ingestion.trips GROUP BY taxi_type"

-- Check trips by payment type

bruin query --connection duckdb-default --query "SELECT payment_type_name, COUNT(*) FROM staging.trips GROUP BY payment_type_name"


-- Top pickup location by fare amount

bruin query --connection duckdb-default --query "SELECT pickup_location_id, SUM(fare_amount) as total_revenue FROM staging.trips WHERE taxi_type = 'green' AND EXTRACT(YEAR FROM pickup_datetime) = 2022 GROUP BY pickup_location_id ORDER BY total_revenue DESC LIMIT 1"

-- Monthly revenue by taxi type
bruin query --connection duckdb-default --query "SELECT taxi_type, DATE_TRUNC('month', pickup_datetime) as month, SUM(fare_amount) as monthly_revenue FROM staging.trips GROUP BY taxi_type, DATE_TRUNC('month', pickup_datetime) ORDER BY month, taxi_type"

--  Top 10 routes by trip count
bruin query --connection duckdb-default --query "SELECT pickup_location_id, dropoff_location_id, COUNT(*) as trip_count FROM staging.trips GROUP BY pickup_location_id, dropoff_location_id ORDER BY trip_count DESC LIMIT 10"

-- Revenue by payment type
bruin query --connection duckdb-default --query "SELECT payment_type_name, SUM(fare_amount) as total_revenue, COUNT(*) as trip_count FROM staging.trips GROUP BY payment_type_name ORDER BY total_revenue DESC"

-- Average fare by taxi type
bruin query --connection duckdb-default --query "SELECT taxi_type, AVG(fare_amount) as avg_fare, COUNT(*) as trips FROM staging.trips GROUP BY taxi_type"

-- Trips per day
bruin query --connection duckdb-default --query "SELECT DATE(pickup_datetime) as trip_date, COUNT(*) as daily_trips, SUM(fare_amount) as daily_revenue FROM staging.trips GROUP BY DATE(pickup_datetime) ORDER BY trip_date"
