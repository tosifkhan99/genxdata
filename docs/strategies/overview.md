---
title: Strategies Overview
---

### Strategies Overview

One‑line summaries with links to reference. Use these names in `columns[].strategy`.

- RANDOM_NUMBER_RANGE_STRATEGY: Random integers/floats within [min, max].
- DISTRIBUTED_NUMBER_RANGE_STRATEGY: Number range with custom distribution.
- RANDOM_DATE_RANGE_STRATEGY (DATE_GENERATOR_STRATEGY): Random dates in range.
- DATE_SERIES_STRATEGY: Sequential dates with step/frequency.
- DISTRIBUTED_DATE_RANGE_STRATEGY: Date range with custom distribution.
- PATTERN_STRATEGY: Pattern-based strings (format tokens, regex-like pieces).
- SERIES_STRATEGY: Sequential/iterative series over values.
- DISTRIBUTED_CHOICE_STRATEGY: Weighted choices from a list or source.
- TIME_RANGE_STRATEGY: Random time of day range.
- DISTRIBUTED_TIME_RANGE_STRATEGY: Time with custom distribution.
- REPLACEMENT_STRATEGY: Replace values based on mapping rules.
- CONCAT_STRATEGY: Concatenate values/columns using a template.
- RANDOM_NAME_STRATEGY: Random person names.
- DELETE_STRATEGY: Null out values for masked rows.
- MAPPING_STRATEGY: Join/lookup from external file via key(s).
- UUID_STRATEGY: Generate UUIDs.

Example column:
```yaml
- name: order_id
  strategy: CONCAT_STRATEGY
  params:
    template: "ORD-{year}-{seq}"
```

See detailed API docs under Reference → Strategies for full parameters.


