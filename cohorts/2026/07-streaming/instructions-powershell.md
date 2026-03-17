# **Workshop instructions**


# 1️⃣ Install prerequisites

### Install Docker Desktop

Verify installation:

```powershell
docker --version
docker compose version
```

---

### Install uv

Run:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify:

```powershell
uv --version
```

---

### Install PostgreSQL client (optional)

Install pgcli:

```powershell
uv tool install pgcli
```

or run directly:

```powershell
uvx pgcli
```

---

# 2️⃣ Create project folder

```powershell
mkdir pyflink-workshop
cd pyflink-workshop
```

---

# 3️⃣ Create the docker-compose file

Create file:

```powershell
New-Item docker-compose.yml
```

Open and paste Redpanda config:

```powershell
notepad docker-compose.yml
```

Start Kafka broker:

```powershell
docker compose up redpanda -d
```

Verify:

```powershell
docker compose ps
```

Expected:

```
redpanda   Up
```

---

# 4️⃣ Create Python environment

Initialize project:

```powershell
uv init -p 3.12
```

Install dependencies:

```powershell
uv add kafka-python pandas pyarrow
```

---

# 5️⃣ Create project folders

PowerShell equivalent of `mkdir -p`:

```powershell
mkdir src
mkdir src\producers
mkdir src\consumers
mkdir src\job
```

---

# 6️⃣ Create shared model file

Create file:

```powershell
New-Item src\models.py
```

Open:

```powershell
notepad src\models.py
```

Paste the `Ride` dataclass and helper functions from README.

---

# 7️⃣ Create Kafka producer

Create file:

```powershell
New-Item src\producers\producer.py
```

Open:

```powershell
notepad src\producers\producer.py
```

Paste producer code.

---

# 8️⃣ Run the producer

```powershell
uv run python src\producers\producer.py
```

Expected:

```
Sent: Ride(...)
Sent: Ride(...)
...
took 10 seconds
```

Now **1000 events are inside Kafka (Redpanda)**.

---

# 9️⃣ Create Kafka consumer

Create file:

```powershell
New-Item src\consumers\consumer.py
```

Open:

```powershell
notepad src\consumers\consumer.py
```

Paste consumer code.

Run it:

```powershell
uv run python src\consumers\consumer.py
```

Expected:

```
Listening to rides...
Received: PU=...
Received: PU=...
```

---

# 🔟 Add PostgreSQL

Edit compose file:

```powershell
notepad docker-compose.yml
```

Add the **postgres service** from README.

Start PostgreSQL:

```powershell
docker compose up postgres -d
```

---

# 1️⃣1️⃣ Connect to PostgreSQL

Run:

```powershell
uvx pgcli -h localhost -p 5432 -U postgres -d postgres
```

Password:

```
postgres
```

Create table:

```sql
CREATE TABLE processed_events (
    PULocationID INTEGER,
    DOLocationID INTEGER,
    trip_distance DOUBLE PRECISION,
    total_amount DOUBLE PRECISION,
    pickup_datetime TIMESTAMP
);
```

---

# 1️⃣2️⃣ Create consumer that writes to PostgreSQL

Install dependency:

```powershell
uv add psycopg2-binary
```

Create file:

```powershell
New-Item src\consumers\consumer_postgres.py
```

Paste code from README.

Run it:

```powershell
uv run python src\consumers\consumer_postgres.py
```

Stop with:

```
CTRL + C
```

Check data:

```powershell
uvx pgcli -h localhost -p 5432 -U postgres -d postgres
```

```sql
SELECT count(*) FROM processed_events;
```

Expected:

```
1000
```

---

# 1️⃣3️⃣ Download Flink build files

PowerShell version of `wget`:

