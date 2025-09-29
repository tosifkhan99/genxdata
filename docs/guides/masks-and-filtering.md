---
title: Masks & Filtering
---

### Masks & Filtering

Use a pandas query expression in the top-level column field `mask` to restrict which rows a strategy applies to.

Example:
```yaml
- name: discount
  strategy: RANDOM_NUMBER_RANGE_STRATEGY
  params: { start: 5, end: 20 }
  mask: "segment == 'VIP' and country == 'US'"
```

Validation & preview:
- Masks are validated before execution; invalid masks raise errors with context.
- Internally, a safe preview path can estimate how many rows match prior to applying.

Tips:
- Reference existing columns only; ensure they are generated earlier or exist in input.
- Keep expressions simple and test iteratively.
- In streaming/batch, masks apply per chunk; ensure logic is stable across chunks.


