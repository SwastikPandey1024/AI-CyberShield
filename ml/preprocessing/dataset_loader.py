"""
Dataset Loader

Responsible for loading raw cybersecurity datasets from disk into pandas DataFrames.

This module handles:
- File path validation
- Supported format detection (CSV, Parquet)
- Basic file integrity checks
- Consistent DataFrame return contracts
- Post-load column renaming via config-driven feature catalogue

INTEGRATION WITH CONFIG:
    The loader now accepts an optional ``feature_catalogue`` (from ``data_dictionary``
    module). When provided, ``load_with_standardisation()`` automatically renames raw
    columns to canonical names using the catalogue's mapping, ensuring the returned
    DataFrame always uses standardised column names regardless of the source file format.

    This means:
    - ``load(path)``         → returns raw DataFrame (unchanged behaviour)
    - ``load_with_standardisation(path)`` → returns DataFrame with canonical column names

TODO:
    - Add support for streaming large files in chunks.
    - Add remote/URL source loading (S3, HTTP).
    - Add optional hash-based integrity verification.
    - Add column subset filtering via the feature catalogue.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


class DatasetLoadError(Exception):
    """Raised when a dataset cannot be loaded due to path, format, or integrity issues."""


class DatasetLoader:
    """
    Loads raw datasets from disk into pandas DataFrames.

    Supports CSV and Parquet formats with path validation and basic integrity checks.
    Optionally integrates with the config-driven feature catalogue for post-load
    column standardisation.

    Usage:
        loader = DatasetLoader()
        df = loader.load("datasets/raw/CICIDS2017/MachineLearningCVE/Monday-WorkingHours.pcap_ISCX.csv")

        # With feature catalogue standardisation:
        from ml.preprocessing.data_dictionary import get_raw_to_canonical_mapping
        loader = DatasetLoader()
        df = loader.load_with_standardisation(
            "datasets/raw/CICIDS2017/Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv",
            rename_map=get_raw_to_canonical_mapping()
        )

    TODO:
        - Add support for streaming large files in chunks.
        - Add remote/URL source loading (S3, HTTP).
        - Add optional hash-based integrity verification.
        - Add sampling parameter for quick exploration.
    """

    SUPPORTED_EXTENSIONS: set[str] = {".csv", ".parquet", ".parq"}

    def __init__(self, base_path: Optional[Path] = None) -> None:
        """
        Initialise the loader with an optional base path.

        Args:
            base_path: Root directory for dataset lookups.
                       If None, absolute paths are expected.
        """
        self._base_path = Path(base_path) if base_path else None

    def load(self, path: str | Path) -> pd.DataFrame:
        """
        Load a dataset from the given path into a pandas DataFrame.

        Resolves relative paths against the configured base_path if provided.
        Validates the path exists, is a file, and has a supported extension.

        Args:
            path: File path to the dataset. Can be absolute or relative.

        Returns:
            pd.DataFrame containing the dataset contents.

        Raises:
            DatasetLoadError: If the path is invalid, format is unsupported,
                              or the file cannot be read.
            FileNotFoundError: If the resolved path does not exist.

        TODO:
            - Implement chunked loading for files exceeding memory thresholds.
            - Add automatic compression detection (.gz, .zip).
        """
        resolved_path = self._resolve_path(path)
        self._validate_path(resolved_path)
        extension = resolved_path.suffix.lower()
        return self._read_file(resolved_path, extension)

    def load_with_standardisation(
        self,
        path: str | Path,
        rename_map: dict[str, str] | None = None,
    ) -> pd.DataFrame:
        """
        Load a dataset and standardise column names using a rename mapping.

        Args:
            path: File path to the dataset.
            rename_map: Dict mapping raw column names (as they appear in the file)
                        to canonical column names. If None, raw names are kept.

        Returns:
            pd.DataFrame with renamed columns.

        Raises:
            DatasetLoadError: If loading fails.

        Example:
            >>> from ml.preprocessing.data_dictionary import get_raw_to_canonical_mapping
            >>> loader = DatasetLoader()
            >>> df = loader.load_with_standardisation(
            ...     "path/to/file.csv",
            ...     rename_map=get_raw_to_canonical_mapping()
            ... )
            >>> list(df.columns)[:3]
            ['destination_port', 'flow_duration', 'total_fwd_packets']
        """
        df = self.load(path)

        if rename_map:
            # Only rename columns that actually exist in the DataFrame
            existing_cols = set(df.columns)
            filtered_map = {raw: can for raw, can in rename_map.items() if raw in existing_cols}
            df = df.rename(columns=filtered_map)

        return df

    def load_and_validate(
        self,
        path: str | Path,
        rename_map: dict[str, str] | None = None,
    ) -> pd.DataFrame:
        """
        Load, standardise, and validate a dataset in one call.

        A convenience method for the common load → rename → validate pipeline.

        Args:
            path: File path to the dataset.
            rename_map: Optional dict mapping raw to canonical column names.

        Returns:
            Standardised pd.DataFrame.

        Raises:
            DatasetLoadError: If loading or validation fails.
        """
        from ml.preprocessing.dataset_validator import DatasetValidator

        df = self.load_with_standardisation(path, rename_map=rename_map)
        validator = DatasetValidator()
        report = validator.validate(df)

        # Attach the validation report to the DataFrame for downstream inspection
        df._validation_report = report

        return df

    def _resolve_path(self, path: str | Path) -> Path:
        """
        Resolve a potentially relative path against the base path.

        Args:
            path: Raw path string or Path object.

        Returns:
            Absolute Path object.
        """
        path_obj = Path(path)
        if self._base_path and not path_obj.is_absolute():
            return (self._base_path / path_obj).resolve()
        return path_obj.resolve()

    def _validate_path(self, path: Path) -> None:
        """
        Validate that the path exists, points to a file, and has a supported extension.

        Args:
            path: Resolved Path to validate.

        Raises:
            FileNotFoundError: If the path does not exist.
            DatasetLoadError: If the path is not a file or extension is unsupported.

        TODO:
            - Add file size sanity check (warn on unexpectedly large/small files).
            - Add magic-byte based format detection rather than relying solely on extensions.
        """
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")

        if not path.is_file():
            raise DatasetLoadError(f"Path is not a file: {path}")

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise DatasetLoadError(
                f"Unsupported file format: '{path.suffix}'. "
                f"Supported formats: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}"
            )

    def _read_file(self, path: Path, extension: str) -> pd.DataFrame:
        """
        Read the file into a DataFrame based on its extension.

        Args:
            path: Absolute Path to the file.
            extension: Lowercase file extension (e.g. '.csv').

        Returns:
            pd.DataFrame with file contents.

        Raises:
            DatasetLoadError: If pandas fails to parse the file.

        TODO:
            - Add dtype inference optimisation for large CSVs.
            - Add low_memory=False for consistent CSV parsing.
            - Add error handling for malformed files (line skipping).
        """
        try:
            if extension == ".csv":
                return pd.read_csv(path, low_memory=False)
            elif extension in {".parquet", ".parq"}:
                return pd.read_parquet(path)
        except Exception as exc:
            raise DatasetLoadError(f"Failed to read dataset at '{path}': {exc}") from exc

        # Unreachable in practice; satisfies type checker.
        raise DatasetLoadError(f"Unexpected error reading: {path}")

    def list_available(self, directory: str | Path | None = None) -> list[Path]:
        """
        List all supported dataset files in a directory (non-recursive).

        Args:
            directory: Directory to scan. Defaults to base_path if configured.

        Returns:
            Sorted list of Path objects for supported dataset files.

        TODO:
            - Add recursive scanning option.
            - Add file size and row-count metadata.
        """
        scan_path = Path(directory) if directory else self._base_path
        if not scan_path or not scan_path.is_dir():
            return []

        return sorted(
            [
                f
                for f in scan_path.iterdir()
                if f.is_file() and f.suffix.lower() in self.SUPPORTED_EXTENSIONS
            ]
        )