```powershell
$PREFIX="https://raw.githubusercontent.com/DataTalksClub/data-engineering-zoomcamp/main/07-streaming/workshop"

Invoke-WebRequest "$PREFIX/Dockerfile.flink" -OutFile Dockerfile.flink
Invoke-WebRequest "$PREFIX/pyproject.flink.toml" -OutFile pyproject.flink.toml
Invoke-WebRequest "$PREFIX/flink-config.yaml" -OutFile flink-config.yaml
```

---

# 1️⃣4️⃣ Add Flink services to docker-compose

Edit compose file again:

```powershell
notepad docker-compose.yml
```

Add services:

* `jobmanager`
* `taskmanager`

(from README).

---

# 1️⃣5️⃣ Build Flink cluster

```powershell
docker compose up --build -d
```

First build takes **3–5 minutes**.

Check services:

```powershell
docker compose ps
```

Expected:

```
jobmanager
taskmanager
postgres
redpanda
```

---

# 1️⃣6️⃣ Open Flink dashboard

Open browser:

```
http://localhost:8081
```

This is the **Apache Flink dashboard**.

You should see **1 task manager**.

---

# 1️⃣7️⃣ Create Flink streaming job

Create file:

```powershell
New-Item src\job\pass_through_job.py
```

Paste the job code from README.

---

# 1️⃣8️⃣ Submit Flink job

PowerShell multiline command:

```powershell
docker compose exec jobmanager ./bin/flink run `
  -py /opt/src/job/pass_through_job.py `
  --pyFiles /opt/src -d
```

Expected:

```
Job has been submitted with JobID ...
```

---

# 1️⃣9️⃣ Send events again

```powershell
uv run python src\producers\producer.py
```

---

# 2️⃣0️⃣ Check PostgreSQL

```powershell
uvx pgcli -h localhost -p 5432 -U postgres -d postgres
```

```sql
SELECT count(*) FROM processed_events;
```

You should now see rows inserted **via the Flink pipeline**.

Pipeline:

```
Python Producer
      ↓
Kafka (Redpanda)
      ↓
Flink Streaming Job
      ↓
PostgreSQL
```

---


# 2️⃣1️⃣ Kafka offsets: earliest vs latest

Flink consumes Kafka topics based on the **consumer group** and **offset reset policy**.

* `earliest`: starts from the **beginning of the topic**
* `latest`: starts from **new messages only**

You can control this in your Flink job configuration (or in the Python Kafka consumer).

**Experiment**:

Clear the table:
```sql
TRUNCATE processed_events;
```

1. Stop your current Flink job (from dashboard or `docker compose stop jobmanager taskmanager`).
2. Re-run the job with a different offset setting. For example, using earliest offsets will reprocess all messages:

src/job/pass_through_job.py - change both offset settings:

```
'scan.startup.mode' = 'earliest-offset',
'properties.auto.offset.reset' = 'earliest',
```


```powershell
docker compose exec jobmanager ./bin/flink run `
  -py /opt/src/job/pass_through_job.py `
  --pyFiles /opt/src -d
```

3. Then produce events again:

```powershell
uv run python src\producers\producer.py
```

4. Query PostgreSQL:

```powershell
uvx pgcli -h localhost -p 5432 -U postgres -d postgres
```

```sql
SELECT count(*) FROM processed_events;
```

* With **earliest**, the count increases because Flink reprocesses old messages.
* With **latest**, only new events are counted.

This helps you understand **Kafka offset management** in streaming jobs.

---

# 2️⃣2️⃣ Aggregation setup

Now you’ll create a **Flink job that aggregates data**.

## 1️⃣ Create aggregated table in PostgreSQL

```powershell
uvx pgcli -h localhost -p 5432 -U postgres -d postgres
```

Then run:

```sql
CREATE TABLE processed_events_aggregated (
    window_start TIMESTAMP,
    PULocationID INTEGER,
    num_trips BIGINT,
    total_revenue DOUBLE PRECISION,
    PRIMARY KEY (window_start, PULocationID)
);
```

---

## 2️⃣ Create aggregation Flink job

Create the Python file:

