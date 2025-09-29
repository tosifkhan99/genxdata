---
title: Quickstart
---

# Quickstart

This will cover the generation of data using the batch or normal mode.

## Prerequisites

- Python, A package manager -- poetry, uv, pip anything works.
- Repository cloned: `git clone ... && cd GenXData`
- Install the dependencies installed:


```bash
#poetry
poetry sync
#uv
uv sync
```

## Run the example

### Runnnig the normal mode
Use the provided example config to generate data to `output/` or output to your path(see the `file_writer` in your config).
```bash
poetry run python main.py \
  generate \
  examples/by-strategy/all_strategies_example.yaml
```
all_strategies.yaml does contains all the strategies example in a single yaml.

---
## Run the batch example
```bash
poetry run python main.py \
  generate \
  examples/batch_configs/batch_example.yaml \ # your generation config
  --batch examples/batch_configs/batch_example.yaml  # your batch related configs(see batch section in the config)
```

## Run the stream example
```bash
poetry run python main.py \
  generate \
  examples/batch_configs/batch_example.yaml \ # your generation config
  --stream examples/batch_configs/batch_example.yaml
```

Validate the output files under `output/` or your mentioned path. 

## Next steps

- Explore more examples in `examples/`
- See how to write configs in the How‑to guides
EOF
