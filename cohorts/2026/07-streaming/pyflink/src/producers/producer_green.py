import pandas as pd
import json
from kafka import KafkaProducer
from time import time

# Load parquet dataset
df = pd.read_parquet("src/data/green_tripdata_2025-10.parquet")

# Keep only required columns
columns = [
    "lpep_pickup_datetime",
    "lpep_dropoff_datetime",
    "PULocationID",
    "DOLocationID",
    "passenger_count",
    "trip_distance",
    "tip_amount",
    "total_amount",
]

df = df[columns]

# Convert datetime columns to strings (required for JSON)
df["lpep_pickup_datetime"] = df["lpep_pickup_datetime"].astype(str)
df["lpep_dropoff_datetime"] = df["lpep_dropoff_datetime"].astype(str)

print(f"Rows to send: {len(df)}")

# Create Kafka producer
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

t0 = time()

# Send each row to Kafka
for row in df.to_dict(orient="records"):
    producer.send("green-trips", row)

# Ensure all messages are sent
producer.flush()

t1 = time()

print(f"took {(t1 - t0):.2f} seconds")