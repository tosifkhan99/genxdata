---
title: Features Overview
---

### GenXData Features (Backend)

This page summarizes all backend features available today, with links to detailed guides and examples.

- **Running Modes**
  - **Normal mode**: Generate a full dataset in-memory and write once via a file writer.
  - **Batch mode**: Generate and write data in batches using a batch-aware writer.
  - **Streaming mode**: Stream chunked data to external sinks (e.g., Kafka/AMQP) using `StreamWriter`.

- **Strategies (column generators)**
  - Available strategies: `RANDOM_NUMBER_RANGE_STRATEGY`, `DISTRIBUTED_NUMBER_RANGE_STRATEGY`, `RANDOM_DATE_RANGE_STRATEGY` (alias: `DATE_GENERATOR_STRATEGY`), `DATE_SERIES_STRATEGY`, `DISTRIBUTED_DATE_RANGE_STRATEGY`, `PATTERN_STRATEGY`, `SERIES_STRATEGY`, `DISTRIBUTED_CHOICE_STRATEGY`, `TIME_RANGE_STRATEGY`, `DISTRIBUTED_TIME_RANGE_STRATEGY`, `REPLACEMENT_STRATEGY`, `CONCAT_STRATEGY`, `RANDOM_NAME_STRATEGY`, `DELETE_STRATEGY`, `MAPPING_STRATEGY`, `UUID_STRATEGY`.
  - All strategies are stateful; streaming/batch modes maintain state across chunks.
  - Optional per-column flags and fields: `unique`, `seed`, `mask`.

- **Masking**
  - Apply a pandas-query style `mask` per column to target a subset of rows when generating or modifying values.
  - Masks are validated before execution and can be previewed.

- **Uniqueness**
  - Per-strategy `unique: true` is supported (strategy-dependent). In normal mode, a running set is tracked to enforce uniqueness across the full dataset. In streaming/batch, uniqueness across chunks is not guaranteed (best-effort within a chunk only).

- **Writers (outputs)**
  - File writers via `file_writer` (normal mode): `csv`, `json`, `excel` (`xlsx`, `xls`), `parquet`, `sqlite` (`db`), `html`, `feather`.
  - Batch writer: wraps a concrete writer and adds batch metadata/counters; configured under `batch.file_writer`.
  - Stream writer: sends rows/batches to queues via `messaging` (Kafka/AMQP). Supports nested (e.g., `{ amqp: {...} }`) and flat (e.g., `{ type: amqp, ... }`) configs.

- **Messaging**
  - Producers created via `QueueFactory`. Supported types: Kafka and AMQP (e.g., RabbitMQ/ActiveMQ). See How‑to → Messaging.

- **CLI**
  - Single entry command: `python main.py generate <config> [--batch <batch.yaml> | --stream <stream.yaml>]`.
  - See Tutorials → Quickstart for ready-to-run examples.

- **Config ergonomics**
  - Clean YAML schema: top-level dataset metadata, columns with strategies, per-column `mask`, `unique`, and strategy params.
  - Backwards compatible aliases for some strategies and writer types are normalized internally.

- **Observability**
  - Structured logging; optional performance report with timing metrics.
  - Standardized processing results: status, rows/columns generated, writer summary, performance report.

### Minimal Examples

Normal mode (CSV):
```yaml
file_writer:
  type: csv
  params:
    output_path: output/users.csv
metadata:
  rows: 1000
columns:
  - name: user_id
    strategy: UUID_STRATEGY
  - name: age
    strategy: RANDOM_NUMBER_RANGE_STRATEGY
    params: { start: 18, end: 65 }
```

Batch mode (Parquet batches):
```yaml
batch:
  batch_size: 5000
  chunk_size: 2000
  file_writer:
    type: parquet
    params:
      output_path: output/users.parquet
```

Streaming (Kafka):
```yaml
type: kafka
bootstrap_servers: localhost:9092
topic: genxdata.users
batch_size: 1000
chunk_size: 1000
```

Masking and uniqueness on a column:
```yaml
- name: vip_discount
  strategy: RANDOM_NUMBER_RANGE_STRATEGY
  params: { start: 5, end: 20 }
  mask: "segment == 'VIP'"
  unique: false
```

### Next

- Read the Running Modes guide for detailed behavior and sizing.
- Explore How‑to guides for writing batch and streaming configs.
- See Strategies Overview for a one-line summary of each strategy and links to reference.


