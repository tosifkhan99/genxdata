"""
UUID strategy: generates UUID strings for identifiers.

Formatting options via config:
- hyphens (bool): include dashes in the UUID string (default: True)
- uppercase (bool): return uppercase hex (default: False)
- prefix (str): optional string to prepend (default: "")

Version:
- version (int): 4 or 5. Use UUID4 for random IDs, UUID5 for
  deterministic IDs derived from a namespace and counter. Default: 5.

Notes on uniqueness:
- Both version 4 and 5 produce effectively unique values. This strategy ignores
  any 'unique' flag and does not perform additional uniqueness enforcement.
"""

import uuid

import pandas as pd

from core.base_strategy import BaseStrategy
from core.mixins import StatefulMixin, ValidationMixin


class UuidStrategy(BaseStrategy, StatefulMixin, ValidationMixin):
    """
    Strategy for generating UUID values as strings, with optional formatting.
    """

    def __init__(self, mode: str, logger=None, **kwargs):
        super().__init__(mode=mode, logger=logger, **kwargs)
        # Ignore external uniqueness requests for this strategy
        if getattr(self, "unique", False):
            self.logger.debug(
                "UuidStrategy: ignoring 'unique' flag; both v4 and v5 are unique by design."
            )
            self.unique = False
        self._initialize_state()

    def _initialize_state(self) -> None:
        super()._initialize_state()
        self._include_hyphens: bool = bool(self.params.get("hyphens", True))
        self._uppercase: bool = bool(self.params.get("uppercase", False))
        self._prefix: str = str(self.params.get("prefix", ""))
        self._numbers_only: bool = bool(self.params.get("numbers_only", False))
        self._letters_only: bool = bool(self.params.get("letters_only", False))
        self._version: int = int(self.params.get("version", 5))

        # Deterministic mode for version 5
        self._deterministic: bool = self._version == 5
        self._counter: int = 0

        # Build a stable namespace using seed (if provided) and column name
        seed_val = self.params.get("seed")
        seed_str = str(seed_val) if seed_val is not None else "no-seed"
        # Namespacing by column binds generated IDs to the target column logically
        ns_name = f"genxdata:{self.col_name}:{seed_str}"
        self._namespace = uuid.uuid5(uuid.NAMESPACE_DNS, ns_name)

        self.logger.debug(
            f"UuidStrategy initialized: hyphens={self._include_hyphens}, "
            f"uppercase={self._uppercase}, prefix='{self._prefix}', version={self._version}"
        )

    def _format_uuid(self, u: uuid.UUID) -> str:
        value = str(u)

        if not self._include_hyphens:
            value = value.replace("-", "")

        if self._uppercase:
            value = value.upper()

        if self._numbers_only:
            value = str(u.int)

        if self._prefix:
            value = f"{self._prefix}{value}"

        return value

    def generate_chunk(self, count: int) -> pd.Series:
        self.logger.debug(f"Generating {count} UUID values")

        if self._version == 5:
            start = self._counter
            values = [
                self._format_uuid(uuid.uuid5(self._namespace, f"{start + i}"))
                for i in range(count)
            ]
            self._counter += count
            return pd.Series(values, dtype=object)
        else:
            # UUID4 (random)
            values = [self._format_uuid(uuid.uuid4()) for _ in range(count)]
            return pd.Series(values, dtype=object)

    def reset_state(self) -> None:
        self.logger.debug("Resetting UuidStrategy state")
        super().reset_state()
        self._initialize_state()
