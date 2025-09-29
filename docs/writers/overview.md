---
title: Writers Overview
---

### Writers Overview

Supported writers and config examples.

### Normal Mode (file_writer)

Supported types: `csv`, `json`, `excel` (`xlsx`, `xls`), `parquet`, `sqlite` (`db`), `html` (`htm`), `feather`.

Config example:
```yaml
file_writer:
  type: parquet
  params:
    output_path: output/data.parquet
```

Notes:
- Type is case-insensitive; `_WRITER` suffix is normalized.
- If `params` are empty, a default `output_path` is injected.

### Batch Mode (batch.file_writer)

```yaml
batch:
  batch_size: 5000
  chunk_size: 2000
  file_writer:
    type: csv
    params:
      output_path: output/data.csv
```

`BatchWriter` wraps the concrete file writer and tracks batch counters.

### Streaming (queues)

Stream writer uses messaging producers for Kafka/AMQP.

Kafka (flat form):
```yaml
type: kafka
bootstrap_servers: localhost:9092
topic: genxdata.events
batch_size: 1000
chunk_size: 1000
```

AMQP (nested form):
```yaml
amqp:
  host: localhost
  port: 5672
  queue: genxdata.events
batch_size: 1000
chunk_size: 1000
```

See How‑to → Messaging for connection options and examples.


