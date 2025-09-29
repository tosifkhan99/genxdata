"""
GenXData - Synthetic Data Generation Tool
Main entry point for the application.

For programmatic use, use the DataOrchestrator class:
    from core.orchestrator import DataOrchestrator

    orchestrator = DataOrchestrator(config)
    result = orchestrator.run()

For CLI use, run this file directly:
    python main.py <config_path> [options]
"""

from cli.main_cli import main

if __name__ == "__main__":
    main()
