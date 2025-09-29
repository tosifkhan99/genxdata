"""
File operation utilities for GenXData.
"""

import os

from utils.logging import Logger


def ensure_output_dir(output_path: str, logger: Logger | None = None) -> None:
    """
    Ensure the output directory exists.

    Args:
        output_path (str): Path to the output file
        logger (Logger, optional): Logger instance for debug messages
    """
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        if logger:
            logger.debug(f"Created output directory: {output_dir}")
