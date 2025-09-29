---
title: Running Modes
---

### Running Modes

GenXData supports three execution modes. This guide explains when to use each, configuration shapes, and what the orchestrator does internally.

### Normal Mode

- **When**: Small to medium datasets that fit in memory and are written once at the end.
- **Processor**: `NormalConfigProcessor`
- **Writer**: A concrete file writer created by `FileWriterFactory` from `file_writer.type` and `file_writer.params`.

Config shape (excerpt):
```yaml
file_writer:
  type: csv  # csv|json|excel|xlsx|xls|parquet|sqlite|db|html|htm|feather
  params:
    output_path: output/data.csv
metadata:
  rows: 10000
columns:
  - name: id
    strategy: UUID_STRATEGY
```

Behavior:
- Orchestrator builds a `FileWriter` from `file_writer`.
- Generates all rows, applies strategies column-by-column, writes once.
- Returns standardized summary (rows, columns, writer info).

### Batch Mode

- **When**: Large datasets that should be written incrementally to files.
- **Processor**: `StreamingConfigProcessor` (batch and streaming share the same processor)
- **Writer**: `BatchWriter` which wraps a concrete file writer defined under `batch.file_writer`.

Batch config:
```yaml
batch:
  batch_size: 5000   # rows per write
  chunk_size: 2000   # generation chunk (<= batch_size)
  file_writer:
    type: parquet
    params:
      output_path: output/data.parquet
```

CLI:
```bash
python main.py generate examples/by-strategy/all_strategies_example.yaml --batch path/to/batch.yaml
```

Behavior:
- Orchestrator detects `--batch` and creates `BatchWriter`.
- `StreamingConfigProcessor` generates rows in chunks, maintaining strategy state across chunks.
- `BatchWriter` tracks `batches_written`, `total_rows_written`, aggregates paths, and finalizes the underlying file writer.

### Streaming Mode

- **When**: Continuous delivery to message queues like Kafka or AMQP.
- **Processor**: `StreamingConfigProcessor`
- **Writer**: `StreamWriter` using `messaging.QueueFactory`.

Stream config (Kafka, flat form):
```yaml
type: kafka
bootstrap_servers: localhost:9092
topic: genxdata.events
batch_size: 1000
chunk_size: 1000
```

Stream config (AMQP, nested form):
```yaml
amqp:
  host: localhost
  port: 5672
  queue: genxdata.events
batch_size: 1000
chunk_size: 1000
```

CLI:
```bash
python main.py generate examples/by-strategy/all_strategies_example.yaml --stream path/to/stream.yaml
```

Behavior:
- Orchestrator detects `--stream` and creates `StreamWriter`.
- `StreamingConfigProcessor` generates chunks and sends batches via the queue producer.
- Queue type detection supports nested (`amqp`/`kafka` key) or flat (`type: amqp|kafka`).

### Column-Level Options

- **mask**: pandas query expression to restrict target rows for a strategy.
- **unique**: strict in normal mode (global set). In streaming/batching only best-effort within a chunk.
- **seed**: where supported by the strategy, seeds randomness for reproducibility.

### Tips

- Ensure `chunk_size <= batch_size` (enforced internally).
- For batch files, set an explicit `output_path` to avoid defaults.
- For streaming, validate connectivity to Kafka/AMQP beforehand.


