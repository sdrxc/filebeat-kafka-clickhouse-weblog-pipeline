import re
import time
import json
from kafka import KafkaConsumer
from clickhouse_driver import Client
from kafka.errors import NoBrokersAvailable

# Retry Kafka connection
while True:
    try:
        consumer = KafkaConsumer(
            "web_logs",
            bootstrap_servers="kafka:29092",
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda x: x.decode("utf-8")
        )
        print("Connected to Kafka!")
        break
    except NoBrokersAvailable:
        print("Kafka not ready, retrying in 3 seconds...")
        time.sleep(3)

client = Client(host='clickhouse')

log_pattern = re.compile(
    r'(?P<ip>\S+) - - \[(?P<time>[^\]]+)\] "(?P<method>\S+) (?P<url>\S+) \S+" (?P<status>\d+) (?P<size>\d+)'
)

for msg in consumer:
    print("RAW MESSAGE:", msg.value)

    try:
        json_data = json.loads(msg.value)
    except:
        print("ERROR decoding JSON")
        continue

    line = json_data.get("message", "")
    match = log_pattern.match(line)

    if not match:
        print("NO MATCH:", line)
        continue

    row = match.groupdict()
    print("Parsed row:", row)

    client.execute("""
        INSERT INTO processed_logs (ip, url, status)
        VALUES (%(ip)s, %(url)s, %(status)s)
    """, row)

    print("Inserted:", row)
