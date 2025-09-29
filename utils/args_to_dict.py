"""
Utilities to convert CLI-like keyword arguments into dictionaries.

Note: This is a thin wrapper around `dict(**kwargs)` for call sites that prefer
an explicit utility function.
"""


def args_to_dict(**params):
    return dict(params)
