Clean start (removes old containers/volumes):

```powershell
docker compose down -v
docker compose build
docker compose up -d
```

Check the services are running:

```powershell
docker compose ps
```

You should see:

* Redpanda
* Flink JobManager
* Flink TaskManager
* PostgreSQL

---

# Q1. Redpanda version

Run `rpk version` inside the Redpanda container:

```powershell
docker compose exec redpanda rpk version
```


```powershell
rpk version: v25.3.9
Git ref:     836b4a36ef6d5121edbb1e68f0f673c2a8a244e2
Build date:  2026 Feb 26 07 48 21 Thu
OS/Arch:     linux/amd64
Go version:  go1.24.3

Redpanda Cluster
  node-1  v25.3.9 - 836b4a36ef6d5121edbb1e68f0f673c2a8a244e2
```

**Answer: v25.3.9**
---

# Q2. Sending data to Redpanda

"If you sent data to the topic multiple times, delete and recreate the topic to avoid duplicates"

```powershell
docker compose exec redpanda rpk topic delete green-trips
```

Create a topic called `green-trips`:

```powershell
docker compose exec redpanda rpk topic create green-trips
```

```
TOPIC        STATUS
green-trips  OK
```

### Create the data folder


```powershell
New-Item -ItemType Directory -Path src\data
```

---

### Download the dataset

```powershell
Invoke-WebRequest "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-10.parquet" -OutFile "src\data\green_tripdata_2025-10.parquet"
```

---

### Verify

```powershell
ls src\data
```

```
green_tripdata_2025-10.parquet
```


Create `src\producers\producer_green.py`


Run:

```powershell
uv run python src\producers\producer_green.py
```
```
Rows to send: 49416
took 2.59 seconds
```

**Answer: 2.59 seconds**


---

# Q3 — Consumer: trips > 5 km

Create `src\consumers\consumer_distance.py`:

Run:

```powershell
uv run python src\consumers\consumer_distance.py
```

Trips with distance > 5 km: 8506
**Answer: 8506**

---

# Q4 — Tumbling window (5 minutes) by PULocationID - Which `PULocationID` had the most trips in a single 5-minute window?

### Create PostgreSQL table

```sql
CREATE TABLE green_trips_agg (
    window_start TIMESTAMP,
    PULocationID INTEGER,
    num_trips BIGINT,
    PRIMARY KEY (window_start, PULocationID)
);
```


Create `src\job\aggregation_tumbling.py`:


Submit the job:

```powershell
docker exec -it pyflink-jobmanager-1 flink run -py /opt/src/job/aggregation_tumbling.py
```

Wait 1-2 minutes, then query:

```sql
SELECT PULocationID, num_trips
FROM green_trips_agg
ORDER BY num_trips DESC
LIMIT 3;
```

Record the PULocationID with the most trips.

+--------------+-----------+
| pulocationid | num_trips |
|--------------+-----------|
| 74           | 15        |
| 74           | 14        |
| 74           | 13        |
+--------------+-----------+
SELECT 3
Time: 0.005s

**Answer: 74**

---

# Q5 — Session window (5-minute gap) - How many trips were in the longest session?



Create table: 

```sql
docker exec -it pyflink-postgres-1 psql -U postgres -c "
CREATE TABLE IF NOT EXISTS green_trips_session (
    PULocationID  INT,
    window_start  TIMESTAMP,
    window_end    TIMESTAMP,
    num_trips     BIGINT,
    PRIMARY KEY (PULocationID, window_start)
);"
```

Job: `src\job\aggregation_session.py` (similar, use `SESSION` window with 5-minute gap).

Submit:

```powershell
docker exec -it pyflink-jobmanager-1 flink run -py /opt/src/job/aggregation_session.py
```

```sql
SELECT PULocationID, num_trips, window_start, window_end 
FROM green_trips_session 
ORDER BY num_trips DESC 
LIMIT 5; 
```

+--------------+-----------+---------------------+---------------------+
| pulocationid | num_trips | window_start        | window_end          |
|--------------+-----------+---------------------+---------------------|
| 74           | 81        | 2025-10-08 06:46:14 | 2025-10-08 08:27:40 |
| 74           | 72        | 2025-10-01 06:52:23 | 2025-10-01 08:23:33 |
| 74           | 71        | 2025-10-28 08:31:08 | 2025-10-28 09:39:30 |
| 74           | 71        | 2025-10-22 06:58:31 | 2025-10-22 08:25:04 |
| 74           | 70        | 2025-10-27 06:56:30 | 2025-10-27 08:24:09 |
+--------------+-----------+---------------------+---------------------+
SELECT 5
Time: 0.005s

**Answer: 81**
---

# Q6 — Tumbling window (1 hour) total tip - Which hour had the highest total tip amount?

Table:

```sql
CREATE TABLE green_trips_tip_hour (
    window_start TIMESTAMP,
    total_tip DOUBLE PRECISION,
    PRIMARY KEY (window_start)
);
```

Job: `src\job\aggregation_tip_hour.py` using 1-hour tumbling window:

Submit job and query:
```powershell
docker exec -it pyflink-jobmanager-1 flink run -py /opt/src/job/aggregation_tip_hour.py
```

```sql
SELECT window_start, total_tip
FROM green_trips_tip_hour
ORDER BY total_tip DESC
LIMIT 1;
```


postgres@localhost:postgres> SELECT window_start, total_tip FROM green_trips_tip_hour ORDER BY total_tip DESC LIMIT 3;
+---------------------+--------------------+
| window_start        | total_tip          |
|---------------------+--------------------|
| 2025-10-16 18:00:00 | 510.8599999999999  |
| 2025-10-30 16:00:00 | 494.41             |
| 2025-10-09 18:00:00 | 472.01000000000016 |
+---------------------+--------------------+
SELECT 3
Time: 0.013s
**Answer: 2025-10-16 18:00:00**

---
