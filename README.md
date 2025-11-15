# Real time web-log ingestion pipeline

A minimal end-to-end log pipeline demo using Filebeat → Kafka → Python processor → ClickHouse, with Grafana available for visualization.

## Overview

This repository demonstrates a simple streaming pipeline that:
- Produces synthetic access logs to `logs/access.log`.
- Uses Filebeat to tail the log file and publish events to a Kafka topic `web_logs`.
- Consumes messages from Kafka with a Python processor, parses log lines, and inserts them into ClickHouse.
- Exposes ClickHouse and Grafana for storage and visualization.

## What’s included
- `docker-compose.yml` — runs Zookeeper, Kafka, ClickHouse, Grafana, Filebeat, log producer and the Python processor.
- `filebeat/filebeat.yml` — Filebeat configuration (reads `/usr/share/logs/access.log`, publishes to Kafka).
- `logs/generate_logs.py` — simple log generator that appends lines to `logs/access.log`.
- `clickhouse/init.sql` — SQL to create the `processed_logs` table.
- `python_processor/` — contains `Dockerfile`, `processor.py` and `requirements.txt` for the consumer.

## Architecture

1. `log-producer` appends lines into `logs/access.log`.
2. `filebeat` tails the file and sends each line to Kafka topic `web_logs`.
3. `python-processor` consumes the topic, parses each log entry and inserts a row into ClickHouse table `processed_logs`.
4. `grafana` can be connected to ClickHouse to build dashboards.


<img width="727" height="540" alt="Screenshot 2025-11-15 at 8 02 56 PM" src="https://github.com/user-attachments/assets/eaf6566a-9f8e-402c-9178-d41cff42cc20" />

## Prerequisites

- Docker and Docker Compose installed.
- Sufficient resources to run Kafka and ClickHouse containers.

## Quick start

Run from the project root (where `docker-compose.yml` is located):

1. Start services:

   docker-compose up -d

2. Tail logs to verify components are running:

   docker-compose logs -f filebeat python-processor kafka clickhouse

3. Visit services in your browser:
- Grafana: http://localhost:3000
- ClickHouse HTTP: http://localhost:8123/play

Note: Kafka is reachable from host at `localhost:9092` (containers use `kafka:29092`).

## ClickHouse table

`clickhouse/init.sql` creates:

```
CREATE TABLE IF NOT EXISTS processed_logs (
    ip String,
    url String,
    status UInt16,
    ts DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY ts;
```

## Python processor behavior

- `python_processor/processor.py` subscribes to Kafka topic `web_logs`.
- Expects messages in Filebeat JSON format (message string is in `message` field).
- Uses a regex to extract `ip`, `url`, and `status`, then inserts into ClickHouse.
- Prints debug messages on parsing and insertion; it retries connecting to Kafka until available.

## Useful ClickHouse queries

- Show latest rows:

  SELECT * FROM processed_logs ORDER BY ts DESC LIMIT 100;

- Count by status code:

  SELECT status, count() FROM processed_logs GROUP BY status ORDER BY status;

## Troubleshooting

- If the processor prints `NO MATCH` for messages, check the raw message format in the Filebeat output.
- If Kafka is not reachable, ensure Docker Compose started Kafka and check `docker-compose logs kafka`.
- Make sure file paths in `filebeat/filebeat.yml` match the container mount (`/usr/share/logs/access.log`).

## Next steps / Improvements

- Add more robust error handling and dead-lettering for unparsable messages.
- Add Grafana dashboard and ClickHouse datasource configuration.
- Harden Docker Compose with healthchecks, restart policies and resource limits.

---

If you want, I can add a sample Grafana dashboard JSON and instructions to connect Grafana to ClickHouse.
