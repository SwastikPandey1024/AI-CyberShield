"""
Dataset Validator

Responsible for validating the structural and content integrity of loaded datasets.

This module handles:
- Column existence and naming convention checks
- Missing value detection and reporting
- Duplicate row detection
- Schema validation (expected columns, data types)
- Target column existence and cardinality validation

All validators return structured reports rather than raising exceptions,
allowing callers to decide how to handle violations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np
import pandas as pd


# ──────────────────────────────────────────────
# Validation Report Types
# ──────────────────────────────────────────────


@dataclass
class ColumnValidationReport:
    """Report for a single column validation."""

    column: str
    exists: bool
    expected_dtype: Optional[str] = None
    actual_dtype: Optional[str] = None
    dtype_match: Optional[bool] = None
    missing_count: int = 0
    missing_ratio: float = 0.0
    unique_count: int = 0
    issues: list[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    """Aggregate validation report for a full DataFrame."""

    is_valid: bool = True
    row_count: int = 0
    column_count: int = 0
    duplicate_row_count: int = 0
    total_missing_cells: int = 0
    total_missing_ratio: float = 0.0
    column_reports: list[ColumnValidationReport] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# ──────────────────────────────────────────────
# Validator
# ──────────────────────────────────────────────


class DatasetValidator:
    """
    Validates the structure and content of cybersecurity datasets.

    Performs checks on columns, missing values, duplicates, schema conformance,
    and data types. Designed to be used immediately after DatasetLoader.load()
    to catch data quality issues early.

    Usage:
        validator = DatasetValidator()
        report = validator.validate(df, expected_columns=["Flow Duration", "Label"])

    TODO:
        - Add value range checks (e.g. ports 0-65535, timestamps in expected range).
        - Add distribution shift detection vs reference dataset.
        - Add categorical value frequency checks (e.g. minimum class representation).
        - Add correlation-based redundancy detection.
    """

    def __init__(self, target_column: str = "Label") -> None:
        """
        Initialise the validator.

        Args:
            target_column: Name of the target/label column for classification tasks.
                           Defaults to "Label" which is standard for CICIDS datasets.
        """
        self._target_column = target_column

    def validate(
        self,
        df: pd.DataFrame,
        expected_columns: Optional[list[str]] = None,
        schema: Optional[dict[str, str]] = None,
        use_catalogue: bool = False,
    ) -> ValidationReport:
        """
        Run all validation checks against the DataFrame.

        When ``use_catalogue=True``, the validator builds ``expected_columns``
        and ``schema`` from the config-driven feature catalogue automatically,
        ensuring validation is always consistent with the data dictionary.

        Args:
            df: The DataFrame to validate.
            expected_columns: Optional list of column names that must exist.
            schema: Optional dict mapping column names to expected pandas dtypes
                    (e.g. {"Flow Duration": "int64", "Label": "object"}).
            use_catalogue: If True, populate expected_columns and schema from
                           the feature catalogue (ignores explicitly passed args).

        Returns:
            ValidationReport containing all findings.

        TODO:
            - Add parallel validation for large DataFrames.
            - Add option to fail fast on first critical error.
        """
        report = ValidationReport(
            row_count=len(df),
            column_count=len(df.columns),
        )

        # ── Config-driven catalogue integration ──
        if use_catalogue:
            from ml.preprocessing.data_dictionary import CICIDS2017_FEATURES

            expected_columns = [
                f.canonical_name for f in CICIDS2017_FEATURES if not f.is_target
            ]
            schema = {
                f.canonical_name: f.dtype
                for f in CICIDS2017_FEATURES
                if not f.is_target
            }

        self._check_duplicates(df, report)

        if expected_columns is not None:
            self._check_expected_columns(df, expected_columns, report)

        if schema is not None:
            self._check_schema(df, schema, report)
        else:
            # Run column-level validation even without explicit schema
            self._check_columns_generic(df, report)

        # Must run after column_reports has been populated above, since this
        # attaches per-column missing-value stats to existing entries.
        self._check_missing_values(df, report)

        self._check_target_column(df, report)

        report.is_valid = len(report.errors) == 0
        return report

    def _check_duplicates(self, df: pd.DataFrame, report: ValidationReport) -> None:
        """
        Count and report duplicate rows.

        Args:
            df: DataFrame to check.
            report: Mutable report to update.
        """
        dup_count = df.duplicated().sum()
        report.duplicate_row_count = dup_count
        if dup_count > 0:
            dup_ratio = dup_count / len(df)
            report.warnings.append(
                f"Found {dup_count} duplicate rows ({dup_ratio:.2%} of data). "
                "Consider whether duplicates are expected for this dataset."
            )

    def _check_missing_values(self, df: pd.DataFrame, report: ValidationReport) -> None:
        """
        Calculate missing value statistics across the entire DataFrame.

        Args:
            df: DataFrame to check.
            report: Mutable report to update.
        """
        total_cells = df.size
        missing_cells = df.isna().sum().sum()
        report.total_missing_cells = int(missing_cells)
        report.total_missing_ratio = float(missing_cells / total_cells) if total_cells > 0 else 0.0

        # Per-column missing values
        missing_per_column = df.isna().sum()
        columns_with_missing = missing_per_column[missing_per_column > 0]
        for col, count in columns_with_missing.items():
            col_idx = next(
                (i for i, cr in enumerate(report.column_reports) if cr.column == col),
                None,
            )
            if col_idx is not None:
                report.column_reports[col_idx].missing_count = int(count)
                report.column_reports[col_idx].missing_ratio = float(count / len(df))

    def _check_expected_columns(
        self,
        df: pd.DataFrame,
        expected_columns: list[str],
        report: ValidationReport,
    ) -> None:
        """
        Verify that all expected columns exist in the DataFrame.

        Args:
            df: DataFrame to check.
            expected_columns: List of column names that must be present.
            report: Mutable report to update.

        TODO:
            - Check for unexpected columns and warn.
            - Check column ordering if order-sensitive.
        """
        existing_columns = set(df.columns)
        for col in expected_columns:
            if col not in existing_columns:
                report.errors.append(f"Expected column '{col}' is missing from the dataset.")
                report.column_reports.append(
                    ColumnValidationReport(
                        column=col,
                        exists=False,
                        issues=[f"Column '{col}' is missing."],
                    )
                )

    def _check_schema(
        self,
        df: pd.DataFrame,
        schema: dict[str, str],
        report: ValidationReport,
    ) -> None:
        """
        Validate DataFrame columns against an expected schema of name → dtype mappings.

        Args:
            df: DataFrame to check.
            schema: Dict mapping column name to expected pandas dtype string
                    (e.g. {"Flow Duration": "int64", "Label": "object"}).
            report: Mutable report to update.

        TODO:
            - Add nullable dtype awareness (e.g. Int64 vs int64).
            - Add categorical dtype validation with expected categories.
        """
        for col_name, expected_dtype in schema.items():
            if col_name not in df.columns:
                report.errors.append(f"Schema column '{col_name}' not found in DataFrame.")
                continue

            actual_dtype = str(df[col_name].dtype)
            dtype_matches = actual_dtype == expected_dtype
            if not dtype_matches:
                report.warnings.append(
                    f"Column '{col_name}': expected dtype '{expected_dtype}', "
                    f"got '{actual_dtype}'. Automatic coercion may be needed."
                )

            report.column_reports.append(
                ColumnValidationReport(
                    column=col_name,
                    exists=True,
                    expected_dtype=expected_dtype,
                    actual_dtype=actual_dtype,
                    dtype_match=dtype_matches,
                    unique_count=int(df[col_name].nunique()),
                )
            )

    def _check_columns_generic(self, df: pd.DataFrame, report: ValidationReport) -> None:
        """
        Run generic checks on all columns when no explicit schema is provided.

        Args:
            df: DataFrame to check.
            report: Mutable report to update.

        TODO:
            - Detect constant columns (zero variance) and warn.
            - Detect high-cardinality categorical columns that may cause issues.
            - Flag columns with single unique value (potential ID columns).
        """
        for col in df.columns:
            dtype = str(df[col].dtype)
            unique_count = int(df[col].nunique())
            col_report = ColumnValidationReport(
                column=col,
                exists=True,
                actual_dtype=dtype,
                unique_count=unique_count,
            )

            # Check for infinity values in numeric columns
            if pd.api.types.is_numeric_dtype(df[col]):
                inf_count = int(df[col].isin([np.inf, -np.inf]).sum())
                if inf_count > 0:
                    col_report.issues.append(f"Contains {inf_count} infinity values.")
                    report.warnings.append(
                        f"Column '{col}' contains {inf_count} infinity values that may need handling."
                    )

            report.column_reports.append(col_report)

    def _check_target_column(self, df: pd.DataFrame, report: ValidationReport) -> None:
        """
        Validate the target/label column if it exists.

        Since the loader now guarantees canonical (whitespace-cleaned) column names,
        this method does a direct, exact lookup — no fuzzy matching needed.

        Checks for existence, missing values, and class distribution.

        Args:
            df: DataFrame to check.
            report: Mutable report to update.

        TODO:
            - Add class imbalance severity classification.
            - Add minimum samples-per-class check.
            - Validate target is a known attack category.
        """
        if self._target_column not in df.columns:
            report.warnings.append(
                f"Target column '{self._target_column}' not found. "
                "Skipping target-specific validation."
            )
            return

        target = df[self._target_column]
        missing_targets = target.isna().sum()
        if missing_targets > 0:
            report.errors.append(
                f"Target column '{self._target_column}' has {missing_targets} missing values."
            )

        class_counts = target.value_counts()
        report.warnings.append(
            f"Target column '{self._target_column}' has {len(class_counts)} classes: "
            f"{class_counts.to_dict()}"
        )
