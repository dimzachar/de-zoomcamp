-- Question 1: Date range
SELECT 
    MIN(DATE(trip_pickup_date_time)) as start_date,
    MAX(DATE(trip_pickup_date_time)) as end_date
FROM taxi_data;

-- Question 2: Credit card proportion
SELECT 
    ROUND(100.0 * COUNT(*) FILTER (WHERE payment_type = 'Credit') / COUNT(*), 2) as credit_percentage
FROM taxi_data;

-- Question 3: Total tips
SELECT 
    ROUND(SUM(tip_amt), 2) as total_tips
FROM taxi_data;
