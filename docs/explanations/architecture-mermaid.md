---
title: Architecture (Mermaid)
---

# Architecture (Mermaid)

```mermaid
%% GenXData - High-level Architecture Overview (Mermaid)
%% This diagram shows the main runtime flow and module boundaries.

graph TD
  C["Frontend / CLI / Tools"] -->|HTTP JSON| API["FastAPI app (api.py)"]

  API -->|validate| VAL["utils.generator_utils.validate_generator_config"]
  API -->|run()| ORCH["DataOrchestrator"]

  ORCH -->|normal| NPROC["NormalConfigProcessor"]
  ORCH -->|stream/batch| SPROC["StreamingConfigProcessor"]
  ORCH -->|_create_writer()| WSEL{{"Writer selection"}}
  WSEL -->|file_writer| FFACT["FileWriterFactory"]
  WSEL -->|stream| SWR["StreamWriter"]
  WSEL -->|batch| BWR["BatchWriter"]

  NPROC -->|process()| W["BaseWriter"]
  SPROC -->|process()| BWR

  NPROC --> SF["StrategyFactory"]
  SPROC --> SF
  SF --> SMAP["strategy_mapping (get_* functions)"]
  SF --> BSTR["BaseStrategy + Mixins"]
  SF --> BCFG["BaseConfig + Configs"]

  FFACT --> BFW["BaseFileWriter"]
  BFW --> CSV["CsvFileWriter"]
  BFW --> JSON["JsonFileWriter"]
  BFW --> XLSX["ExcelFileWriter"]
  BFW --> PARQ["ParquetFileWriter"]
  BFW --> FTHR["FeatherFileWriter"]
  BFW --> HTML["HtmlFileWriter"]
  BFW --> SQLITE["SqliteFileWriter"]

  SWR -.-> QF["QueueFactory"]
  QF --> QCFG["QueueConfig"]
  QCFG --> AMQPCFG["AMQPConfig"]
  QCFG --> KAFKACFG["KafkaConfig"]
  QF --> QPROD["QueueProducer"]
  QPROD --> AMQPPROD["AMQPProducer"]
  QPROD --> KAFKAPROD["KafkaProducer"]

  CSV --> OUT1["Files in output/ (CSV)"]
  JSON --> OUT2["Files in output/ (JSON)"]
  XLSX --> OUT3["Files in output/ (Excel)"]
  PARQ --> OUT4["Files in output/ (Parquet)"]
  FTHR --> OUT5["Files in output/ (Feather)"]
  HTML --> OUT6["Files in output/ (HTML)"]
  SQLITE --> OUT7["SQLite DB file"]
  SWR --> QOUT["Message Queues (AMQP/Kafka)"]

  classDef mod fill:#eef,stroke:#88a,stroke-width:1px;
  class API,ORCH,NPROC,SPROC,SF,FFACT,SWR,BWR,QF,QCFG,QPROD,SMAP,BSTR,BCFG,VAL mod;
```
