❯ python -V
Python 3.12.1


❯ docker run -it --rm --entrypoint=bash python:3.13
Unable to find image 'python:3.13' locally
3.13: Pulling from library/python
281b80c799de: Pull complete 
15f14138abe4: Pull complete 
378c64c44580: Pull complete 
02e37abc533a: Pull complete 
72a54b312891: Pull complete 
49bfa2c2fcc6: Pull complete 
eccf4e14738d: Pull complete 
Digest: sha256:366cbc24500bf74339dee68b5d3b514e2adcba7f9fc4ddb4e320881f7121bf9e
Status: Downloaded newer image for python:3.13
root@231c26442b53:/# pip -V
pip 25.3 from /usr/local/lib/python3.13/site-packages/pip (python 3.13)

docker run -it --rm \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16


uv run python ingest_data.py --help
Usage: ingest_data.py [OPTIONS]

  Ingest NYC taxi Parquet data into PostgreSQL database.

Options:
  --pg-user TEXT                  PostgreSQL user
  --pg-pass TEXT                  PostgreSQL password
  --pg-host TEXT                  PostgreSQL host
  --pg-port INTEGER               PostgreSQL port
  --pg-db TEXT                    PostgreSQL database name
  --taxi-type [green|yellow|fhv|fhvhv]
                                  Taxi dataset type
  --year INTEGER                  Year of the data
  --month INTEGER                 Month of the data
  --target-table TEXT             Target table name
  --batch-size INTEGER            Batch size for Parquet loading
  --help                          Show this message and exit.



uv run python ingest_data.py \
  --pg-user root \
  --pg-pass root \
  --pg-host localhost \
  --pg-port 5432 \
  --pg-db ny_taxi \
  --taxi-type yellow \
  --year 2021 \
  --month 01

uv run pgcli -h localhost -p 5432 -u root -d ny_taxi


Q3/ 
SELECT COUNT(*) 
FROM green_taxi_data_2025_11
WHERE lpep_pickup_datetime >= '2025-11-01'
  AND lpep_pickup_datetime < '2025-12-01'
  AND trip_distance <= 1;


+-------+
| count |
|-------|
| 8007  |
+-------+
SELECT 1
Time: 0.537s

Q4/

SELECT
    DATE(lpep_pickup_datetime) AS pickup_day,
    trip_distance
FROM green_taxi_data_2025_11
WHERE trip_distance < 100
ORDER BY trip_distance DESC
LIMIT 5;

2025-11-14

Q5/

SELECT z."Zone", SUM(g.total_amount) as total
FROM green_taxi_data_2025_11 g
JOIN taxi_zone_lookup z ON g."PULocationID" = z."LocationID"
WHERE DATE(g.lpep_pickup_datetime) = '2025-11-18'
GROUP BY z."Zone"
ORDER BY total DESC
LIMIT 1;

+-------------------+-------------------+
| Zone              | total             |
|-------------------+-------------------|
| East Harlem North | 9281.919999999991 |
+-------------------+-------------------+
SELECT 1
Time: 0.011s

Q6/

SELECT dz."Zone" as dropoff_zone, MAX(g.tip_amount) as max_tip
FROM public.green_taxi_data_2025_11 g
JOIN public.taxi_zone_lookup pz ON g."PULocationID" = pz."LocationID"
JOIN public.taxi_zone_lookup dz ON g."DOLocationID" = dz."LocationID"
WHERE pz."Zone" = 'East Harlem North'
  AND g.lpep_pickup_datetime >= '2025-11-01'
  AND g.lpep_pickup_datetime < '2025-12-01'
GROUP BY dz."Zone"
ORDER BY max_tip DESC
LIMIT 1;

+----------------+---------+
| dropoff_zone   | max_tip |
|----------------+---------|
| Yorkville West | 81.89   |
+----------------+---------+
SELECT 1
Time: 0.017s

-----------------------------------------

docker network create pg-network

docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  --network=pg-network \
  --name pgdatabase \
  postgres:16

docker run -it \
  --network=pg-network \
  taxi_ingest:v001 \
    --pg-user root \
    --pg-pass root \
    --pg-host pgdatabase \
    --pg-port 5432 \
    --pg-db ny_taxi \
    --taxi-type yellow \
    --year 2021 \
    --month 01


# In another terminal, run pgAdmin on the same network

docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -v pgadmin_data:/var/lib/pgadmin \
  -p 8085:80 \
  --network=pg-network \
  --name pgadmin \
  dpage/pgadmin4