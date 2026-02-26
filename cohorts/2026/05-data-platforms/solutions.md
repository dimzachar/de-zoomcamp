# Module 5 Homework: Data Platforms with Bruin


### Question 1. Bruin Pipeline Structure

In a Bruin project, what are the required files/directories?

- `bruin.yml` and `assets/`
- `.bruin.yml` and `pipeline.yml` (assets can be anywhere)
- `.bruin.yml` and `pipeline/` with `pipeline.yml` and `assets/`
- `pipeline.yml` and `assets/` only

Assets can be placed anywhere in the directory structure, but by convention they're typically in an assets/ folder.

**Answer:  `.bruin.yml` and `pipeline.yml` (assets can be anywhere)**

---

### Question 2. Materialization Strategies

You're building a pipeline that processes NYC taxi data organized by month based on `pickup_datetime`. Which incremental strategy is best for processing a specific interval period by deleting and inserting data for that time period?

- `append` - always add new rows
- `replace` - truncate and rebuild entirely
- `time_interval` - incremental based on a time column
- `view` - create a virtual table only

**Answer: `time_interval` - incremental based on a time column**

---

### Question 3. Pipeline Variables

You have the following variable defined in `pipeline.yml`:

```yaml
variables:
  taxi_types:
    type: array
    items:
      type: string
    default: ["yellow", "green"]
```

How do you override this when running the pipeline to only process yellow taxis?

- `bruin run --taxi-types yellow`
- `bruin run --var taxi_types=yellow`
- `bruin run --var 'taxi_types=["yellow"]'`
- `bruin run --set taxi_types=["yellow"]`

Quote the entire value to prevent shell interpretation.

**Answer: `bruin run --var 'taxi_types=["yellow"]'`**

---

### Question 4. Running with Dependencies

You've modified the `ingestion/trips.py` asset and want to run it plus all downstream assets. Which command should you use?

- `bruin run ingestion.trips --all`
- `bruin run ingestion/trips.py --downstream`
- `bruin run pipeline/trips.py --recursive`
- `bruin run --select ingestion.trips+`

the --downstream flag is used to run an asset along with all its downstream dependencies.

**Answer: `bruin run ingestion/trips.py --downstream`**

---

### Question 5. Quality Checks

You want to ensure the `pickup_datetime` column in your trips table never has NULL values. Which quality check should you add to your asset definition?

- `name: unique`
- `name: not_null`
- `name: positive`
- `name: accepted_values, value: [not_null]`

the not_null check ensures a column never has NULL values.

**Answer: name: not_null**

---

### Question 6. Lineage and Dependencies

After building your pipeline, you want to visualize the dependency graph between assets. Which Bruin command should you use?

- `bruin graph`
- `bruin dependencies`
- `bruin lineage`
- `bruin show`

the lineage command is used to visualize the dependency graph between assets.
**Answer: `bruin lineage`**

---

### Question 7. First-Time Run

You're running a Bruin pipeline for the first time on a new DuckDB database. What flag should you use to ensure tables are created from scratch?

- `--create`
- `--init`
- `--full-refresh`
- `--truncate`

the --full-refresh flag is used to create tables from scratch.

**Answer: `--full-refresh`**

---