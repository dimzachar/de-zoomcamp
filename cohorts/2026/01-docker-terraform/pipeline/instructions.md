# Module 1 Homework

## Environment Setup

```bash
python -V
# Python 3.12.1
```

---

## Q1: Understanding Docker images

```bash
docker run -it --rm --entrypoint=bash python:3.13
```

Inside the container:
```bash
pip -V
# pip 25.3 from /usr/local/lib/python3.13/site-packages/pip (python 3.13)
```

**Answer: 25.3**

---

## Q2: Understanding Docker networking and docker-compose

- Service name is `db`, container name is `postgres`
- Internal port is `5432`

**Answer: db:5432**

---

## Setting Up PostgreSQL manual

```bash
docker run -it --rm \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16
```

---

## Data Ingestion

```bash
uv run python ingest_data.py --help
```

```
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
```

### Ingest Green Taxi Data (November 2025)

```bash
uv run python ingest_data.py \
  --pg-user root \
  --pg-pass root \
  --pg-host localhost \
  --pg-port 5432 \
  --pg-db ny_taxi \
  --taxi-type green \
  --year 2025 \
  --month 11
```

### Connect to Database

```bash
uv run pgcli -h localhost -p 5432 -u root -d ny_taxi
```

---

## Q3: Counting short trips

For the trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a `trip_distance` of less than or equal to 1 mile?


```sql
SELECT COUNT(*) 
FROM green_taxi_data_2025_11
WHERE lpep_pickup_datetime >= '2025-11-01'
  AND lpep_pickup_datetime < '2025-12-01'
  AND trip_distance <= 1;
```

| count |
|-------|
| 8007  |

**Answer: 8,007**

---

## Q4: Longest trip for each day

Which was the pick up day with the longest trip distance? Only consider trips with `trip_distance` less than 100 miles (to exclude data errors).

```sql
SELECT 
  DATE(lpep_pickup_datetime) AS pickup_day,
  trip_distance
FROM green_taxi_data_2025_11
WHERE trip_distance < 100
ORDER BY trip_distance DESC
LIMIT 5;
```

**Answer: 2025-11-14**

---

## Q5: Biggest pickup zone

Which was the pickup zone with the largest `total_amount` (sum of all trips) on November 18th, 2025?

```sql
SELECT z."Zone", SUM(g.total_amount) as total
FROM green_taxi_data_2025_11 g
JOIN taxi_zone_lookup z ON g."PULocationID" = z."LocationID"
WHERE DATE(g.lpep_pickup_datetime) = '2025-11-18'
GROUP BY z."Zone"
ORDER BY total DESC
LIMIT 1;
```

| Zone              | total             |
|-------------------|-------------------|
| East Harlem North | 9281.919999999991 |

SELECT 1
Time: 0.011s

**Answer: East Harlem North**

---

## Q6: Largest tip


For the passengers picked up in the zone named "East Harlem North" in November 2025, which was the drop off zone that had the largest tip?

Note: it's `tip` , not `trip`. We need the name of the zone, not the ID.

```sql
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
```

| dropoff_zone   | max_tip |
|----------------|---------|
| Yorkville West | 81.89   |

SELECT 1
Time: 0.017s

**Answer: Yorkville West**

---

## Docker Network Setup (manual experiment not needed)

### Create network and run containers

```bash
# Create network
docker network create pg-network

# Run PostgreSQL
docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  --network=pg-network \
  --name pgdatabase \
  postgres:16

# Run ingestion container
docker run -it \
  --network=pg-network \
  taxi_ingest:v001 \
  --pg-user root \
  --pg-pass root \
  --pg-host pgdatabase \
  --pg-port 5432 \
  --pg-db ny_taxi \
  --taxi-type green \
  --year 2025 \
  --month 11

# In another terminal, run pgAdmin on the same network

docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -v pgadmin_data:/var/lib/pgadmin \
  -p 8085:80 \
  --network=pg-network \
  --name pgadmin \
  dpage/pgadmin4
```

------------------

### Docker Compose (homework)

```bash
# Build ingestion image
docker build -t taxi_ingest:v002 .

docker-compose down -v

docker-compose up -d

docker network ls

# Run ingestion
docker run -it --rm \
  --network=pipeline_default \
  taxi_ingest:v002 \
  --pg-user postgres \
  --pg-pass postgres \
  --pg-host db \
  --pg-port 5432 \
  --pg-db ny_taxi \
  --taxi-type green \
  --year 2025 \
  --month 11

Run queries on pgadmin

# Cleanup
docker-compose down -v
```


## Q7: Terraform Workflow

1. Downloading provider plugins and setting up backend: `terraform init`
2. Generating proposed changes and auto-executing: `terraform apply -auto-approve`
3. Remove all resources: `terraform destroy`

**Answer: terraform init, terraform apply -auto-approve, terraform destroy**

---