```powershell
New-Item -ItemType File src\job\aggregation_job.py
```

Paste the aggregation code from the README (uses **tumbling windows, group by PULocationID, sum/count**).

Key points:

* Read from Kafka topic `rides`.
* Group by `PULocationID`.
* Aggregate with **windowing** (e.g., 1-minute tumbling windows).
* Write results to `processed_events_aggregated`.

---

# 2️⃣3️⃣ Submit aggregation job

Run:

```powershell
docker compose exec jobmanager ./bin/flink run `
  -py /opt/src/job/aggregation_job.py `
  --pyFiles /opt/src -d
```

Expected:

```
Job has been submitted with JobID ...
```

---

# 2️⃣4️⃣ Produce more events

To test the aggregation job, run your producer again:

```powershell
uv run python src\producers\producer.py
```

---

# 2️⃣5️⃣ Query aggregated table

Connect to PostgreSQL:

```powershell
uvx pgcli -h localhost -p 5432 -U postgres -d postgres
```

Then run:

```sql
SELECT * FROM processed_events_aggregated ORDER BY window_start DESC LIMIT 10;
```

You should see **aggregated counts and revenue per pickup location**, updated in near-real-time.

---

# 2️⃣6️⃣ Continuous streaming

If you modify your producer to **loop continuously** (e.g., sleep + send batch), the aggregation table will continuously update.

This demonstrates **stateful stream processing** with Flink, which is the main goal of this workshop.

---

At this point, you’ve covered:

```
Python Producer
      ↓
Kafka (Redpanda)
      ↓
Flink Aggregation Job (windowed)
      ↓
PostgreSQL (aggregated table)
```

---

now we’re into the **“late events” and upserts** part of the workshop. That’s the next Flink concept after offsets and windowed aggregation. The README shows that the **CSV producer is always in order**, so Flink’s watermarks never see late events, but to experiment with **late arrivals**, you use the **real-time synthetic producer**.

---

# 2️⃣7️⃣ Download the real-time producer

In PowerShell, you can download the file like this:

```powershell
$PREFIX = "https://raw.githubusercontent.com/DataTalksClub/data-engineering-zoomcamp/main/07-streaming/workshop"
Invoke-WebRequest "$PREFIX/src/producers/producer_realtime.py" -OutFile "src\producers\producer_realtime.py"
```

This is the equivalent of the `wget` command in Linux/macOS.

---

# 2️⃣8️⃣ Run the real-time producer

Now run it with `uv`:

```powershell
uv run python src\producers\producer_realtime.py
```

* This producer **generates synthetic ride events** continuously.
* It introduces **occasional delays**, simulating **late arrivals**.

---

# 2️⃣9️⃣ Observe Flink handling late events

1. The **aggregation job** you submitted earlier will now start processing late events.

2. Flink uses **event time + watermarks**:

   * Events arriving **after the watermark** for a window are considered **late**.
   * Depending on your job configuration, late events can **update aggregates via upserts**.

3. Query PostgreSQL:

```powershell
uvx pgcli -h localhost -p 5432 -U postgres -d postgres
```

```sql
SELECT * FROM processed_events_aggregated ORDER BY window_start DESC LIMIT 20;
```

* You may see **rows updated** with new totals because late events triggered **upserts**.
* The `PRIMARY KEY (window_start, PULocationID)` ensures Flink **merges late events into existing rows**, not inserts duplicates.

---

# 3️⃣0️⃣ Key concepts here

* **Late events**: Flink can handle events arriving out of order if **watermarks** are set correctly.
* **Upserts**: Aggregated tables with primary keys allow Flink to **update existing rows** instead of inserting duplicates.
* **Real-time streaming**: Using the synthetic producer simulates real-world scenarios where events are not perfectly ordered.

---


# 🧹 Cleanup when finished

Stop everything:

```powershell
docker compose down
```

Remove volumes too:

```powershell
docker compose down -v
```

---
