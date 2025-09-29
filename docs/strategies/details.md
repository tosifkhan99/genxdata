---
title: Strategies – Detailed Guide
---

### How to use

Each column defines a `strategy` and `params`. Optional fields at column level: `mask`, `unique`, `seed` (strategy-dependent).

```yaml
columns:
  - name: age
    strategy: RANDOM_NUMBER_RANGE_STRATEGY
    params:
      start: 18
      end: 65
      step: 1
      precision: 0
    unique: false
    mask: "country == 'US'"
```

---

### RANDOM_NUMBER_RANGE_STRATEGY
- Generates numbers in [start, end) with optional step and precision.
- Params: `start` (default 0), `end` (default 99), `step` (default 1), `precision` (default 0), `unique` (default false)

Example:
```yaml
- name: age
  strategy: RANDOM_NUMBER_RANGE_STRATEGY
  params: { start: 18, end: 65, step: 1, precision: 0 }
```

---

### DISTRIBUTED_NUMBER_RANGE_STRATEGY
- Piecewise number ranges with weights summing to 100.
- Params: `ranges: [{ start, end, distribution }]`

Example:
```yaml
- name: items
  strategy: DISTRIBUTED_NUMBER_RANGE_STRATEGY
  params:
    ranges:
      - { start: 1, end: 5, distribution: 70 }
      - { start: 5, end: 10, distribution: 30 }
```

---

### RANDOM_DATE_RANGE_STRATEGY (alias: DATE_GENERATOR_STRATEGY)
- Random date between start and end, formatted to `output_format`.
- Params: `start_date` ("2020-1-31"), `end_date` ("2020-12-31"), `format` ("%Y-%m-%d"), `output_format` ("%Y-%m-%d")

Example:
```yaml
- name: signup_date
  strategy: RANDOM_DATE_RANGE_STRATEGY
  params: { start_date: "2023-01-01", end_date: "2023-12-31", output_format: "%Y-%m-%d" }
```

---

### DATE_SERIES_STRATEGY
- Sequential date series starting at `start_date` with frequency `freq`.
- Params: `start_date` ("2024-01-01"), `freq` ("D"), `format`, `output_format`

Example:
```yaml
- name: day
  strategy: DATE_SERIES_STRATEGY
  params: { start_date: "2024-01-01", freq: "D" }
```

---

### DISTRIBUTED_DATE_RANGE_STRATEGY
- Weighted date ranges. Weights must sum to 100.
- Params: `ranges: [{ start_date, end_date, format, output_format, distribution }]`

Example:
```yaml
- name: promo_period
  strategy: DISTRIBUTED_DATE_RANGE_STRATEGY
  params:
    ranges:
      - { start_date: "2023-01-01", end_date: "2023-03-31", format: "%Y-%m-%d", output_format: "%Y-%m-%d", distribution: 60 }
      - { start_date: "2023-04-01", end_date: "2023-06-30", format: "%Y-%m-%d", output_format: "%Y-%m-%d", distribution: 40 }
```

---

### PATTERN_STRATEGY
- Generate strings following a regex pattern.
- Params: `regex` (default `^[A-Za-z0-9]+$`)

Example:
```yaml
- name: sku
  strategy: PATTERN_STRATEGY
  params: { regex: "[A-Z]{3}[0-9]{5}" }
```

---

### SERIES_STRATEGY
- Numeric series with start and step.
- Params: `start` (1), `step` (1)

Example:
```yaml
- name: line_no
  strategy: SERIES_STRATEGY
  params: { start: 1, step: 1 }
```

---

### DISTRIBUTED_CHOICE_STRATEGY
- Weighted choices; total weight = 100.
- Params: `choices: { value: weight, ... }`

Example:
```yaml
- name: segment
  strategy: DISTRIBUTED_CHOICE_STRATEGY
  params:
    choices:
      VIP: 5
      Pro: 15
      Free: 80
```

---

### TIME_RANGE_STRATEGY
- Random time between `start_time` and `end_time` (supports overnight by lexical precedence).
- Params: `start_time` ("00:00:00"), `end_time` ("23:59:59"), `format` ("%H:%M:%S")

Example:
```yaml
- name: event_time
  strategy: TIME_RANGE_STRATEGY
  params: { start_time: "09:00:00", end_time: "18:00:00" }
```

---

### DISTRIBUTED_TIME_RANGE_STRATEGY
- Weighted time windows; weights sum to 100. Optional `seed` for reproducibility.
- Params: `seed`, `ranges: [{ start, end, format, distribution }]`

Example:
```yaml
- name: access_time
  strategy: DISTRIBUTED_TIME_RANGE_STRATEGY
  params:
    seed: 42
    ranges:
      - { start: "08:00:00", end: "12:00:00", format: "%H:%M:%S", distribution: 60 }
      - { start: "12:00:01", end: "18:00:00", format: "%H:%M:%S", distribution: 40 }
```

---

### REPLACEMENT_STRATEGY
- Replace occurrences of `from_value` with `to_value`.
- Params: `from_value` ("a"), `to_value` ("b")

Example:
```yaml
- name: country
  strategy: REPLACEMENT_STRATEGY
  params: { from_value: "UK", to_value: "GB" }
```

---

### CONCAT_STRATEGY
- Concatenate columns with optional prefix/suffix/separator.
- Params: `lhs_col`, `rhs_col`, `separator`, `prefix`, `suffix`

Example:
```yaml
- name: order_id
  strategy: CONCAT_STRATEGY
  params: { lhs_col: "region", rhs_col: "seq", separator: "-", prefix: "ORD-" }
```

---

### RANDOM_NAME_STRATEGY
- Generate names; supports first/last/full, gender and case.
- Params: `name_type` (first|last|full), `gender` (male|female|any), `case` (title|upper|lower)

Example:
```yaml
- name: customer_name
  strategy: RANDOM_NAME_STRATEGY
  params: { name_type: "full", gender: "any", case: "title" }
```

---

### MAPPING_STRATEGY
- Map values using either an inline dict or an external file.
- Params (either/or):
  - Inline: `map_from`, `mapping: { from_value: to_value, ... }`
  - File: `map_from`, `source`, `source_column`

Example (inline):
```yaml
- name: country_code
  strategy: MAPPING_STRATEGY
  params:
    map_from: country
    mapping:
      United Kingdom: GB
      United States: US
```

Example (file):
```yaml
- name: country_code
  strategy: MAPPING_STRATEGY
  params:
    map_from: country
    source: data/country_map.csv
    source_column: country
```

---

### DELETE_STRATEGY
- Null out values (use with a `mask` to target rows).
- Params: none

Example:
```yaml
- name: phone
  strategy: DELETE_STRATEGY
  mask: "do_not_contact == true"
```

---

### UUID_STRATEGY
- Generate UUIDs with formatting controls.
- Params: `hyphens` (true), `uppercase` (false), `prefix` (""), `unique` (false), `numbers_only` (false), `version` (4|5)

Example:
```yaml
- name: user_id
  strategy: UUID_STRATEGY
  params: { hyphens: true, uppercase: false, prefix: "", version: 4 }
```


