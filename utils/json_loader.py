"""
Utility for loading JSON configuration files.
"""

import json


def read_json(filename):
    """Read a JSON file and return its parsed content."""
    with open(filename) as f:
        return json.load(f)
