# Module 6 Homework

See [homework2026.ipynb](homework2026.ipynb)

Yellow 2025-11:

```bash
wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-11.parquet
```


## Question 1: Install Spark and PySpark

- Install Spark
- Run PySpark
- Create a local spark session
- Execute spark.version.

**Answer: spark.version '4.1.1'**


## Question 2: Yellow November 2025

Read the November 2025 Yellow into a Spark Dataframe.

Repartition the Dataframe to 4 partitions and save it to parquet.

What is the average size of the Parquet (ending with .parquet extension) Files that were created (in MB)? Select the answer which most closely matches.

- 6MB
- 25MB
- 75MB
- 100MB

```bash
!ls -lh ./data/pq/yellow/2025/11

total 98M
-rwxrwxrwx 1 home home   0 Mar  5 15:49 _SUCCESS
-rwxrwxrwx 1 home home 25M Mar  5 15:49 part-00000-2f74f9ed-629a-4994-9517-bc3d03963497-c000.snappy.parquet
-rwxrwxrwx 1 home home 25M Mar  5 15:49 part-00001-2f74f9ed-629a-4994-9517-bc3d03963497-c000.snappy.parquet
-rwxrwxrwx 1 home home 25M Mar  5 15:49 part-00002-2f74f9ed-629a-4994-9517-bc3d03963497-c000.snappy.parquet
-rwxrwxrwx 1 home home 25M Mar  5 15:49 part-00003-2f74f9ed-629a-4994-9517-bc3d03963497-c000.snappy.parquet
```

**Answer:  100MB**


## Question 3: Count records

How many taxi trips were there on the 15th of November?

Consider only trips that started on the 15th of November.

- 62,610
- 102,340
- 162,604
- 225,768

```sql
df \
    .withColumn('tpep_pickup_datetime', F.to_date(df.tpep_pickup_datetime)) \
    .filter("tpep_pickup_datetime = '2025-11-15'") \
    .count()
```


**Answer: 162604**


## Question 4: Longest trip

What is the length of the longest trip in the dataset in hours?

- 22.7
- 58.2
- 90.6
- 134.5

```sql
df.withColumn('duration_hours', 
    (F.unix_timestamp('tpep_dropoff_datetime') - F.unix_timestamp('tpep_pickup_datetime')) / 3600
).agg(F.max('duration_hours')).show()
```

+-------------------+
|max(duration_hours)|
+-------------------+
|  90.64666666666666|
+-------------------+


**Answer: 90.6**

## Question 5: User Interface

Spark's User Interface which shows the application's dashboard runs on which local port?

- 80
- 443
- 4040
- 8080

**Answer: 4040**

## Question 6: Least frequent pickup location zone

Load the zone lookup data into a temp view in Spark:

```bash
wget https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
```

Using the zone lookup data and the Yellow November 2025 data, what is the name of the LEAST frequent pickup location Zone?

- Governor's Island/Ellis Island/Liberty Island
- Arden Heights
- Rikers Island
- Jamaica Bay

If multiple answers are correct, select any

```sql
df.join(df_zones, df.PULocationID == df_zones.LocationID) \
    .groupBy('Zone') \
    .count() \
    .orderBy('count', ascending=True) \
    .limit(5) \
    .show(truncate=False)
```

**Answer: Governor's Island/Ellis Island/Liberty Island , Arden Heights**