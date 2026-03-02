# Homework: Build Your Own dlt Pipeline

## The Challenge

See the homework description here: [dlt_homework.md](dlt_homework.md)


### Run the pipeline

From the `dlt-taxi` folder, install dependencies (managed in `pyproject.toml`) and run the pipeline:

```bash
uv sync          # install dlt, duckdb, marimo, ibis, plotly, etc.
uv run python taxi_pipeline.py
```

This script:

- **Creates/updates** a DuckDB file (e.g. `taxi_pipeline.duckdb`)
- **Loads** the NYC taxi API data into the `nyc_taxi_data` dataset
- **Writes** a table named `taxi_data` (from the `taxi_source` resource)

To quickly inspect the pipeline metadata and loaded tables, you can also run:

```bash
dlt pipeline taxi_pipeline show
```

### Run the Marimo report

After the pipeline has successfully run and the DuckDB file exists, start the Marimo dashboard:

```bash
uv sync
uv run marimo edit taxi_visualization.py
```

This will open an interactive report that:

- Attaches to the existing `taxi_pipeline` DuckDB dataset
- Uses Ibis to query the `taxi_data` table
- Shows visualizations and the exact aggregates used to answer the homework questions (date range, credit‑card share, total tips) in the bottom section titled **SQL Answers**.

---

## Questions

### Question 1: What is the start date and end date of the dataset?

- 2009-01-01 to 2009-01-31
- 2009-06-01 to 2009-07-01
- 2024-01-01 to 2024-02-01
- 2024-06-01 to 2024-07-01

**Answer: 2009-06-01 to 2009-07-01**

We computed this in the Marimo notebook by casting the pickup timestamp to a date and taking the minimum and maximum over the `taxi_data` table:

```sql
SELECT
  MIN(CAST(trip_pickup_date_time AS DATE)) AS start_date,
  MAX(CAST(trip_pickup_date_time AS DATE)) AS end_date
FROM taxi_data;
```

The resulting date range is **2009‑06‑01** to **2009‑07‑01**, which matches the second multiple‑choice option.

### Question 2: What proportion of trips are paid with credit card?

- 16.66%
- 26.66%
- 36.66%
- 46.66%

**Answer: 26.66%**

To get this proportion, we counted how many trips have `payment_type = 'Credit'` and divided by the total number of trips:

```sql
WITH stats AS (
  SELECT
    COUNT(*) AS total_trips,
    SUM(CASE WHEN payment_type = 'Credit' THEN 1 ELSE 0 END) AS credit_trips
  FROM taxi_data
)
SELECT
  100.0 * credit_trips / total_trips AS credit_percentage
FROM stats;
```

The Marimo cell that performs this aggregation prints a value of about **26.66%**, so we chose that option.

### Question 3: What is the total amount of money generated in tips?

- $4,063.41
- $6,063.41
- $8,063.41
- $10,063.41

**Answer: $6,063.41**

For total tips, we simply summed the `tip_amt` column over all rows in `taxi_data`:

```sql
SELECT
  SUM(tip_amt) AS total_tips
FROM taxi_data;
```

The Marimo report shows `total_tips` as **$6,063.41**, which corresponds to the second option in the multiple‑choice list.
