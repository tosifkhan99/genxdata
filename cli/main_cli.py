"""
GenXData Command-Line Interface

A comprehensive CLI tool for managing generators, creating configurations, and generating
synthetic data. This interface provides easy access to GenXData's 175+ generators across
9 domains, with support for 13 different data generation strategies.

OVERVIEW:
    The CLI is organized into several subcommands, each serving a specific purpose:
    - list-generators: Explore available generators with filtering and statistics
    - show-generator: Get detailed information about specific generators
    - by-strategy: Find generators using specific strategies
    - create-config: Build configuration files from generator mappings
    - create-domain-configs: Generate domain-specific example configurations
    - generate: Generate synthetic data from configuration files
    - stats: Display comprehensive generator statistics

INSTALLATION:
    poetry install

GLOBAL OPTIONS:
    --help              Show help message and available commands
    --log-level, -l     Set logging level (DEBUG, INFO, WARN, ERROR)

COMMANDS:

    list-generators [OPTIONS]
        List available generators with optional filtering and statistics.

        Options:
            --filter, -f PATTERN    Filter generators by name pattern
            --show-stats           Show comprehensive statistics

        Examples:
            python -m cli.main_cli list-generators
            python -m cli.main_cli list-generators --filter NAME
            python -m cli.main_cli list-generators --show-stats
            python -m cli.main_cli --log-level DEBUG list-generators --filter NAME

    show-generator GENERATOR_NAME
        Show detailed information about a specific generator, including strategy and parameters.

        Examples:
            python -m cli.main_cli show-generator PERSON_NAME
            python -m cli.main_cli show-generator EMAIL_PATTERN

    by-strategy STRATEGY_NAME
        List all generators using a specific strategy.

        Examples:
            python -m cli.main_cli by-strategy RANDOM_NAME_STRATEGY
            python -m cli.main_cli by-strategy DATE_GENERATOR_STRATEGY

    create-config [OPTIONS]
        Create configuration files from generator mappings.

        Options:
            --mapping, -m MAPPING       Generator mapping: "col1:gen1,col2:gen2"
            --mapping-file FILE        File containing generator mapping (JSON/YAML)
            --output, -o FILE          Output configuration file path (required)
            --rows, -r NUMBER          Number of rows to generate (default: 100)
            --name NAME                Configuration name
            --description DESC         Configuration description

        Examples:
            python -m cli.main_cli create-config \
                --mapping "name:FULL_NAME,age:PERSON_AGE,email:EMAIL_PATTERN" \
                --output test_config.json --rows 50

            python -m cli.main_cli create-config \
                --mapping-file mapping.json --output config.yaml --rows 500

    create-domain-configs
        Create example configurations for various domains (ecommerce, healthcare, education, etc.).

        Examples:
            python -m cli.main_cli create-domain-configs

    generate CONFIG_FILE [OPTIONS]
        Generate synthetic data from configuration files.

        Options:
            --stream STREAM_CONFIG    Use streaming mode with queue integration
            --batch BATCH_CONFIG      Use batch file mode for large datasets
            --perf-report             Print performance timing report after generation

        Examples:
            python -m cli.main_cli generate test_config.json
            python -m cli.main_cli generate examples/simple_random_number_example.yaml
            python -m cli.main_cli --log-level DEBUG generate config.yaml
            python -m cli.main_cli generate config.yaml \
                --stream examples/streaming_config_example.yaml
            python -m cli.main_cli generate config.yaml \
                --batch examples/batch_config_csv.yaml
            python -m cli.main_cli generate config.yaml --perf-report

    stats
        Display comprehensive generator statistics including totals, strategy
        distribution, domain distribution, and available strategies.

        Examples:
            python -m cli.main_cli stats

DOMAINS AND GENERATORS:
    GenXData includes 175 generators across 9 domains:
    - Generic (25): Basic data types, IDs, patterns
    - Geographic (24): Addresses, coordinates, locations
    - IoT Sensors (23): Device data, telemetry, readings
    - Education (22): Academic data, courses, grades
    - Business (21): Company data, financial metrics
    - Healthcare (21): Medical data, patient information
    - Technology (20): Software, hardware, tech specs
    - Transportation (19): Vehicle data, logistics
    - Ecommerce (18): Product data, pricing, orders

AVAILABLE STRATEGIES:
    - DATE_GENERATOR_STRATEGY: Generate date values within ranges
    - DELETE_STRATEGY: Delete values from columns
    - DISTRIBUTED_CHOICE_STRATEGY: Generate categorical data with custom distributions
    - DISTRIBUTED_DATE_RANGE_STRATEGY: Generate dates with custom distributions
    - DISTRIBUTED_NUMBER_RANGE_STRATEGY: Generate numbers with custom distributions
    - DISTRIBUTED_TIME_RANGE_STRATEGY: Generate times with custom distributions
    - RANDOM_NUMBER_RANGE_STRATEGY: Generate numbers within ranges
    - PATTERN_STRATEGY: Generate data matching regex patterns
    - RANDOM_NAME_STRATEGY: Generate random names
    - REPLACEMENT_STRATEGY: Replace specific values
    - SERIES_STRATEGY: Generate series of values
    - TIME_RANGE_STRATEGY: Generate time values within ranges
    - CONCAT_STRATEGY: Concatenate values from other columns

IMPORTANT NOTES:
    - Configuration formats: Both JSON and YAML are supported
    - Output format is determined by file extension
    - All commands include comprehensive error handling and validation

EXAMPLES:
    # Explore available generators
    python -m cli.main_cli list-generators --show-stats

    # Create a user profile dataset
    python -m cli.main_cli create-config \
        --mapping "user_id:USER_ID,name:FULL_NAME,email:EMAIL_PATTERN,age:PERSON_AGE" \
        --output user_profiles.yaml --rows 1000

    # Generate the data
    python -m cli.main_cli generate user_profiles.yaml

    # Create domain examples and generate healthcare data with debug output
    python -m cli.main_cli create-domain-configs
    python -m cli.main_cli --log-level DEBUG generate output/healthcare_config.yaml

For more information, visit: https://github.com/tosifkhan99/GenXData
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

# Add the parent directory to the path so we can import from utils
sys.path.append(str(Path(__file__).parent.parent))

from core.orchestrator import DataOrchestrator
from utils.generator_utils import (
    create_domain_configs_example,
    generator_to_config,
    get_generator_info,
    get_generator_stats,
    get_generators_by_strategy,
    list_available_generators,
    save_config_as_json,
    save_config_as_yaml,
    validate_generator_config,
)
from utils.logging import Logger

# Initialize CLI logger
logger = Logger.get_logger("cli")


def list_generators_command(args):
    """List available generators."""
    try:
        generators = list_available_generators(args.filter)

        if not generators:
            if args.filter:
                logger.info(f"No generators found matching filter: {args.filter}")
            else:
                logger.info("No generators found")
            return

        logger.info(f"Available generators ({len(generators)}):")
        for i, gen_name in enumerate(generators, 1):
            logger.info(f"  {i:3d}. {gen_name}")

        if args.show_stats:
            stats = get_generator_stats()
            logger.info("\nStatistics:")
            logger.info(f"  Total generators: {stats['total_generators']}")
            logger.info("  Strategy distribution:")
            for strategy, count in sorted(stats["strategy_distribution"].items()):
                logger.info(f"    {strategy}: {count}")

    except Exception as e:
        logger.error(f"Failed to list generators: {e}")


def show_generator_command(args):
    """Show detailed information about a specific generator."""
    try:
        generator_info = get_generator_info(args.name)
        logger.info(f"Generator: {args.name}")
        logger.info(f"Strategy: {generator_info['implementation']}")
        logger.info("Parameters:")
        for param, value in generator_info["params"].items():
            logger.info(f"  {param}: {value}")

    except Exception as e:
        logger.error(f"Failed to show generator '{args.name}': {e}")


def generators_by_strategy_command(args):
    """List generators using a specific strategy."""
    try:
        generators = get_generators_by_strategy(args.strategy)

        if not generators:
            logger.info(f"No generators found using strategy: {args.strategy}")
            return

        logger.info(f"Generators using {args.strategy} ({len(generators)}):")
        for i, gen_name in enumerate(generators, 1):
            logger.info(f"  {i:3d}. {gen_name}")

    except Exception as e:
        logger.error(f"Failed to list generators by strategy '{args.strategy}': {e}")


def create_config_command(args):
    """Create a configuration file from generators."""
    try:
        # Parse generator mapping from input
        if args.mapping_file:
            logger.debug(f"Loading generator mapping from file: {args.mapping_file}")
            # Load from file
            with open(args.mapping_file) as f:
                if args.mapping_file.endswith(".json"):
                    generator_mapping = json.load(f)
                else:
                    generator_mapping = yaml.safe_load(f)
        else:
            # Parse from command line args
            if not args.mapping:
                logger.error("Either --mapping-file or --mapping must be provided")
                return

            logger.debug(f"Parsing generator mapping from command line: {args.mapping}")
            # Parse mapping from string: "col1:gen1,col2:gen2"
            generator_mapping = {}
            for pair in args.mapping.split(","):
                if ":" not in pair:
                    logger.error(
                        f"Invalid mapping format '{pair}'. Use 'column:generator'"
                    )
                    return
                col, gen = pair.strip().split(":", 1)
                generator_mapping[col.strip()] = gen.strip()

        logger.debug(
            f"Creating configuration with {len(generator_mapping)} column mappings"
        )

        # Create configuration
        config = generator_to_config(
            generator_mapping,
            num_rows=args.rows,
            metadata={
                "name": args.name or "generated_config",
                "description": args.description or "Generated configuration from CLI",
                "version": "1.0.0",
            },
        )

        # Validate configuration
        validate_generator_config(config)

        # Save configuration
        if args.output.endswith(".yaml") or args.output.endswith(".yml"):
            save_config_as_yaml(config, args.output)
        else:
            save_config_as_json(config, args.output)

        logger.info(f"Configuration saved to {args.output}")

    except Exception as e:
        logger.error(f"Failed to create configuration: {e}")


def create_domain_configs_command(args):
    """Create example domain configurations."""
    try:
        logger.debug("Creating domain configuration examples")
        create_domain_configs_example()
        logger.info("Domain configuration examples created in ./output/")

    except Exception as e:
        logger.error(f"Failed to create domain configurations: {e}")


def generate_data_command(args):
    """Generate data using a configuration file."""
    try:
        logger.debug(f"Loading configuration from: {args.config}")

        # Load configuration
        if args.config.endswith(".yaml") or args.config.endswith(".yml"):
            with open(args.config) as f:
                config = yaml.safe_load(f)
        else:
            # Support for json configuration
            with open(args.config) as f:
                config = json.load(f)

        # Validate configuration
        validate_generator_config(config)

        logger.debug("Creating data orchestrator")

        # Determine processing mode
        if hasattr(args, "stream") and args.stream:
            logger.info(f"Running in streaming mode with config: {args.stream}")
        elif hasattr(args, "batch") and args.batch:
            logger.info(f"Running in batch mode with config: {args.batch}")
        else:
            logger.info("Running in standard mode")

        # Validate stream & batch config
        if args.stream:
            with open(args.stream) as f:
                stream_config = yaml.safe_load(f)
            validate_generator_config(stream_config)
        if args.batch:
            with open(args.batch) as f:
                batch_config = yaml.safe_load(f)
            validate_generator_config(batch_config)

        # Create orchestrator and run with streaming/batch support
        orchestrator = DataOrchestrator(
            config,
            log_level=args.log_level,
            stream=getattr(args, "stream", None),
            batch=getattr(args, "batch", None),
            perf_report=getattr(args, "perf_report", False),
        )
        result = orchestrator.run()
        logger.info(f"Data generation completed with result {result}")
        logger.info(f"Data generation completed using {args.config}")

        # Print performance report if requested
        if getattr(args, "perf_report", False):
            try:
                from utils.performance_timer import get_performance_report

                report_text = get_performance_report()
                if report_text and report_text.strip():
                    print("\nPerformance Report:\n" + report_text)
                else:
                    logger.info("No performance data collected.")
            except Exception as e:
                logger.error(f"Failed to print performance report: {e}")

    except KeyError as keyError:
        logger.error(f"KeyError with config {args.config} : {keyError}")
    except Exception as e:
        logger.error(f"Failed to generate data from '{args.config}': {e.__class__}")


def stats_command(args):
    """Show generator statistics."""
    try:
        stats = get_generator_stats()

        logger.info("Generator Statistics")
        logger.info("=" * 40)
        logger.info(f"Total generators: {stats['total_generators']}")

        logger.info("\nStrategy distribution:")
        for strategy, count in sorted(stats["strategy_distribution"].items()):
            logger.info(f"  {strategy}: {count}")

        logger.info("\nDomain distribution:")
        for domain, count in sorted(stats["domain_distribution"].items()):
            if count > 0:
                logger.info(f"  {domain}: {count}")

        logger.info(f"\nAvailable strategies: {len(stats['available_strategies'])}")
        for strategy in sorted(stats["available_strategies"]):
            logger.info(f"  - {strategy}")

    except Exception as e:
        logger.error(f"Failed to show statistics: {e}")


def main():
    """Main CLI entry point."""

    parser = argparse.ArgumentParser(
        description="GenXData CLI - Data Generation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all generators
  python -m cli.main_cli list-generators

  # List generators matching a filter
  python -m cli.main_cli list-generators --filter NAME

  # Show details of a specific generator
  python -m cli.main_cli show-generator PERSON_NAME

  # List generators using a specific strategy
  python -m cli.main_cli by-strategy RANDOM_NAME_STRATEGY

  # Create a configuration from generators
  python -m cli.main_cli create-config --mapping "name:FULL_NAME,age:PERSON_AGE" --output config.json

  # Generate data from configuration
  python -m cli.main_cli generate config.json

  # Generate data with streaming to AMQP queue
  python -m cli.main_cli generate config.json --stream streaming_config.yaml

  # Generate data in batch files
  python -m cli.main_cli generate config.json --batch batch_config.yaml

  # Show generator statistics
  python -m cli.main_cli stats
        """,
    )
    # Add global arguments

    # Create subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add log-level argument
    parser.add_argument(
        "--log-level",
        "-l",
        type=str,
        default="INFO",
        help="Set logging level (DEBUG, INFO, WARN, ERROR)",
    )

    # List generators command
    list_parser = subparsers.add_parser(
        "list-generators", help="List available generators"
    )
    list_parser.add_argument(
        "--filter", "-f", type=str, help="Filter generators by name pattern"
    )
    list_parser.add_argument(
        "--show-stats", action="store_true", help="Show statistics with the list"
    )
    list_parser.set_defaults(func=list_generators_command)

    # Show generator command
    show_parser = subparsers.add_parser(
        "show-generator", help="Show detailed generator information"
    )
    show_parser.add_argument("name", type=str, help="Name of the generator to show")
    show_parser.set_defaults(func=show_generator_command)

    # Generators by strategy command
    strategy_parser = subparsers.add_parser(
        "by-strategy", help="List generators using a strategy"
    )
    strategy_parser.add_argument(
        "strategy", type=str, help="Strategy name (e.g., RANDOM_NAME_STRATEGY)"
    )
    strategy_parser.set_defaults(func=generators_by_strategy_command)

    # Create config command
    config_parser = subparsers.add_parser(
        "create-config", help="Create configuration from generators"
    )
    config_parser.add_argument(
        "--mapping", "-m", type=str, help='Generator mapping: "col1:gen1,col2:gen2"'
    )
    config_parser.add_argument(
        "--mapping-file", type=str, help="File containing generator mapping (JSON/YAML)"
    )
    config_parser.add_argument(
        "--output", "-o", type=str, required=True, help="Output configuration file path"
    )
    config_parser.add_argument(
        "--rows", "-r", type=int, default=100, help="Number of rows to generate"
    )
    config_parser.add_argument("--name", type=str, help="Configuration name")
    config_parser.add_argument(
        "--description", type=str, help="Configuration description"
    )
    config_parser.set_defaults(func=create_config_command)

    # Create domain configs command
    # todo: do we need this command?
    domain_parser = subparsers.add_parser(
        "create-domain-configs", help="Create example domain configurations"
    )
    domain_parser.set_defaults(func=create_domain_configs_command)

    # Generate data command
    generate_parser = subparsers.add_parser(
        "generate", help="Generate data from configuration"
    )
    generate_parser.add_argument("config", type=str, help="Configuration file path")
    generate_parser.add_argument(
        "--stream", type=str, help="Path to a configuration file for streaming mode"
    )
    generate_parser.add_argument(
        "--batch", type=str, help="Path to a configuration file for batch mode"
    )
    generate_parser.add_argument(
        "--perf-report",
        action="store_true",
        help="Enable performance timing report",
    )
    generate_parser.set_defaults(func=generate_data_command)

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show generator statistics")
    stats_parser.set_defaults(func=stats_command)

    # Parse arguments
    args = parser.parse_args()

    # Configure logger with user-specified log level
    Logger.configure_all_loggers(
        {
            "log_level": args.log_level,
            "format_detailed": args.log_level.upper() == "DEBUG",
        }
    )

    logger.debug(f"CLI started with command: {args.command}")

    # Execute command
    if not args.command:
        parser.print_help()
        return

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
