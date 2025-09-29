---
title: CLI Reference
---

# CLI Reference

Command-line usage and options for GenXData.

## Entry points

- Poetry script: 
- Module: 

## Global options

-  Set logging level. One of: , , , . Default: .
-  Show help.

## Commands

### list-generators

List available generators.

Options:

-  Filter generators by name pattern
-  Show strategy/domain stats summary

Examples:



### show-generator

Show details for a specific generator.

Usage:



### by-strategy

List generators using a given strategy.

Usage:



### create-config

Create a configuration from a generator mapping.

Options:

-  Mapping string like 
-  Path to JSON/YAML mapping file
-  Output file path (required; .yaml/.yml or .json)
-  Number of rows (default: 100)
-  Config name
-  Config description

Examples:



### create-domain-configs

Generate example configurations for multiple domains into .



### generate

Generate data from a configuration file.

Usage:



Options:

-  Use streaming mode with a separate config
-  Use batch file mode with a separate config

Examples:



### stats

Show generator statistics: counts per strategy/domain and available strategies.



## Notes

- Config format can be YAML or JSON. Output writer is chosen by config contents.
- See also:  for required/optional fields.
