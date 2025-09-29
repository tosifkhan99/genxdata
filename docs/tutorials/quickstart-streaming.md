---
title: Quickstart (Streaming)
---

# Quickstart (Streaming)

This guide runs GenXData in streaming mode to a message broker.

## Prerequisites

- Python and Poetry installed
- Broker locally (Kafka or AMQP) via Docker Compose

```bash
docker compose up -d
```

## Run streaming

```bash
poetry run python main.py \
  --config examples/stream_configs/streaming_example.yaml \
  --mode streaming
```

Check the target topic/queue with the tools in `tools/`.

## Next steps

- See messaging guides for Kafka/AMQP configuration
- Validate continuity and ordering with the tests and tools provided
EOF
