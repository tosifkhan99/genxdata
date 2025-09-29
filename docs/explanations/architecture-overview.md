---
title: Architecture Overview
---

# Architecture Overview

This page summarizes the core components and how GenXData operates end‑to‑end.

## Core Components

- Orchestrator (`core/orchestrator.py`): coordinates config loading, strategy execution, and writing.
- Strategies (`core/strategies/*.py`): data generation primitives.
- Processors (`core/processors/*.py`): config processing modes (normal vs streaming).
- Writers (`core/writers/*.py`): output sinks (CSV, Parquet, Kafka, AMQP, etc.).
- Messaging (`messaging/*`): Kafka/AMQP integration.
- CLI (`cli/main_cli.py`) and Python API (`api.py`).

## Flow

1. Load YAML config and validate against strategy configuration (`core/strategy_config.py`).
2. Initialize orchestrator with selected mode (batch/streaming).
3. Create appropriate processor and strategy instances.
4. Generate records and write via configured writer(s).
5. Handle errors with rich exception classes.

Refer to diagrams in `dev-docs/` for class and sequence views.
EOF
