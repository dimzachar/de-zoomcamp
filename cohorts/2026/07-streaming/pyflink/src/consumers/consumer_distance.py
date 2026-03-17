import json
from kafka import KafkaConsumer

TOPIC_NAME = "green-trips"

consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    consumer_timeout_ms=10000,
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

count = 0

for message in consumer:
    trip = message.value

    if trip["trip_distance"] and trip["trip_distance"] > 5:
        count += 1

print("Trips with distance > 5 km:", count)