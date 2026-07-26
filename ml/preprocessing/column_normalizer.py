"""
Column Name Normalizer

Owns all raw-CSV-header-to-canonical-name normalization logic.
Dataset-agnostic: works for CICIDS2017 today, and any future dataset
(UNSW-NB15, TON-IoT, etc.) without modification, since header quirks
are an ingestion concern, not something any specific dataset's metadata
module should know about.

This module is the SINGLE owner of column-name normalization. No other
module should contain its own column-name-stripping or fuzzy-matching logic.
"""

from __future__ import annotations

import re
from typing import Optional


class ColumnNormalizer:
    """
    Owns all raw-CSV-header-to-canonical-name normalization logic.

    Attributes:
        alias_mapping: Optional dict mapping a raw name to an alternate
                       canonical form. Reserved for future use; ``None``
                       for CICIDS2017.
    """

    def __init__(self, alias_mapping: Optional[dict[str, str]] = None) -> None:
        """
        Initialise the normalizer.

        Args:
            alias_mapping: Optional dict mapping raw names to alternative
                           canonical names. Not used for CICIDS2017 but
                           reserved as an extension point for future datasets.
        """
        self._alias_mapping = alias_mapping or {}

    def normalize_column_name(self, name: str) -> str:
        """
        Normalise a single column name.

        Strips leading/trailing whitespace and collapses internal runs of
        whitespace to a single space. Does NOT change case, since Step 1
        diagnostics showed no case variance across CICIDS2017 files.

        Args:
            name: The raw column name from the source file.

        Returns:
            Normalised column name with whitespace cleaned.
        """
        name = name.strip()
        name = re.sub(r"\s+", " ", name)
        return name

    def normalize_columns(self, columns: list[str]) -> list[str]:
        """
        Apply ``normalize_column_name`` to every element in a column list.

        Args:
            columns: List of raw column names.

        Returns:
            List of normalised column names.
        """
        return [self.normalize_column_name(col) for col in columns]

    def build_column_mapping(self, columns: list[str]) -> dict[str, str]:
        """
        Build a mapping from raw column names to their normalised forms.

        Useful for auditability/logging — callers can log what actually
        changed, rather than normalising silently with no trace.

        Only includes entries where the raw name differs from the
        normalised name.

        Args:
            columns: List of raw column names.

        Returns:
            Dict of ``{raw_name: canonical_name}`` for entries that changed.
        """
        mapping: dict[str, str] = {}
        for col in columns:
            normalised = self.normalize_column_name(col)
            if normalised != col:
                mapping[col] = normalised
        return mapping

    @staticmethod
    def to_canonical_name(name: str) -> str:
        """
        Convert a column name to a canonical snake_case form.

        This is used for config-driven feature catalogue lookups (e.g.
        converting YAML feature names like ``"Destination Port"`` to
        ``"destination_port"``). It is NOT applied to raw CSV headers at
        load time — only ``normalize_column_name()`` is used there.

        Args:
            name: The column name to convert.

        Returns:
            Snake_case canonical name.
        """
        return (
            name.strip()
            .lower()
            .replace(" ", "_")
            .replace("/", "_")
            .replace(".", "_")
            .replace("-", "_")
        )
